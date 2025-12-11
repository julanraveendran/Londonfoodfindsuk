"""
Script to create processed_data.json from Excel file for Vercel deployment.
Run this locally before deploying to generate the JSON file.
"""
import pandas as pd
import json
import os
from app import load_data, df, cuisine_counts, neighbourhood_counts, KNOWN_AREAS

def export_to_json():
    """Export processed DataFrame to JSON format."""
    print("Loading data from Excel...")
    
    # Load the data using the app's load_data function
    load_data()
    
    if df is None or df.empty:
        print("Error: No data loaded!")
        return False
    
    print(f"Loaded {len(df)} restaurants")
    
    # Convert DataFrame to list of dictionaries
    restaurants_list = df.to_dict('records')
    
    # Prepare data for JSON export
    data_to_export = {
        'restaurants': restaurants_list,
        'cuisines': cuisine_counts,
        'neighbourhoods': neighbourhood_counts
    }
    
    # Save to JSON
    output_file = "processed_data.json"
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_export, f, ensure_ascii=False, indent=2, default=str)
    
    file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
    print(f"Success! Created {output_file}")
    print(f"  - {len(restaurants_list)} restaurants")
    print(f"  - {len(cuisine_counts)} cuisines")
    print(f"  - {len(neighbourhood_counts)} neighbourhoods")
    print(f"  - File size: {file_size:.2f} MB")
    print("\nYou can now deploy to Vercel. The JSON file will be loaded instead of Excel.")
    
    return True

if __name__ == '__main__':
    if not os.path.exists("OS-20251124200014m1e_restaurant.xlsx"):
        print("Error: Excel file not found!")
        print("Please ensure OS-20251124200014m1e_restaurant.xlsx is in the current directory")
    else:
        export_to_json()

