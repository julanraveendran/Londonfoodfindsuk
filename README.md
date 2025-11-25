# London Food Finds

A comprehensive restaurant directory website for Greater London, featuring 12,000+ restaurants with filtering by cuisine and neighbourhood.

## Features

- **Homepage** with top restaurants ranked by Google reviews
- **Cuisine pages** - Browse restaurants by cuisine type (e.g., Korean, Chinese, Italian)
- **Neighbourhood pages** - Explore restaurants by London area (e.g., Sutton, Bromley)
- **All Neighbourhoods page** - Complete list of London areas
- **All Cuisines page** - Complete list of cuisine types
- **About page** - Information about the directory
- **Sitemap** - Dynamic XML sitemap for SEO (`/sitemap.xml`)
- **Responsive design** - Works on desktop, tablet, and mobile
- **SEO optimized** - Clean URLs, metadata, and schema markup
- **Julan's Pick badges** - Highlights top-rated restaurants

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the Excel file `OS-20251124200014m1e_restaurant.xlsx` is in the root directory.

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The website will be available at `http://localhost:5000`

## URL Structure

- Homepage: `/`
- Paginated homepage: `/page/2`
- Cuisine page: `/cuisine/korean-restaurant`
- Neighbourhood page: `/neighbourhood/sutton`
- Neighbourhood with cuisine filter: `/neighbourhood/sutton/cuisine/korean-restaurant`
- All neighbourhoods: `/neighbourhoods`
- All cuisines: `/cuisines`
- About: `/about`
- Sitemap: `/sitemap.xml`

## Data Processing

The application processes restaurant data from the Excel file and:
- Extracts cuisine types from the `subtypes` column
- Groups restaurants by neighbourhood using the `city` column
- Ranks restaurants by Google review score (rating × review count)
- Marks top 5% as "Julan's Pick"

## Technologies

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, openpyxl
- **Styling**: Custom CSS matching EatingVancouver.ca design

## Notes

- Restaurant images are loaded from URLs in the data file
- If an image fails to load, a placeholder is shown
- Pagination shows 12 restaurants per page
- All links are fully functional and responsive
