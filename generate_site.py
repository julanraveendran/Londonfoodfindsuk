"""
Static directory site generator for Greater London restaurants.
Reads Excel file and generates pure HTML/CSS static site with no JavaScript.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd


# Configuration
DATA_PATH = Path("OS-20251124200014m1e_restaurant.xlsx")
OUTPUT_DIR = Path("site")
CSS_DIR = OUTPUT_DIR / "css"
IMAGES_DIR = OUTPUT_DIR / "images"
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


def slugify(value: str) -> str:
    """Create URL-friendly slugs such as `korean-restaurant`."""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "listing"


def normalize_city(value: str | float | None) -> str | None:
    """Return a cleaned city name or None if unusable."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
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


def parse_categories(raw: str) -> List[str]:
    """Extract restaurant-focused categories."""
    if pd.isna(raw):
        return []
    categories: List[str] = []
    for chunk in str(raw).split(","):
        label = chunk.strip()
        if not label:
            continue
        if "restaurant" in label.lower():
            categories.append(label.title())
    return categories


def format_link(row: Dict) -> str:
    """Extract website link from row data."""
    website = row.get("site")
    if not isinstance(website, str) or not website.strip() or website.strip().lower() == "nan":
        backup = row.get("location_link")
        website = backup if isinstance(backup, str) and backup.strip() else "#"
    return website


def get_image_url(row: Dict) -> str:
    """Get image URL or placeholder."""
    photo = row.get("photo")
    if isinstance(photo, str) and photo.strip() and photo.strip().lower() != "nan":
        return photo
    return PLACEHOLDER_IMAGE


def should_show_badge(row: Dict) -> bool:
    """Determine if restaurant should show 'Julan's Pick' badge."""
    rating = row.get("rating")
    reviews = int(row.get("reviews", 0))
    # Show badge for restaurants with high rating (4.5+) and good review count (500+)
    if pd.notna(rating) and rating >= 4.5 and reviews >= 500:
        return True
    return False


def build_restaurant_card(row: Dict) -> str:
    """Build a single restaurant card with schema markup."""
    website = format_link(row)
    name = row.get("name", "Restaurant")
    rating = row.get("rating", 0)
    reviews = int(row.get("reviews", 0))
    address = row.get("full_address") or row.get("street") or row.get("city") or ""
    phone = row.get("phone") or row.get("phone_1") or ""
    photo = get_image_url(row)
    
    rating_num = float(rating) if pd.notna(rating) else 0.0
    stars_count = int(rating_num)
    stars_display = "★" * stars_count if stars_count > 0 else ""
    
    badge_html = '<p class="badge">Julan\'s Pick</p>' if should_show_badge(row) else ''
    
    # Schema.org Restaurant markup
    schema = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": name,
        "image": photo,
        "address": {"@type": "PostalAddress", "streetAddress": address},
        "telephone": phone if phone else None,
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": rating_num,
            "reviewCount": reviews
        } if rating_num > 0 and reviews > 0 else None
    }
    schema_str = json.dumps({k: v for k, v in schema.items() if v is not None}, ensure_ascii=False)
    
    return f"""
            <article class="feature-card" itemscope itemtype="https://schema.org/Restaurant">
                <script type="application/ld+json">{schema_str}</script>
                <div class="card-media" style="background-image:url('{photo}')"></div>
                <div class="card-body">
                    {badge_html}
                    <h3 itemprop="name">{name}</h3>
                    <p class="meta">
                        <span itemprop="aggregateRating" itemscope itemtype="https://schema.org/AggregateRating">
                            <span itemprop="ratingValue" content="{rating_num}">{stars_display}</span>
                            (<span itemprop="reviewCount">{reviews:,}</span>)
                        </span>
                    </p>
                    <p class="meta" itemprop="address" itemscope itemtype="https://schema.org/PostalAddress">
                        <span itemprop="streetAddress">{address}</span>
                    </p>
                    <p class="meta" itemprop="telephone">{phone}</p>
                    <a class="btn" href="{website}" target="_blank" rel="noopener" itemprop="url">Visit Website</a>
                </div>
            </article>
        """


def build_restaurant_cards(rows: Iterable[Dict]) -> str:
    """Build multiple restaurant cards."""
    return "\n".join(build_restaurant_card(row) for row in rows)


def build_pagination(current_page: int, total_pages: int, base_url: str) -> str:
    """Generate pagination HTML with proper links."""
    if total_pages <= 1:
        return ""
    
    def get_page_url(page: int) -> str:
        if page == 1:
            return f"{base_url}/"
        return f"{base_url}/page{page}.html"
    
    pages = []
    start = max(1, current_page - 2)
    end = min(total_pages, start + 4)
    if end - start < 4:
        start = max(1, end - 4)
    
    for p in range(start, end + 1):
        if p == current_page:
            pages.append(f'<span class="page-num active">{p}</span>')
        else:
            pages.append(f'<a href="{get_page_url(p)}" class="page-num">{p}</a>')
    
    prev_link = f'<a href="{get_page_url(current_page - 1)}" class="page-nav">« Previous</a>' if current_page > 1 else '<span class="page-nav disabled">« Previous</span>'
    next_link = f'<a href="{get_page_url(current_page + 1)}" class="page-nav">Next »</a>' if current_page < total_pages else '<span class="page-nav disabled">Next »</span>'
    
    return f'<div class="pagination">{prev_link} {" ".join(pages)} {next_link}</div>'


def build_header() -> str:
    """Build consistent header with navigation."""
    return """
    <header>
        <div class="logo"><a href="/">LondonFoodFinds</a></div>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/neighbourhoods/">Neighbourhoods</a></li>
                <li><a href="/cuisine/">Cuisines</a></li>
                <li><a href="/#about">About</a></li>
            </ul>
        </nav>
    </header>
    """


def build_footer(popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> str:
    """Build consistent footer with links."""
    neighbourhood_links = "\n".join(
        f'<li><a href="/{item["slug"]}/">{item["city"]}</a></li>'
        for item in popular_neighbourhoods[:5]
    )
    cuisine_links = "\n".join(
        f'<li><a href="/cuisine/{item["slug"]}/">{item["cuisine"]}</a></li>'
        for item in popular_cuisines[:5]
    )
    
    return f"""
    <footer id="contact">
        <div class="columns">
            <div>
                <strong>About LondonFoodFinds</strong>
                <p>Your guide to the best restaurants in London. Find top-rated places to eat near you.</p>
                <p><a href="https://www.tiktok.com/@londonfoodfindsuk/" target="_blank" rel="noopener">TikTok</a></p>
            </div>
            <div>
                <p>Popular Neighbourhoods</p>
                <ul>
                    {neighbourhood_links}
                </ul>
            </div>
            <div>
                <p>Popular Cuisines</p>
                <ul>
                    {cuisine_links}
                </ul>
            </div>
        </div>
        <p class="muted">© 2025 LondonFoodFinds. All rights reserved.</p>
        <p><a href="/#about">About</a></p>
    </footer>
    """


def render_page(title: str, meta_desc: str, body_html: str, popular_neighbourhoods: List[Dict] = None, popular_cuisines: List[Dict] = None) -> str:
    """Wrap shared head/foot markup around a page body."""
    if popular_neighbourhoods is None:
        popular_neighbourhoods = []
    if popular_cuisines is None:
        popular_cuisines = []
    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>
    {build_header()}
    {body_html}
    {build_footer(popular_neighbourhoods, popular_cuisines)}
</body>
</html>"""


def create_css_file() -> None:
    """Create external CSS file."""
    css_content = """
:root {
    --red: #d32323;
    --dark: #1c1c1c;
    --grey: #f5f5f5;
    --text: #2d2d2d;
    --card: #ffffff;
    --muted: #6b6b6b;
}

* {
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

body {
    margin: 0;
    background: var(--grey);
    color: var(--text);
    line-height: 1.6;
}

/* Header */
header {
    background: #fff;
    border-bottom: 1px solid #ececec;
    padding: 1rem 5vw;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 10;
    gap: 1rem;
}

header .logo {
    color: var(--red);
    font-weight: 700;
    font-size: 1.4rem;
}

header .logo a {
    color: var(--red);
    text-decoration: none;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 1.5rem;
    margin: 0;
    padding: 0;
}

nav a {
    text-decoration: none;
    color: var(--dark);
    font-weight: 600;
}

nav a:hover {
    color: var(--red);
}

/* Hero */
.hero {
    padding: 5rem 5vw 4rem;
    background: linear-gradient(135deg, rgba(5,5,5,0.4), rgba(5,5,5,0.7)), url('https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1400&q=60') center/cover;
    color: #fff;
    text-align: center;
}

.hero h1 {
    margin: 0 0 1rem;
    font-size: clamp(2.2rem, 6vw, 3.5rem);
}

.hero p {
    max-width: 52rem;
    margin: 0 auto;
    font-size: 1.1rem;
}

/* Main content */
main {
    padding: 3rem 5vw 5rem;
}

section {
    margin-bottom: 4rem;
}

.section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.section-head h2 {
    margin: 0;
    font-size: 1.6rem;
}

.section-head .eyebrow {
    font-size: .95rem;
    color: var(--muted);
}

/* Grids */
.grid {
    display: grid;
    gap: 1.25rem;
}

.grid--3 {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.grid--4 {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

/* Cards */
.card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: 0 5px 18px rgba(0,0,0,0.06);
    text-decoration: none;
    display: block;
    transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.card strong {
    display: block;
    font-size: 1.1rem;
    margin-bottom: .3rem;
    color: var(--dark);
}

.card span {
    color: #777;
    font-size: .95rem;
}

/* Feature cards (restaurants) */
.feature-card {
    background: #fff;
    border-radius: 18px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 70px rgba(0,0,0,0.08);
}

.feature-card .card-media {
    height: 180px;
    background-size: cover;
    background-position: center;
    position: relative;
}

.feature-card .card-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: .4rem;
}

.feature-card .badge {
    width: fit-content;
    background: #ffe5e5;
    color: var(--red);
    border-radius: 999px;
    padding: .15rem .85rem;
    font-weight: 600;
    font-size: .85rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: .5rem;
}

.feature-card h3 {
    margin: .25rem 0;
    font-size: 1.25rem;
    color: var(--dark);
}

.feature-card .meta {
    color: var(--muted);
    margin: 0;
    font-size: .95rem;
}

.feature-card .btn {
    margin-top: .5rem;
    background: var(--red);
    color: #fff;
    text-align: center;
    padding: .6rem 1rem;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 600;
    transition: background 0.2s;
}

.feature-card .btn:hover {
    background: #b01e1e;
}

/* Pills */
.pill {
    display: inline-flex;
    flex-direction: column;
    gap: .2rem;
    background: #fff;
    border-radius: 16px;
    padding: .9rem 1.1rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    text-decoration: none;
    transition: transform 0.2s, box-shadow 0.2s;
}

.pill:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.pill strong {
    font-size: 1rem;
    color: var(--dark);
}

.pill span {
    font-size: .85rem;
    color: var(--muted);
}

.pill-grid {
    display: grid;
    gap: .75rem;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

/* Pagination */
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: .5rem;
    margin-top: 2rem;
    padding: 1.5rem 0;
    flex-wrap: wrap;
}

.pagination .page-nav,
.pagination .page-num {
    padding: .5rem 1rem;
    text-decoration: none;
    color: var(--dark);
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fff;
    font-weight: 500;
    transition: background 0.2s;
}

.pagination .page-nav:hover,
.pagination .page-num:hover {
    background: var(--grey);
}

.pagination .page-num.active {
    background: var(--red);
    color: #fff;
    border-color: var(--red);
}

.pagination .page-nav.disabled {
    opacity: 0.4;
    cursor: not-allowed;
    pointer-events: none;
}

/* About section */
.about-text {
    background: #fff;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
}

.about-text p {
    margin: 0 0 1rem;
    line-height: 1.7;
}

.about-text p:last-child {
    margin-bottom: 0;
}

/* Header actions */
.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.restaurant-count {
    color: var(--muted);
    font-size: .95rem;
}

/* Footer */
footer {
    background: #111;
    color: #fff;
    padding: 2rem 5vw;
}

footer .columns {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

footer a {
    color: #fff;
    text-decoration: none;
    opacity: 0.8;
}

footer a:hover {
    opacity: 1;
}

footer ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: .4rem;
}

footer p {
    margin: 0 0 .5rem;
    color: #ccc;
}

.muted {
    color: var(--muted);
    font-size: .95rem;
}

/* Responsive */
@media (max-width: 768px) {
    nav ul {
        flex-wrap: wrap;
        gap: .75rem;
    }
    
    header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .section-head {
        flex-direction: column;
        gap: .4rem;
    }
    
    .grid--3 {
        grid-template-columns: 1fr;
    }
    
    .grid--4 {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .grid--3 {
        grid-template-columns: repeat(2, 1fr);
    }
}
"""
    
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    (CSS_DIR / "style.css").write_text(css_content, encoding="utf-8")


def build_london_homepage(london_records: List[Dict], cuisine_counts: Dict[str, int], all_cuisines: List[str], nearby_cities: List[Dict], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build homepage focused on London."""
    total_london = len(london_records)
    
    hero = f"""
    <div class="hero">
        <h1>Top {total_london} Best Restaurants in London</h1>
        <p>Discover top-rated dining options in London.</p>
    </div>
    """
    
    # Browse by Cuisine pills
    cuisine_pills = "\n".join(
        f'<a class="pill" href="/cuisine/{slugify(cat)}/"><strong>{cat}</strong><span>{count} restaurants</span></a>'
        for cat, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)[:12]
    )
    
    # All restaurants grid with pagination
    total_pages = (total_london + RESTAURANTS_PER_PAGE - 1) // RESTAURANTS_PER_PAGE
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * RESTAURANTS_PER_PAGE
        end_idx = start_idx + RESTAURANTS_PER_PAGE
        page_records = london_records[start_idx:end_idx]
        
        restaurant_cards = build_restaurant_cards(page_records)
        pagination_html = build_pagination(page_num, total_pages, "")
        
        nearby_html = "\n".join(
            f'<a class="card" href="/{item["slug"]}/"><strong>{item["city"]}</strong><span>{item["count"]} restaurants</span></a>'
            for item in nearby_cities[:3]
        )
        
        about_section = f"""
        <section id="about">
            <div class="section-head">
                <h2>About Top {total_london} Restaurants in London</h2>
            </div>
            <div class="about-text">
                <p>We've compiled the top {total_london} restaurants in London based on Google ratings and review counts. Whether you're looking for fine dining, casual eats, or something in between, our directory helps you discover the best dining experiences in London.</p>
                <p>Browse our selection of {total_london} restaurants in London, read reviews from other diners, and find the perfect spot for your next meal.</p>
            </div>
        </section>
        """
        
        body = f"""
        {hero}
        <main>
            <section>
                <div class="section-head">
                    <h2>Browse by Cuisine in London</h2>
                </div>
                <div class="pill-grid">
                    {cuisine_pills}
                </div>
            </section>
            
            <section>
                <div class="section-head">
                    <h2>All Restaurants in London</h2>
                    <span class="restaurant-count">{total_london} restaurants found.</span>
                </div>
                <div class="grid grid--3">
                    {restaurant_cards}
                </div>
                {pagination_html}
            </section>
            
            <section>
                <div class="section-head">
                    <h2>Nearby Neighbourhoods</h2>
                </div>
                <div class="grid grid--3">
                    {nearby_html}
                </div>
            </section>
            
            {about_section}
        </main>
        """
        
        html = render_page(
            f"Top {total_london} Best Restaurants in London",
            f"Discover the top {total_london} restaurants in London. Browse by cuisine, read reviews, and find your perfect dining experience.",
            body,
            popular_neighbourhoods,
            popular_cuisines,
        )
        
        filename = "index.html" if page_num == 1 else f"page{page_num}.html"
        (OUTPUT_DIR / filename).write_text(html, encoding="utf-8")


def build_cuisine_index_page(all_cuisines: List[Dict], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build /cuisine/index.html listing all cuisines."""
    cuisine_dir = OUTPUT_DIR / "cuisine"
    cuisine_dir.mkdir(parents=True, exist_ok=True)
    
    hero = """
    <div class="hero">
        <h1>All Cuisines in London</h1>
        <p>Browse restaurants by cuisine type.</p>
    </div>
    """
    
    cuisine_cards = "\n".join(
        f'<a class="card" href="/cuisine/{item["slug"]}/"><strong>{item["cuisine"]}</strong><span>{item["count"]} restaurants</span></a>'
        for item in sorted(all_cuisines, key=lambda x: x["count"], reverse=True)
    )
    
    body = f"""
    {hero}
    <main>
        <section>
            <div class="grid grid--4">
                {cuisine_cards}
            </div>
        </section>
    </main>
    """
    
    html = render_page(
        "All Cuisines in London",
        "Browse all cuisines available in London restaurants.",
        body,
        popular_neighbourhoods,
        popular_cuisines,
    )
    (cuisine_dir / "index.html").write_text(html, encoding="utf-8")


def build_cuisine_page(cuisine: str, cuisine_slug: str, records: List[Dict], all_cuisines: List[str], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build cuisine page at /cuisine/[slug] with pagination."""
    cuisine_dir = OUTPUT_DIR / "cuisine" / cuisine_slug
    cuisine_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort by rating by default
    sorted_records = sorted(records, key=lambda x: (x.get("rating", 0) or 0, x.get("reviews", 0) or 0), reverse=True)
    
    total = len(sorted_records)
    total_pages = (total + RESTAURANTS_PER_PAGE - 1) // RESTAURANTS_PER_PAGE
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * RESTAURANTS_PER_PAGE
        end_idx = start_idx + RESTAURANTS_PER_PAGE
        page_records = sorted_records[start_idx:end_idx]
        
        restaurant_cards = build_restaurant_cards(page_records)
        pagination_html = build_pagination(page_num, total_pages, f"/cuisine/{cuisine_slug}")
        
        hero = f"""
        <div class="hero">
            <h1>Best {cuisine} in London</h1>
            <p>Browse all {cuisine.lower()} restaurants in London.</p>
        </div>
        """
        
        # Cuisine filter pills
        filter_pills = "\n".join(
            f'<a class="pill" href="/cuisine/{slugify(cat)}/"><strong>{cat}</strong></a>'
            for cat in sorted(set(all_cuisines))[:15]
        )
        
        body = f"""
        {hero}
        <main>
            <section>
                <div class="section-head">
                    <h2>Browse by Cuisine in London</h2>
                </div>
                <div class="pill-grid">
                    {filter_pills}
                </div>
            </section>
            
            <section>
                <div class="section-head">
                    <h2>All {cuisine} Restaurants in London</h2>
                    <span class="restaurant-count">{total} restaurants found.</span>
                </div>
                <div class="grid grid--3">
                    {restaurant_cards}
                </div>
                {pagination_html}
            </section>
        </main>
        """
        
        html = render_page(
            f"Best {cuisine} in London",
            f"Discover the best {cuisine.lower()} restaurants in London. Browse {total} restaurants, read reviews, and find your perfect dining experience.",
            body,
            popular_neighbourhoods,
            popular_cuisines,
        )
        
        filename = "index.html" if page_num == 1 else f"page{page_num}.html"
        (cuisine_dir / filename).write_text(html, encoding="utf-8")


def build_neighbourhoods_page(all_cities: List[Dict], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build /neighbourhoods/index.html listing all neighborhoods."""
    neighbourhood_dir = OUTPUT_DIR / "neighbourhoods"
    neighbourhood_dir.mkdir(parents=True, exist_ok=True)
    
    hero = """
    <div class="hero">
        <h1>All London Neighbourhoods</h1>
        <p>Browse restaurants by neighbourhood, sorted by number of restaurants.</p>
    </div>
    """
    
    city_cards = "\n".join(
        f'<a class="card" href="/{item["slug"]}/"><strong>{item["city"]}</strong><span>{item["count"]} restaurants</span></a>'
        for item in sorted(all_cities, key=lambda x: x["count"], reverse=True)
    )
    
    body = f"""
    {hero}
    <main>
        <section>
            <div class="grid grid--4">
                {city_cards}
            </div>
        </section>
    </main>
    """
    
    html = render_page(
        "All London Neighbourhoods",
        "Browse all London neighbourhoods and discover restaurants in each area.",
        body,
        popular_neighbourhoods,
        popular_cuisines,
    )
    (neighbourhood_dir / "index.html").write_text(html, encoding="utf-8")


def build_neighbourhood_page(city: str, slug: str, records: List[Dict], categories: Counter, nearby_cities: List[Dict], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build neighbourhood page with pagination."""
    city_dir = OUTPUT_DIR / slug
    city_dir.mkdir(parents=True, exist_ok=True)
    
    total_restaurants = len(records)
    total_pages = (total_restaurants + RESTAURANTS_PER_PAGE - 1) // RESTAURANTS_PER_PAGE
    
    category_links = "\n".join(
        f'<a class="pill" href="/{slug}/{slugify(cat)}/"><strong>{cat}</strong><span>{count} restaurants</span></a>'
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:8]
    )
    
    nearby_html = "\n".join(
        f'<a class="card" href="/{item["slug"]}/"><strong>{item["city"]}</strong><span>{item["count"]} restaurants</span></a>'
        for item in nearby_cities[:3]
    )
    
    for page_num in range(1, total_pages + 1):
        start_idx = (page_num - 1) * RESTAURANTS_PER_PAGE
        end_idx = start_idx + RESTAURANTS_PER_PAGE
        page_records = records[start_idx:end_idx]
        
        restaurant_cards = build_restaurant_cards(page_records)
        pagination_html = build_pagination(page_num, total_pages, f"/{slug}")
        
        hero = f"""
        <div class="hero">
            <h1>Top {total_restaurants} Best Restaurants in {city}</h1>
            <p>Discover top-rated dining options in {city}.</p>
        </div>
        """
        
        about_section = f"""
        <section id="about">
            <div class="section-head">
                <h2>About Top {total_restaurants} Restaurants in {city}</h2>
            </div>
            <div class="about-text">
                <p>We've compiled the top {total_restaurants} restaurants in {city}, Greater London, based on Google ratings and review counts. Whether you're looking for fine dining, casual eats, or something in between, our directory helps you discover the best dining experiences in {city}.</p>
                <p>Browse our selection of {total_restaurants} restaurants in {city}, read reviews from other diners, and find the perfect spot for your next meal.</p>
            </div>
        </section>
        """
        
        body = f"""
        {hero}
        <main>
            <section>
                <div class="section-head">
                    <h2>Browse by Cuisine in {city}</h2>
                </div>
                <div class="pill-grid">
                    {category_links or '<p>No categories available.</p>'}
                </div>
            </section>
            
            <section>
                <div class="section-head">
                    <h2>All Restaurants in {city}</h2>
                    <span class="restaurant-count">{total_restaurants} restaurants found.</span>
                </div>
                <div class="grid grid--3">
                    {restaurant_cards}
                </div>
                {pagination_html}
            </section>
            
            <section>
                <div class="section-head">
                    <h2>Nearby Neighbourhoods</h2>
                </div>
                <div class="grid grid--3">
                    {nearby_html or '<p>No nearby neighborhoods available.</p>'}
                </div>
            </section>
            
            {about_section}
        </main>
        """
        
        html = render_page(
            f"Top {total_restaurants} Best Restaurants in {city}",
            f"Discover the top {total_restaurants} restaurants in {city}, Greater London. Browse by cuisine, read reviews, and find your perfect dining experience.",
            body,
            popular_neighbourhoods,
            popular_cuisines,
        )
        
        filename = "index.html" if page_num == 1 else f"page{page_num}.html"
        (city_dir / filename).write_text(html, encoding="utf-8")


def build_category_page(city: str, city_slug: str, category: str, records: List[Dict], popular_neighbourhoods: List[Dict], popular_cuisines: List[Dict]) -> None:
    """Build /city/category/ page."""
    cat_slug = slugify(category)
    cat_dir = OUTPUT_DIR / city_slug / cat_slug
    cat_dir.mkdir(parents=True, exist_ok=True)
    
    hero = f"""
    <div class="hero">
        <h1>Best {category} in {city}</h1>
        <p>Every listing is sorted by Google review score first, then volume, helping diners find standout {category.lower()} options fast.</p>
    </div>
    """
    
    restaurant_cards = build_restaurant_cards(records)
    
    body = f"""
    {hero}
    <main>
        <section>
            <div class="grid grid--3">
                {restaurant_cards}
            </div>
        </section>
    </main>
    """
    
    html = render_page(
        f"Best {category} in {city}",
        f"Directory of the best {category.lower()} in {city}, ranked by Google reviews.",
        body,
        popular_neighbourhoods,
        popular_cuisines,
    )
    (cat_dir / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    """Main function to generate the entire static site."""
    print("Reading Excel file...")
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df = df[df["query"].str.contains("Greater London", na=False)].copy()
    
    print("Processing cities...")
    city_primary = df["city"].apply(normalize_city)
    borough_primary = df["borough"].apply(normalize_city)
    valid_cities = set(city_primary.dropna()) | set(KNOWN_AREAS)
    
    def pick_city(row: pd.Series) -> str:
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
    
    city_counts = df.groupby("city_clean")["city_clean"].transform("count")
    df = df[city_counts >= MIN_CITY_ROWS].copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0).astype(int)
    df["score"] = df["rating"].fillna(0) + (df["reviews"] / 1000)
    df["categories"] = df["subtypes"].apply(parse_categories)
    
    print("Cleaning output directory...")
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CSS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Creating CSS file...")
    create_css_file()
    
    print("Processing data summaries...")
    # Get London records for homepage
    london_df = df[df["city_clean"] == "London"].copy()
    london_records = london_df.sort_values(["score", "reviews"], ascending=False).to_dict("records")
    
    # Get cuisine counts for London
    exploded = df.explode("categories")
    london_exploded = exploded[exploded["city_clean"] == "London"]
    cuisine_counts = london_exploded[london_exploded["categories"].notna()].groupby("categories").size().to_dict()
    all_cuisines_list = list(cuisine_counts.keys())
    
    # Get all cities for neighbourhoods page
    all_cities_summary = []
    for city, chunk in df.groupby("city_clean"):
        all_cities_summary.append({
            "city": city,
            "slug": slugify(city),
            "count": len(chunk),
        })
    all_cities_summary.sort(key=lambda x: x["count"], reverse=True)
    
    # Get popular neighbourhoods and cuisines for footer
    popular_neighbourhoods = all_cities_summary[:5]
    all_cuisines_summary = [
        {"cuisine": cat, "slug": slugify(cat), "count": count}
        for cat, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    popular_cuisines = all_cuisines_summary[:5]
    
    # Get nearby cities (excluding London)
    nearby_cities = [item for item in all_cities_summary if item["city"] != "London"][:3]
    
    print("Building homepage...")
    build_london_homepage(london_records, cuisine_counts, all_cuisines_list, nearby_cities, popular_neighbourhoods, popular_cuisines)
    
    print("Building cuisine index page...")
    build_cuisine_index_page(all_cuisines_summary, popular_neighbourhoods, popular_cuisines)
    
    print("Building cuisine pages...")
    for cuisine, cat_df in london_exploded[london_exploded["categories"].notna()].groupby("categories"):
        cuisine_slug = slugify(cuisine)
        records = cat_df.sort_values(["score", "reviews"], ascending=False).to_dict("records")
        build_cuisine_page(cuisine, cuisine_slug, records, all_cuisines_list, popular_neighbourhoods, popular_cuisines)
    
    print("Building neighbourhoods page...")
    build_neighbourhoods_page(all_cities_summary, popular_neighbourhoods, popular_cuisines)
    
    print("Building neighbourhood pages...")
    for city, chunk in df.groupby("city_clean"):
        if city == "London":
            continue  # Already handled by homepage
        city_slug = slugify(city)
        records = chunk.sort_values(["score", "reviews"], ascending=False).to_dict("records")
        flat_cats = [cat for cats in chunk["categories"] if isinstance(cats, list) for cat in cats if cat]
        category_counts = Counter(flat_cats)
        filtered_counts = Counter({cat: count for cat, count in category_counts.items() if count >= 3})
        
        nearby = [item for item in all_cities_summary if item["city"] != city][:3]
        build_neighbourhood_page(city, city_slug, records, filtered_counts, nearby, popular_neighbourhoods, popular_cuisines)
        
        # Build category pages for this city
        city_exploded = exploded[(exploded["city_clean"] == city) & exploded["categories"].notna()]
        for category, cat_rows in city_exploded.groupby("categories"):
            if filtered_counts.get(category, 0) < 3:
                continue
            records = cat_rows.sort_values(["score", "reviews"], ascending=False).to_dict("records")
            build_category_page(city, city_slug, category, records, popular_neighbourhoods, popular_cuisines)
    
    print(f"✓ Site generated successfully in {OUTPUT_DIR}/")
    print(f"  - Homepage: {OUTPUT_DIR}/index.html")
    print(f"  - CSS: {CSS_DIR}/style.css")
    print(f"  - Total neighbourhoods: {len(all_cities_summary)}")
    print(f"  - Total cuisines: {len(all_cuisines_summary)}")


if __name__ == "__main__":
    main()
