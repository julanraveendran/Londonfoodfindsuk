# London Food Finds - Static Directory Site Generator

A Python script that generates a complete static HTML/CSS directory website for Greater London restaurants from an Excel file.

## Requirements

- Python 3.7+
- pandas
- openpyxl (for reading Excel files)

## Installation

1. Install required packages:
```bash
pip install pandas openpyxl
```

2. Ensure you have the Excel file `OS-20251124200014m1e_restaurant.xlsx` in the same directory as the script.

## Usage

Run the generator script:

```bash
python generate_site.py
```

The script will:
1. Read the Excel file
2. Process and clean restaurant data
3. Generate all HTML pages
4. Create CSS file at `site/css/style.css`
5. Create images directory at `site/images/`

## Output Structure

The generated site will be in the `site/` directory with the following structure:

```
site/
├── index.html              # Homepage
├── page2.html, page3.html  # Paginated homepage pages
├── css/
│   └── style.css          # External stylesheet
├── images/                 # Images directory
├── cuisine/
│   ├── index.html         # All cuisines listing
│   └── [cuisine-slug]/
│       ├── index.html     # Cuisine page
│       └── page2.html     # Paginated cuisine pages
├── neighbourhoods/
│   └── index.html         # All neighbourhoods listing
└── [neighbourhood-slug]/
    ├── index.html         # Neighbourhood page
    ├── page2.html         # Paginated neighbourhood pages
    └── [category-slug]/
        └── index.html     # Category page
```

## Preview Locally

### Option 1: Python HTTP Server

Navigate to the `site` directory and run:

```bash
cd site
python -m http.server 8000
```

Then open your browser to `http://localhost:8000`

### Option 2: Serve from Root Directory

If you want to serve from the project root (to access `/css/style.css` correctly):

```bash
python -m http.server 8000
```

Then open your browser to `http://localhost:8000/site/`

### Option 3: Any Static File Server

The `site/` directory can be uploaded to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Any web server

Just upload the entire `site/` folder contents.

## Features

- **Pure Static HTML/CSS**: No JavaScript required
- **Responsive Design**: Mobile (1 column), tablet (2 columns), desktop (3 columns)
- **SEO Optimized**: Meta tags and Schema.org Restaurant markup
- **Pagination**: Server-side pagination with 12 restaurants per page
- **Navigation**: All header and footer links are functional HTML links
- **Restaurant Cards**: Include rating, reviews, address, phone, website link
- **"Julan's Pick" Badge**: Automatically shown on high-rated restaurants (4.5+ stars, 500+ reviews)

## URL Structure

- Homepage: `/`
- Cuisine pages: `/cuisine/[cuisine-slug]/`
- All cuisines: `/cuisine/`
- Neighbourhood pages: `/[neighbourhood-slug]/`
- All neighbourhoods: `/neighbourhoods/`
- Category pages: `/[neighbourhood-slug]/[category-slug]/`

## Configuration

You can modify these constants in `generate_site.py`:

- `RESTAURANTS_PER_PAGE`: Number of restaurants per page (default: 12)
- `MIN_CITY_ROWS`: Minimum restaurants required to create a neighbourhood page (default: 5)
- `KNOWN_AREAS`: List of valid Greater London areas

## Notes

- All images use URLs from the Excel file. Missing images fall back to a placeholder.
- Restaurant sorting is by Google rating (descending), then review count (descending).
- Only cuisines and neighbourhoods with 3+ restaurants are displayed.
- The site is completely static and can be served by any web server.

## License

© 2025 LondonFoodFinds. All rights reserved.




