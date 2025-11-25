import pandas as pd
import json
import re
from flask import Flask, render_template, jsonify, request, Response
from urllib.parse import unquote
import os
from datetime import datetime

app = Flask(__name__)

# Global variables to store processed data
restaurants_data = None
cuisines_dict = None
neighbourhoods_dict = None

def slugify(text):
    """Convert text to URL-friendly slug"""
    if pd.isna(text) or not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_cuisines(subtypes_str):
    """Extract cuisine types from subtypes string"""
    if pd.isna(subtypes_str):
        return ['Restaurant']
    
    subtypes_str = str(subtypes_str)
    parts = [p.strip() for p in subtypes_str.split(',')]
    
    cuisines = []
    skip_terms = {'restaurant', 'bar', 'cafe', 'café', 'food', 'dining', 'establishment', 'grill'}
    
    for part in parts:
        part_lower = part.lower()
        
        # Skip generic terms
        if part_lower in skip_terms:
            continue
        
        # Remove common suffixes
        cuisine = part
        cuisine = re.sub(r'\s+restaurant\s*$', '', cuisine, flags=re.IGNORECASE)
        cuisine = re.sub(r'\s+takeaway\s*$', '', cuisine, flags=re.IGNORECASE)
        cuisine = re.sub(r'\s+cafe\s*$', '', cuisine, flags=re.IGNORECASE)
        cuisine = re.sub(r'\s+café\s*$', '', cuisine, flags=re.IGNORECASE)
        cuisine = cuisine.strip()
        
        # Skip if it's just a generic term or too short
        if not cuisine or len(cuisine) < 3 or cuisine.lower() in skip_terms:
            continue
        
        # Capitalize properly
        if cuisine:
            # Handle multi-word cuisines
            words = cuisine.split()
            if len(words) > 1:
                cuisine = ' '.join([w.capitalize() for w in words])
            else:
                cuisine = cuisine.capitalize()
            
            cuisines.append(cuisine)
    
    # If no cuisines found, default to Restaurant
    if not cuisines:
        cuisines = ['Restaurant']
    
    # Return unique cuisines (preserving order)
    seen = set()
    result = []
    for c in cuisines:
        c_lower = c.lower()
        if c_lower not in seen:
            seen.add(c_lower)
            result.append(c)
    
    return result

def load_and_process_data():
    """Load and process restaurant data from Excel or JSON"""
    global restaurants_data, cuisines_dict, neighbourhoods_dict
    
    # Get the base directory (works for both local and Vercel)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'processed_data.json')
    excel_path = os.path.join(base_dir, 'OS-20251124200014m1e_restaurant.xlsx')
    
    # Try to load from JSON first (for Vercel/production)
    if os.path.exists(json_path):
        print("Loading from processed_data.json...")
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                restaurants_data = data.get('restaurants', [])
                cuisines_dict = data.get('cuisines', {})
                neighbourhoods_dict = data.get('neighbourhoods', {})
            print(f"Loaded {len(restaurants_data)} restaurants from JSON")
            print(f"Found {len(cuisines_dict)} unique cuisines")
            print(f"Found {len(neighbourhoods_dict)} neighbourhoods")
            return
        except Exception as e:
            print(f"Error loading JSON: {e}")
            # Continue to try Excel file
    
    # Fallback to Excel file (for local development)
    if os.path.exists(excel_path):
        print("Loading Excel file...")
    elif not os.path.exists(json_path):
        print("ERROR: Neither processed_data.json nor OS-20251124200014m1e_restaurant.xlsx found!")
        print(f"Looked in: {base_dir}")
        print("Please run: python convert_to_json.py to create processed_data.json")
        restaurants_data = []
        cuisines_dict = {}
        neighbourhoods_dict = {}
        return
    else:
        # JSON exists but failed to load, Excel doesn't exist
        print("ERROR: Failed to load processed_data.json and Excel file not found!")
        restaurants_data = []
        cuisines_dict = {}
        neighbourhoods_dict = {}
        return
    
    # Load Excel file
    df = pd.read_excel(excel_path)
    
    print(f"Loaded {len(df)} restaurants")
    
    # Filter for Greater London area (you can adjust this)
    # For now, we'll use all data
    
    # Process each restaurant
    restaurants = []
    cuisines_count = {}
    neighbourhoods_count = {}
    
    for idx, row in df.iterrows():
        # Extract cuisine from subtypes
        subtypes = row.get('subtypes', '')
        cuisines = extract_cuisines(subtypes)
        if not cuisines:
            cuisines = ['Restaurant']
        
        primary_cuisine = cuisines[0] if cuisines else 'Restaurant'
        
        # Get city (neighbourhood)
        city = str(row.get('city', 'London')).strip()
        if not city or city == 'nan':
            city = 'London'
        
        # Get rating and reviews
        rating = row.get('rating', 0)
        reviews = row.get('reviews', 0)
        
        # Convert to numeric, handling NaN
        try:
            rating = float(rating) if pd.notna(rating) else 0
            reviews = int(float(reviews)) if pd.notna(reviews) else 0
        except:
            rating = 0
            reviews = 0
        
        # Calculate score for sorting (rating * reviews weight)
        score = rating * (1 + reviews / 100)
        
        restaurant = {
            'id': idx,
            'name': str(row.get('name', 'Unknown')),
            'cuisines': cuisines,
            'primary_cuisine': primary_cuisine,
            'city': city,
            'rating': rating,
            'reviews': reviews,
            'score': score,
            'address': str(row.get('full_address', '')) or str(row.get('street', '')),
            'phone': str(row.get('phone', '')) or str(row.get('phone_1', '')),
            'website': str(row.get('site', '')) if pd.notna(row.get('site')) else '',
            'photo': str(row.get('photo', '')) if pd.notna(row.get('photo')) else '',
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'julans_pick': False  # We'll mark some manually or based on criteria
        }
        
        restaurants.append(restaurant)
        
        # Count cuisines
        for cuisine in cuisines:
            cuisine_slug = slugify(cuisine)
            if cuisine_slug:
                if cuisine_slug not in cuisines_count:
                    cuisines_count[cuisine_slug] = {'name': cuisine, 'count': 0}
                cuisines_count[cuisine_slug]['count'] += 1
        
        # Count neighbourhoods
        city_slug = slugify(city)
        if city_slug:
            if city_slug not in neighbourhoods_count:
                neighbourhoods_count[city_slug] = {'name': city, 'count': 0}
            neighbourhoods_count[city_slug]['count'] += 1
    
    # Mark top restaurants as "Julan's Pick" (top 5% by score)
    restaurants.sort(key=lambda x: x['score'], reverse=True)
    top_count = max(1, len(restaurants) // 20)  # Top 5%
    for i in range(min(top_count, 500)):  # Max 500 picks
        restaurants[i]['julans_pick'] = True
    
    restaurants_data = restaurants
    cuisines_dict = cuisines_count
    neighbourhoods_dict = neighbourhoods_count
    
    print(f"Processed {len(restaurants)} restaurants")
    print(f"Found {len(cuisines_dict)} unique cuisines")
    print(f"Found {len(neighbourhoods_dict)} neighbourhoods")

# Load data on startup (with error handling for Vercel)
try:
    load_and_process_data()
except Exception as e:
    print(f"Error loading data: {e}")
    import traceback
    traceback.print_exc()
    # Set empty defaults to prevent app from crashing
    if restaurants_data is None:
        restaurants_data = []
    if cuisines_dict is None:
        cuisines_dict = {}
    if neighbourhoods_dict is None:
        neighbourhoods_dict = {}

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    # Sort dictionaries by count for footer
    cuisines = cuisines_dict or {}
    neighbourhoods = neighbourhoods_dict or {}
    
    sorted_cuisines = []
    sorted_neighbourhoods = []
    
    if cuisines:
        sorted_cuisines = sorted(cuisines.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    if neighbourhoods:
        sorted_neighbourhoods = sorted(neighbourhoods.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    
    return {
        'cuisines_dict': cuisines,
        'neighbourhoods_dict': neighbourhoods,
        'footer_cuisines': sorted_cuisines,
        'footer_neighbourhoods': sorted_neighbourhoods
    }

def get_restaurants_for_cuisine(cuisine_slug, page=1, per_page=12):
    """Get restaurants filtered by cuisine"""
    cuisine_name = None
    for slug, data in cuisines_dict.items():
        if slug == cuisine_slug:
            cuisine_name = data['name']
            break
    
    if not cuisine_name:
        return [], 0
    
    # Find restaurants with this cuisine
    filtered = [r for r in restaurants_data if cuisine_name.lower() in [c.lower() for c in r['cuisines']]]
    
    # Sort by score
    filtered.sort(key=lambda x: x['score'], reverse=True)
    
    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    
    return filtered[start:end], total

def get_restaurants_for_neighbourhood(neighbourhood_slug, cuisine_slug=None, page=1, per_page=12):
    """Get restaurants filtered by neighbourhood and optionally cuisine"""
    neighbourhood_name = None
    for slug, data in neighbourhoods_dict.items():
        if slug == neighbourhood_slug:
            neighbourhood_name = data['name']
            break
    
    if not neighbourhood_name:
        return [], 0
    
    # Find restaurants in this neighbourhood
    filtered = [r for r in restaurants_data if slugify(r['city']) == neighbourhood_slug]
    
    # Filter by cuisine if provided
    if cuisine_slug:
        cuisine_name = None
        for slug, data in cuisines_dict.items():
            if slug == cuisine_slug:
                cuisine_name = data['name']
                break
        if cuisine_name:
            filtered = [r for r in filtered if cuisine_name.lower() in [c.lower() for c in r['cuisines']]]
    
    # Sort by score
    filtered.sort(key=lambda x: x['score'], reverse=True)
    
    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    
    return filtered[start:end], total

def get_all_restaurants(page=1, per_page=12):
    """Get all restaurants sorted by score"""
    filtered = restaurants_data.copy()
    filtered.sort(key=lambda x: x['score'], reverse=True)
    
    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    
    return filtered[start:end], total

@app.route('/')
def homepage():
    """Homepage route"""
    # Get top restaurants for homepage
    top_restaurants, total = get_all_restaurants(page=1, per_page=12)
    
    # Get top cuisines for filter pills
    top_cuisines = sorted(cuisines_dict.items(), key=lambda x: x[1]['count'], reverse=True)[:20]
    
    # Get top neighbourhoods
    top_neighbourhoods = sorted(neighbourhoods_dict.items(), key=lambda x: x[1]['count'], reverse=True)[:12]
    
    return render_template('index.html',
                         restaurants=top_restaurants,
                         total_restaurants=len(restaurants_data),
                         cuisines=top_cuisines,
                         neighbourhoods=top_neighbourhoods,
                         current_page=1,
                         total_pages=(len(restaurants_data) + 11) // 12)

@app.route('/page/<int:page>')
def homepage_paginated(page):
    """Paginated homepage"""
    restaurants, total = get_all_restaurants(page=page, per_page=12)
    
    top_cuisines = sorted(cuisines_dict.items(), key=lambda x: x[1]['count'], reverse=True)[:20]
    top_neighbourhoods = sorted(neighbourhoods_dict.items(), key=lambda x: x[1]['count'], reverse=True)[:12]
    
    return render_template('index.html',
                         restaurants=restaurants,
                         total_restaurants=total,
                         cuisines=top_cuisines,
                         neighbourhoods=top_neighbourhoods,
                         current_page=page,
                         total_pages=(total + 11) // 12)

@app.route('/cuisine/<slug>')
@app.route('/cuisine/<slug>/page/<int:page>')
def cuisine_page(slug, page=1):
    """Cuisine page route"""
    restaurants, total = get_restaurants_for_cuisine(slug, page=page, per_page=12)
    
    # Get cuisine name
    cuisine_name = 'Restaurant'
    for s, data in cuisines_dict.items():
        if s == slug:
            cuisine_name = data['name']
            break
    
    # Get all cuisines for filter
    all_cuisines = sorted(cuisines_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    
    return render_template('cuisine.html',
                         cuisine_name=cuisine_name,
                         cuisine_slug=slug,
                         restaurants=restaurants,
                         total_restaurants=total,
                         all_cuisines=all_cuisines,
                         current_page=page,
                         total_pages=(total + 11) // 12)

@app.route('/neighbourhood/<slug>')
@app.route('/neighbourhood/<slug>/page/<int:page>')
@app.route('/neighbourhood/<slug>/cuisine/<cuisine_slug>')
@app.route('/neighbourhood/<slug>/cuisine/<cuisine_slug>/page/<int:page>')
def neighbourhood_page(slug, page=1, cuisine_slug=None):
    """Neighbourhood page route"""
    restaurants, total = get_restaurants_for_neighbourhood(slug, cuisine_slug=cuisine_slug, page=page, per_page=12)
    
    # Get neighbourhood name
    neighbourhood_name = 'London'
    for s, data in neighbourhoods_dict.items():
        if s == slug:
            neighbourhood_name = data['name']
            break
    
    # Get top cuisines for this neighbourhood
    cuisine_counts = {}
    for r in restaurants_data:
        if slugify(r['city']) == slug:
            for cuisine in r['cuisines']:
                cuisine_slug_local = slugify(cuisine)
                if cuisine_slug_local:
                    if cuisine_slug_local not in cuisine_counts:
                        cuisine_counts[cuisine_slug_local] = {'name': cuisine, 'count': 0}
                    cuisine_counts[cuisine_slug_local]['count'] += 1
    
    top_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:20]
    
    # Get all cuisines
    all_cuisines = sorted(cuisines_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # Get active cuisine name if filtering
    active_cuisine_name = None
    if cuisine_slug:
        for s, data in cuisines_dict.items():
            if s == cuisine_slug:
                active_cuisine_name = data['name']
                break
    
    return render_template('neighbourhood.html',
                         neighbourhood_name=neighbourhood_name,
                         neighbourhood_slug=slug,
                         restaurants=restaurants,
                         total_restaurants=total,
                         cuisines=top_cuisines,
                         all_cuisines=all_cuisines,
                         active_cuisine_slug=cuisine_slug,
                         active_cuisine_name=active_cuisine_name,
                         current_page=page,
                         total_pages=(total + 11) // 12)

@app.route('/neighbourhoods')
def all_neighbourhoods():
    """All neighbourhoods page"""
    all_neighbourhoods_list = sorted(neighbourhoods_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    return render_template('neighbourhoods.html', neighbourhoods=all_neighbourhoods_list)

@app.route('/cuisines')
def all_cuisines():
    """All cuisines page"""
    all_cuisines_list = sorted(cuisines_dict.items(), key=lambda x: x[1]['count'], reverse=True)
    return render_template('cuisines.html', cuisines=all_cuisines_list)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml dynamically"""
    base_url = 'https://www.londonfoodfindsuk.co.uk'
    urls = []
    
    # Static pages
    urls.append({
        'loc': f'{base_url}/',
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    urls.append({
        'loc': f'{base_url}/about',
        'changefreq': 'monthly',
        'priority': '0.7'
    })
    
    urls.append({
        'loc': f'{base_url}/cuisines',
        'changefreq': 'weekly',
        'priority': '0.8'
    })
    
    urls.append({
        'loc': f'{base_url}/neighbourhoods',
        'changefreq': 'weekly',
        'priority': '0.8'
    })
    
    # All neighbourhood pages
    if neighbourhoods_dict:
        for slug, data in sorted(neighbourhoods_dict.items()):
            urls.append({
                'loc': f'{base_url}/neighbourhood/{slug}',
                'changefreq': 'weekly',
                'priority': '0.8'
            })
    
    # All cuisine pages
    if cuisines_dict:
        for slug, data in sorted(cuisines_dict.items()):
            urls.append({
                'loc': f'{base_url}/cuisine/{slug}',
                'changefreq': 'weekly',
                'priority': '0.8'
            })
    
    # Neighbourhood + cuisine combination pages
    if neighbourhoods_dict and cuisines_dict:
        for n_slug, n_data in sorted(neighbourhoods_dict.items()):
            # Get cuisines available in this neighbourhood
            neighbourhood_cuisines = {}
            for restaurant in restaurants_data:
                if slugify(restaurant['city']) == n_slug:
                    for cuisine in restaurant['cuisines']:
                        cuisine_slug = slugify(cuisine)
                        if cuisine_slug and cuisine_slug in cuisines_dict:
                            if cuisine_slug not in neighbourhood_cuisines:
                                neighbourhood_cuisines[cuisine_slug] = True
            
            # Add URLs for each cuisine in this neighbourhood
            for c_slug in sorted(neighbourhood_cuisines.keys()):
                urls.append({
                    'loc': f'{base_url}/neighbourhood/{n_slug}/cuisine/{c_slug}',
                    'changefreq': 'weekly',
                    'priority': '0.7'
                })
    
    # Generate XML
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url_data in urls:
        xml += '    <url>\n'
        xml += f'        <loc>{url_data["loc"]}</loc>\n'
        xml += f'        <changefreq>{url_data["changefreq"]}</changefreq>\n'
        xml += f'        <priority>{url_data["priority"]}</priority>\n'
        xml += '    </url>\n'
    
    xml += '</urlset>'
    
    return Response(xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

