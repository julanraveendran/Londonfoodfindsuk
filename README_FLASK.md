# LondonFoodFinds - Flask Web Application

A dynamic Flask web application for browsing restaurants in Greater London, built with Python, Flask, and Pandas.

## Features

- **Dynamic Routing**: Browse restaurants by neighbourhood, cuisine, or view all
- **Server-Side Pagination**: 12 restaurants per page with efficient pagination
- **Responsive Design**: Mobile (1 column), tablet (2 columns), desktop (3 columns)
- **Julan's Pick Badge**: Automatically highlights top-rated restaurants (4.5+ stars, 500+ reviews)
- **Search & Filter**: Filter by neighbourhood or cuisine type
- **Clean UI**: Grid-based layout matching the LondonFoodFinds design

## Requirements

- Python 3.7+
- Flask
- pandas
- openpyxl

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the Excel file `OS-20251124200014m1e_restaurant.xlsx` is in the same directory as `app.py`.

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will:
- Load and process the Excel file on startup
- Start the development server on `http://localhost:5000`

Open your browser and navigate to `http://localhost:5000`.

## Project Structure

```
londonfoodfinds/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── OS-20251124200014m1e_restaurant.xlsx  # Data source
├── templates/
│   ├── base.html              # Base template with header/footer
│   ├── index.html             # Homepage and filtered views
│   ├── categories.html        # Neighbourhoods/Cuisines grid pages
│   └── about.html             # About page
└── static/
    └── style.css              # Custom CSS stylesheet
```

## Routes

- `/` - Homepage with all London restaurants
- `/neighbourhoods` - Grid view of all neighbourhoods
- `/cuisines` - Grid view of all cuisines
- `/neighbourhood/<name>` - Restaurants filtered by neighbourhood
- `/cuisine/<name>` - Restaurants filtered by cuisine
- `/about` - About page

## URL Parameters

- `?page=N` - Pagination (e.g., `/?page=2`)

## Data Processing

On startup, the application:
1. Loads the Excel file into a Pandas DataFrame
2. Cleans and normalizes city/neighbourhood names
3. Extracts restaurant categories
4. Calculates cuisine and neighbourhood counts
5. Adds "Julan's Pick" flags based on rating and review count

## Configuration

You can modify these constants in `app.py`:

- `RESTAURANTS_PER_PAGE`: Number of restaurants per page (default: 12)
- `MIN_CITY_ROWS`: Minimum restaurants to create a neighbourhood page (default: 5)
- `KNOWN_AREAS`: List of valid Greater London areas

## Development

The Flask app runs in debug mode by default. To disable:

```python
app.config['DEBUG'] = False
```

## Production Deployment

For production deployment, consider:

1. Using a production WSGI server (e.g., Gunicorn)
2. Setting up environment variables for configuration
3. Implementing caching for data loading
4. Using a proper database instead of loading Excel on each startup

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## License

© 2025 LondonFoodFinds. All rights reserved.




