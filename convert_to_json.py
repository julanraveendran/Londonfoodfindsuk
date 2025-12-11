"""
Script to convert Excel data to JSON for faster loading on Vercel
Run this locally before deploying to create the processed_data.json file
"""
import pandas as pd
import json
from app import load_and_process_data

print("Converting Excel data to JSON...")
print("This may take a minute...")

# Load and process data (this uses the same function from app.py)
load_and_process_data()

# Import the global variables after processing
from app import restaurants_data, cuisines_dict, neighbourhoods_dict

# Save to JSON
data_to_save = {
    'restaurants': restaurants_data,
    'cuisines': cuisines_dict,
    'neighbourhoods': neighbourhoods_dict
}

print(f"\nSaving processed data...")
print(f"  - {len(restaurants_data)} restaurants")
print(f"  - {len(cuisines_dict)} cuisines")
print(f"  - {len(neighbourhoods_dict)} neighbourhoods")

with open('processed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=2)

print("\nSuccess! processed_data.json created.")
print("You can now deploy to Vercel. The JSON file will be loaded instead of Excel.")

