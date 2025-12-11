"""
Flask web application for London Food Finds directory.
Dynamic routing for restaurants, cuisines, and neighbourhoods.
"""

from flask import Flask, render_template, request, url_for
import pandas as pd
import math
import re
import unicodedata
from collections import Counter
from typing import Dict, List, Optional
import os

app = Flask(__name__)
app.config['DEBUG'] = True

# Add slugify filter to Jinja2
@app.template_filter('slugify')
def slugify_filter(text):
    return slugify(str(text))

# Configuration
DATA_PATH = "OS-20251124200014m1e_restaurant.xlsx"
RESTAURANTS_PER_PAGE = 12
MIN_CITY_ROWS = 5

KNOWN_AREAS = {
    "Barking", "Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden", "Croydon",
    "Ealing", "Enfield", "Greenwich", "Hackney", "Hammersmith", "Hammersmith And Fulham",
    "Fulham", "Haringey", "Harrow", "Havering", "Hillingdon", "Hounslow", "Islington",
    "Kensington", "Chelsea", "Kensington And Chelsea", "Kingston Upon Thames", "Lambeth",
    "Lewisham", "Merton", "Newham", "Redbridge", "Richmond Upon Thames", "Southwark",
    "Sutton", "Tower Hamlets", "Waltham Forest", "Wandsworth", "Westminster", "City Of London",
    "London", "Surbiton", "Twickenham", "Richmond", "Ilford", "Uxbridge", "Wembley",
    "Southall", "Hayes", "Feltham", "Pinner", "Sidcup", "Morden", "Ruislip", "Northwood",
    "New Malden", "Teddington", "Brentford", "Greenford", "Stanmore", "Mitcham",
    "Bexleyheath", "Isleworth", "Dartford", "Banstead", "Barking And Dagenham",
}

PLACEHOLDER_IMAGE = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=60"

# Global data storage
df = None
cuisine_counts = {}
neighbourhood_counts = {}


def slugify(value: str) -> str:
    """Create URL-friendly slugs."""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "listing"


def normalize_city(value) -> Optional[str]:
    """Return a cleaned city name or None if unusable."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if not re.search(r"[a-zA-Z]", text):
        return None
    if any(char.isdigit() for char in text):
        return None
    if len(text) < 3:
        return None
    text = re.sub(r"\s+", " ", text)
    lower_words = {word.strip("'-").lower() for word in text.split()}
    address_terms = {
        "road", "rd", "street", "st", "lane", "ln", "square", "sq", "close", "cl",
        "way", "wharf", "mall", "walk", "hill", "park", "avenue", "ave", "place", "pl",
        "circus", "crescent", "cres", "drive", "dr", "market", "row", "arcade", "court",
        "ct", "quay", "stairs", "terrace", "green", "gardens", "parade", "carriageway",
    }
    if lower_words & address_terms:
        return None
    return text.title()


def parse_categories(raw) -> List[str]:
    """Extract restaurant-focused categories."""
    if pd.isna(raw):
        return []
    categories = []
    for chunk in str(raw).split(","):
        label = chunk.strip()
        if not label:
            continue
        if "restaurant" in label.lower():
            categories.append(label.title())
    return categories


def load_data():
    """Load and process the Excel file into a cleaned DataFrame."""
    global df, cuisine_counts, neighbourhood_counts
    
    print("Loading Excel file...")
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df = df[df["query"].str.contains("Greater London", na=False)].copy()
    
    print("Processing cities...")
    city_primary = df["city"].apply(normalize_city)
    borough_primary = df["borough"].apply(normalize_city)
    valid_cities = set(city_primary.dropna()) | set(KNOWN_AREAS)
    
    def pick_city(row):
        if isinstance(row.get("city_primary"), str):
            return row["city_primary"]
        borough_name = row.get("borough_primary")
        if isinstance(borough_name, str) and borough_name in valid_cities:
            return borough_name
        address = row.get("full_address")
        if isinstance(address, str):
            parts = [part.strip() for part in address.split(",")]
            for part in reversed(parts):
                name = normalize_city(part)
                if name and name in valid_cities:
                    return name
        return "London"
    
    df["city_primary"] = city_primary
    df["borough_primary"] = borough_primary
    df["city_clean"] = df.apply(pick_city, axis=1)
    
    # Filter cities with minimum restaurants
    city_counts = df.groupby("city_clean")["city_clean"].transform("count")
    df = df[city_counts >= MIN_CITY_ROWS].copy()
    
    # Clean and calculate fields
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0).astype(int)
    df["score"] = df["rating"].fillna(0) + (df["reviews"] / 1000)
    df["categories"] = df["subtypes"].apply(parse_categories)
    
    # Add Julan's Pick flag
    df["julans_pick"] = (df["rating"] >= 4.5) & (df["reviews"] >= 500)
    
    # Calculate cuisine counts (from London only)
    london_df = df[df["city_clean"] == "London"].copy()
    exploded = df.explode("categories")
    london_exploded = exploded[exploded["city_clean"] == "London"]
    cuisine_counts = london_exploded[london_exploded["categories"].notna()].groupby("categories").size().to_dict()
    
    # Calculate neighbourhood counts
    neighbourhood_counts = df.groupby("city_clean").size().to_dict()
    
    print(f"Loaded {len(df)} restaurants")
    print(f"Found {len(cuisine_counts)} cuisines")
    print(f"Found {len(neighbourhood_counts)} neighbourhoods")


def get_restaurant_data(row) -> Dict:
    """Convert DataFrame row to restaurant dictionary."""
    website = row.get("site")
    if not isinstance(website, str) or not website.strip() or str(website).strip().lower() == "nan":
        backup = row.get("location_link")
        website = backup if isinstance(backup, str) and backup.strip() else "#"
    
    photo = row.get("photo")
    if not isinstance(photo, str) or not photo.strip() or str(photo).strip().lower() == "nan":
        photo = PLACEHOLDER_IMAGE
    
    rating = float(row.get("rating", 0)) if pd.notna(row.get("rating")) else 0.0
    reviews = int(row.get("reviews", 0))
    
    return {
        "name": str(row.get("name", "Restaurant")),
        "rating": rating,
        "reviews": reviews,
        "address": str(row.get("full_address") or row.get("street") or row.get("city") or ""),
        "phone": str(row.get("phone") or row.get("phone_1") or ""),
        "website": website,
        "image": photo,
        "julans_pick": bool(row.get("julans_pick", False)),
        "neighbourhood": str(row.get("city_clean", "London")),
    }


def get_nearby_neighbourhoods(exclude_neighbourhood: str = "London", limit: int = 3) -> List[Dict]:
    """Get nearby neighbourhoods for sidebar."""
    nearby = []
    for city, count in sorted(neighbourhood_counts.items(), key=lambda x: x[1], reverse=True):
        if city != exclude_neighbourhood and len(nearby) < limit:
            nearby.append({
                "name": city,
                "slug": slugify(city),
                "count": count
            })
    return nearby


@app.route('/')
def index():
    """Homepage with all London restaurants."""
    if df is None or df.empty:
        return "Error: Data not loaded. Please check server logs.", 500
    
    page = request.args.get('page', 1, type=int)
    
    # Filter to London only
    london_df = df[df["city_clean"] == "London"].copy()
    london_df = london_df.sort_values(["score", "reviews"], ascending=False)
    
    total = len(london_df)
    total_pages = math.ceil(total / RESTAURANTS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * RESTAURANTS_PER_PAGE
    end_idx = start_idx + RESTAURANTS_PER_PAGE
    page_df = london_df.iloc[start_idx:end_idx]
    
    restaurants = [get_restaurant_data(row) for _, row in page_df.iterrows()]
    
    # Top cuisines for pills
    top_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    # Nearby neighbourhoods
    nearby = get_nearby_neighbourhoods()
    
    return render_template('index.html',
                         restaurants=restaurants,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         title=f"Top {total} Best Restaurants in London",
                         top_cuisines=top_cuisines,
                         nearby_neighbourhoods=nearby,
                         filter_type=None)


@app.route('/neighbourhood/<name>')
def neighbourhood(name):
    """Filter restaurants by neighbourhood."""
    page = request.args.get('page', 1, type=int)
    
    # Find matching neighbourhood (try slug match or name match)
    matching_neighbourhood = None
    for city in neighbourhood_counts.keys():
        if slugify(city) == name or city.lower() == name.lower():
            matching_neighbourhood = city
            break
    
    if not matching_neighbourhood:
        return "Neighbourhood not found", 404
    
    neighbourhood_df = df[df["city_clean"] == matching_neighbourhood].copy()
    neighbourhood_df = neighbourhood_df.sort_values(["score", "reviews"], ascending=False)
    
    total = len(neighbourhood_df)
    total_pages = math.ceil(total / RESTAURANTS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * RESTAURANTS_PER_PAGE
    end_idx = start_idx + RESTAURANTS_PER_PAGE
    page_df = neighbourhood_df.iloc[start_idx:end_idx]
    
    restaurants = [get_restaurant_data(row) for _, row in page_df.iterrows()]
    
    # Get cuisine categories for this neighbourhood
    exploded = df.explode("categories")
    neighbourhood_exploded = exploded[exploded["city_clean"] == matching_neighbourhood]
    neighbourhood_categories = neighbourhood_exploded[neighbourhood_exploded["categories"].notna()].groupby("categories").size().to_dict()
    filtered_categories = {cat: count for cat, count in neighbourhood_categories.items() if count >= 3}
    
    # Nearby neighbourhoods
    nearby = get_nearby_neighbourhoods(exclude_neighbourhood=matching_neighbourhood)
    
    # Top cuisines for pills
    top_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    return render_template('index.html',
                         restaurants=restaurants,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         title=f"Best Restaurants in {matching_neighbourhood}",
                         top_cuisines=top_cuisines,
                         nearby_neighbourhoods=nearby,
                         filter_type="neighbourhood",
                         filter_name=matching_neighbourhood,
                         filter_categories=filtered_categories)


@app.route('/cuisine/<name>')
def cuisine(name):
    """Filter restaurants by cuisine."""
    page = request.args.get('page', 1, type=int)
    
    # Find matching cuisine (try slug match or name match)
    matching_cuisine = None
    for cuisine_name in cuisine_counts.keys():
        if slugify(cuisine_name) == name or cuisine_name.lower() == name.lower():
            matching_cuisine = cuisine_name
            break
    
    if not matching_cuisine:
        return "Cuisine not found", 404
    
    # Filter to London only, with this cuisine
    london_df = df[df["city_clean"] == "London"].copy()
    exploded = df.explode("categories")
    cuisine_df = exploded[(exploded["city_clean"] == "London") & (exploded["categories"] == matching_cuisine)].copy()
    cuisine_df = cuisine_df.sort_values(["score", "reviews"], ascending=False)
    
    total = len(cuisine_df)
    total_pages = math.ceil(total / RESTAURANTS_PER_PAGE)
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * RESTAURANTS_PER_PAGE
    end_idx = start_idx + RESTAURANTS_PER_PAGE
    page_df = cuisine_df.iloc[start_idx:end_idx]
    
    restaurants = [get_restaurant_data(row) for _, row in page_df.iterrows()]
    
    # Nearby neighbourhoods
    nearby = get_nearby_neighbourhoods()
    
    # Top cuisines for pills
    top_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:8]
    
    return render_template('index.html',
                         restaurants=restaurants,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         title=f"Best {matching_cuisine} in London",
                         top_cuisines=top_cuisines,
                         nearby_neighbourhoods=nearby,
                         filter_type="cuisine",
                         filter_name=matching_cuisine)


@app.route('/neighbourhoods')
def neighbourhoods():
    """All neighbourhoods page."""
    neighbourhoods_list = []
    for city, count in sorted(neighbourhood_counts.items(), key=lambda x: x[1], reverse=True):
        neighbourhoods_list.append({
            "name": city,
            "slug": slugify(city),
            "count": count
        })
    
    return render_template('categories.html',
                         items=neighbourhoods_list,
                         title="All London Neighbourhoods",
                         item_type="neighbourhood",
                         base_url="/neighbourhood")


@app.route('/cuisines')
def cuisines():
    """All cuisines page."""
    cuisines_list = []
    for cuisine_name, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True):
        cuisines_list.append({
            "name": cuisine_name,
            "slug": slugify(cuisine_name),
            "count": count
        })
    
    return render_template('categories.html',
                         items=cuisines_list,
                         title="All Cuisines in London",
                         item_type="cuisine",
                         base_url="/cuisine")


@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')


def initialize_data():
    """Initialize data from Excel or JSON file."""
    global df, cuisine_counts, neighbourhood_counts

    if os.path.exists(DATA_PATH):
        try:
            print(f"Loading data from {DATA_PATH}...")
            load_data()
            print("Data loaded successfully from Excel")
            return True
        except Exception as e:
            print(f"Error loading data from Excel: {e}")
            import traceback
            traceback.print_exc()

    if os.path.exists("processed_data.json"):
        try:
            import json
            print("Loading data from processed_data.json...")
            with open("processed_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert JSON back to DataFrame structure
            restaurants = data.get("restaurants", [])
            if not restaurants:
                raise ValueError("processed_data.json has no restaurants")

            df = pd.DataFrame(restaurants)

            # Ensure required columns exist with defaults
            if "city_clean" not in df.columns:
                df["city_clean"] = df.get("city", "London")
            if "categories" not in df.columns:
                df["categories"] = df.get("subtypes", "").apply(lambda x: [x] if pd.notna(x) and x else [])

            # Recalculate necessary fields if missing
            if "rating" not in df.columns or df["rating"].isna().all():
                df["rating"] = pd.to_numeric(df.get("rating", 0), errors="coerce").fillna(0)
            else:
                df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)

            if "reviews" not in df.columns:
                df["reviews"] = 0
            df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0).astype(int)

            if "score" not in df.columns:
                df["score"] = df["rating"] + (df["reviews"] / 1000)
            else:
                df["score"] = pd.to_numeric(df["score"], errors="coerce").fillna(df["rating"] + (df["reviews"] / 1000))

            # Set julans_pick flag
            if "julans_pick" not in df.columns:
                df["julans_pick"] = (df["rating"] >= 4.5) & (df["reviews"] >= 500)

            # Load counts from JSON or recalculate
            cuisine_counts = data.get("cuisines", {})
            neighbourhood_counts = data.get("neighbourhoods", {})

            if not cuisine_counts or not neighbourhood_counts:
                # Recalculate if not in JSON
                from collections import Counter
                exploded = df.explode("categories")
                london_exploded = exploded[exploded["city_clean"] == "London"]
                cuisine_counts = london_exploded[london_exploded["categories"].notna()].groupby("categories").size().to_dict()
                neighbourhood_counts = df.groupby("city_clean").size().to_dict()

            print(f"Loaded {len(df)} restaurants from JSON")
            return True
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            import traceback
            traceback.print_exc()

    print(f"Warning: Neither {DATA_PATH} nor processed_data.json found")
    print("Data loading failed. Please ensure data file exists.")
    df = pd.DataFrame()


# Load data when module is imported (works for both direct run and Vercel)
initialize_data()

# Ensure df is not None before routes execute
if df is None or df.empty:
    print("WARNING: Data failed to load. App will show errors.")

if __name__ == '__main__':
    # Only run the Flask dev server when running directly
    app.run(debug=True, port=5000)

