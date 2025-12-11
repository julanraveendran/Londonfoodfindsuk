# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify the Excel file is present:**
   - Make sure `OS-20251124200014m1e_restaurant.xlsx` is in the root directory

## Running the Application

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Access the website:**
   - Open your browser and go to: `http://localhost:5000`

3. **Initial load:**
   - The first time you run the app, it will process the Excel file
   - This may take 30-60 seconds depending on your computer
   - You'll see progress messages in the terminal

## Testing the Features

1. **Homepage (`/`)**
   - Should show "Top X Best Restaurants in London"
   - Scroll to see cuisine filter pills
   - View restaurant cards with ratings
   - Check pagination at the bottom
   - See "Nearby Neighbourhoods" section

2. **Navigation Menu:**
   - Click "Home" → goes to homepage
   - Click "Neighbourhoods" → shows all neighbourhoods page
   - Click "Cuisines" → shows all cuisines page
   - Click "About" → shows about page

3. **Cuisine Pages (`/cuisine/korean-restaurant`):**
   - Click any cuisine pill on homepage
   - Should filter restaurants by that cuisine
   - Pagination should work

4. **Neighbourhood Pages (`/neighbourhood/sutton`):**
   - Click any neighbourhood box
   - Should show restaurants in that area
   - Can filter by cuisine within the neighbourhood

5. **Mobile Responsive:**
   - Resize browser window
   - Menu should collapse on mobile
   - Cards should stack vertically

## Troubleshooting

**Error: "ModuleNotFoundError: No module named 'flask'"**
- Run: `pip install -r requirements.txt`

**Error: "FileNotFoundError: OS-20251124200014m1e_restaurant.xlsx"**
- Make sure the Excel file is in the same directory as `app.py`

**Slow loading:**
- First load processes 12,000+ restaurants - this is normal
- Subsequent page loads should be faster

**Images not showing:**
- Some restaurant images may not load if URLs are broken
- Placeholder "No Image" will show instead

## Next Steps

1. Replace `domain.co.uk` with your actual domain in:
   - `templates/base.html` (canonical links)
   - `templates/index.html` (schema markup)
   - `templates/cuisine.html` (schema markup)
   - `templates/neighbourhood.html` (schema markup)

2. Customize the "Julan's Pick" logic in `app.py` if needed

3. Adjust the number of restaurants per page in `app.py` (currently 12)

4. Deploy to a production server (Heroku, AWS, etc.)


