from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
import csv
import re
import os
import hashlib
from datetime import datetime
import time
import uuid  # Add UUID import for generating truly unique IDs
from config.settings import (
    ROOM_RENTAL_TITLE_TERMS,
    ROOM_RENTAL_DESCRIPTION_TERMS
)

app = FastAPI(title="Houses API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins including ngrok
    allow_credentials=False,  # Must be False when using "*" for origins
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# File paths
EXCEL_PATH = Path("data/houses.csv")
CONTACTED_PATH = Path("data/contacted_houses.json")
DISCARDED_PATH = Path("data/discarded_houses.json")
FAVORITES_PATH = Path("data/favorite_houses.json")
HOUSE_IDS_PATH = Path("data/house_ids.json")
ERA_STATUS_PATH = Path("data/scraper_status/era_status.json")
IMOVIRTUAL_STATUS_PATH = Path("data/scraper_status/imovirtual_status.json")

def load_contacted_houses():
    """Load contacted houses from JSON file, create if doesn't exist"""
    if CONTACTED_PATH.exists():
        with open(CONTACTED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support only the new format with by_id
                return {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except:
                return {"houses": set(), "by_id": {}}
    else:
        # Create the directory if it doesn't exist
        CONTACTED_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file with proper structure
        empty_data = {"houses": [], "by_id": {}}
        with open(CONTACTED_PATH, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, ensure_ascii=False, indent=2)
        
    return {"houses": set(), "by_id": {}}

def save_contacted_houses(contacted_data):
    """Save contacted houses to JSON file"""
    try:
        with open(CONTACTED_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": [], # Keep empty list for backward compatibility
                "by_id": contacted_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save contacted houses: {str(e)}")
        pass

def load_discarded_houses():
    """Load discarded houses from JSON file, create if doesn't exist"""
    if DISCARDED_PATH.exists():
        with open(DISCARDED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support only the new format with by_id
                return {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except:
                return {"houses": set(), "by_id": {}}
    else:
        # Create the directory if it doesn't exist
        DISCARDED_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file with proper structure
        empty_data = {"houses": [], "by_id": {}}
        with open(DISCARDED_PATH, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, ensure_ascii=False, indent=2)
        
    return {"houses": set(), "by_id": {}}

def save_discarded_houses(discarded_data):
    """Save discarded houses to JSON file"""
    try:
        with open(DISCARDED_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": [], # Keep empty list for backward compatibility
                "by_id": discarded_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save discarded houses: {str(e)}")

def load_favorite_houses():
    """Load favorite houses from JSON file, create if doesn't exist"""
    if FAVORITES_PATH.exists():
        with open(FAVORITES_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support only the new format with by_id
                return {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except:
                return {"houses": set(), "by_id": {}}
    else:
        # Create the directory if it doesn't exist
        FAVORITES_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file with proper structure
        empty_data = {"houses": [], "by_id": {}}
        with open(FAVORITES_PATH, 'w', encoding='utf-8') as f:
            json.dump(empty_data, f, ensure_ascii=False, indent=2)
        
    return {"houses": set(), "by_id": {}}

def save_favorite_houses(favorite_data):
    """Save favorite houses to JSON file"""
    try:
        with open(FAVORITES_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": [], # Keep empty list for backward compatibility
                "by_id": favorite_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to save favorite houses: {str(e)}")

def generate_house_id(house_data):
    """Generate a unique ID using UUID"""
    # Return a shortened version of a UUID (first 10 characters)
    return str(uuid.uuid4())[:10]

def load_house_ids():
    """Load house ID mappings from JSON file, create if doesn't exist"""
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Create the directory if it doesn't exist
        HOUSE_IDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file with proper structure
        with open(HOUSE_IDS_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        
    return {}

def save_house_ids(house_ids):
    """Save house ID mappings to JSON file"""
    with open(HOUSE_IDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(house_ids, f, ensure_ascii=False, indent=2)

def get_house_name_from_id(house_id, house_ids_dict):
    """Get house name from ID using the mapping dictionary"""
    for name, id_val in house_ids_dict.items():
        if id_val == house_id:
            return name
    return None

# Initialize houses from files
contacted_houses = load_contacted_houses()
discarded_houses = load_discarded_houses()
favorite_houses = load_favorite_houses()
house_ids = load_house_ids()

def deduplicate_image_urls(urls):
    """Remove duplicate image URLs by comparing base names without extensions"""
    if not urls:
        return []
    
    # Convert string representation of list to actual list if needed
    if isinstance(urls, str):
        try:
            # Try to parse as JSON first
            urls = json.loads(urls)
        except json.JSONDecodeError:
            try:
                # Fallback to eval if JSON parsing fails
                urls = eval(urls)
            except:
                # If both fail, try to split by comma if it looks like a comma-separated string
                if ',' in urls:
                    urls = [url.strip(' "[]\'') for url in urls.split(',')]
                else:
                    return []
    
    # Ensure we have a list
    if not isinstance(urls, list):
        return []
    
    # Helper function to get base name without extension
    def get_base_name(url):
        # Split URL by '/' and get the last part
        filename = url.split('/')[-1]
        # Remove extension
        return filename.rsplit('.', 1)[0]
    
    # Use dict to keep only one URL per base name
    unique_urls = {}
    for url in urls:
        if not isinstance(url, str):
            continue
        base_name = get_base_name(url)
        # Prefer webp format if available
        if base_name not in unique_urls or url.endswith('.webp'):
            unique_urls[base_name] = url
    
    return list(unique_urls.values())

def process_houses_data(sort_column=None, sort_order="asc"):
    """Process houses data and prepare for API response"""
    # Try to read the CSV file with houses
    if not Path(EXCEL_PATH).exists():
        return {"houses": [], "by_id": {}}, False, {}
        
    try:
        contacted_data = load_contacted_houses()
        discarded_data = load_discarded_houses()
        favorite_data = load_favorite_houses()
    except Exception as e:
        # Initialize with empty data
        contacted_data = {"houses": set(), "by_id": {}}
        discarded_data = {"houses": set(), "by_id": {}}
        favorite_data = {"houses": set(), "by_id": {}}
    
    try:
        # Read the DataFrame from CSV
        df = pd.read_csv(EXCEL_PATH, 
                        quoting=csv.QUOTE_ALL, 
                        escapechar='\\',
                        lineterminator='\n',
                        on_bad_lines='warn')
        
        # Convert numeric columns
        for col in ['Price', 'Area', 'Bedrooms']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Load existing house IDs
        house_ids = load_house_ids()
        house_ids_updated = False
            
        # Add house_id to each house and check states
        for index, row in df.iterrows():
            house_data = row.to_dict()
            
            # Generate house ID if not already assigned
            house_name = house_data.get('Name', '')
            if house_name in house_ids:
                house_data['house_id'] = house_ids[house_name]
            else:
                # Generate new ID using UUID
                house_data['house_id'] = generate_house_id(house_data)
                house_ids[house_name] = house_data['house_id']
                house_ids_updated = True
            
            # Set initial states - only check by_id
            house_data['contacted'] = house_data['house_id'] in contacted_data['by_id']
            house_data['discarded'] = house_data['house_id'] in discarded_data['by_id']
            house_data['favorite'] = house_data['house_id'] in favorite_data['by_id']
            
            # Update the DataFrame with the house_id
            df.at[index, 'house_id'] = house_data['house_id']
        
        # Deduplicate image URLs if available
        if 'Image URLs' in df.columns:
            df['Image URLs'] = df['Image URLs'].apply(deduplicate_image_urls)
        
        # Save updated house IDs
        if house_ids_updated:
            save_house_ids(house_ids)
            
        # Create a temporary column with house_ids for filtering
        df['temp_house_id'] = df['house_id']
            
        # Filter out discarded houses
        if len(discarded_data['by_id']) > 0:
            discarded_ids = set(discarded_data['by_id'].keys())
            df = df[~df['temp_house_id'].isin(discarded_ids)]
            
        # Filter out room rentals
        def is_room_rental(row):
            name = str(row['Name']).upper()
            
            # Check title for room rental terms
            is_room_by_title = any(name.startswith(term) for term in ROOM_RENTAL_TITLE_TERMS)
            
            return is_room_by_title

        # Apply room rental filter
        df = df[~df.apply(is_room_rental, axis=1)]
            
        # Remove the temporary column
        df = df.drop('temp_house_id', axis=1)
            
        # Sort the DataFrame
        if sort_column and sort_column in df.columns:
            # For numeric columns, ensure they are converted
            if sort_column in ['Price', 'Area', 'Bedrooms']:
                df[sort_column] = pd.to_numeric(df[sort_column], errors='coerce')
                
            # Sort with NaN values at the end
            df = df.sort_values(by=sort_column, 
                              ascending=True if sort_order == "asc" else False,
                              na_position='last')
                
        # Convert DataFrame to list of dictionaries
        houses = df.fillna('').to_dict(orient='records')
        
        # Create mapping of house_id to house data
        houses_by_id = {house['house_id']: house for house in houses}
        
        # Return the houses, house IDs update status, and the mapping  
        return houses, house_ids_updated, houses_by_id
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"houses": [], "by_id": {}}, False, {}

@app.get("/houses")
async def get_houses():
    """API endpoint to get all houses"""
    if not EXCEL_PATH.exists():
        return JSONResponse({"error": "Houses data file not found"})
    
    # Use the common process_houses_data function
    houses, updated_ids, house_ids = process_houses_data()
    
    # Save the updated house IDs if any new ones were added
    if updated_ids:
        save_house_ids(house_ids)
    
    return JSONResponse({"houses": houses})

@app.get("/sort/{column}")
async def sort_houses(column: str, order: str = "asc"):
    # Use the common process_houses_data function with sorting
    houses, updated_ids, house_ids = process_houses_data(column, order)
    
    # Save the updated house IDs if any new ones were added
    if updated_ids:
        save_house_ids(house_ids)
    
    return JSONResponse({"houses": houses})

@app.get("/")
async def root():
    """API root endpoint - redirect to houses"""
    return await get_houses()

@app.post("/toggle-contacted")
async def toggle_contacted(house_id: str):
    # Read current contacted houses directly from the JSON file
    if CONTACTED_PATH.exists():
        with open(CONTACTED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                contacted_data = {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except Exception as e:
                contacted_data = {"houses": set(), "by_id": {}}
    else:
        contacted_data = {"houses": set(), "by_id": {}}
    
    # Load house IDs mapping
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            house_ids = json.load(f)
    else:
        house_ids = {}
        
    # Find house name from ID
    house_name = get_house_name_from_id(house_id, house_ids)
    
    if not house_name:
        return JSONResponse({"error": f"House not found for ID: {house_id}", "contacted": False}, status_code=404)
    
    # Check if the house is already in the ID map
    is_contacted_by_id = house_id in contacted_data["by_id"]
    
    # Toggle the contacted status
    if is_contacted_by_id:
        # Remove from the ID mapping
        del contacted_data["by_id"][house_id]
        contacted = False
    else:
        contacted_data["by_id"][house_id] = house_name
        contacted = True
    
    # Save changes to file
    save_contacted_houses(contacted_data)
    
    return JSONResponse({"contacted": contacted})

@app.post("/toggle-discarded")
async def toggle_discarded(house_id: str):
    # Read current discarded houses directly from the JSON file
    if DISCARDED_PATH.exists():
        with open(DISCARDED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                discarded_data = {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except Exception as e:
                discarded_data = {"houses": set(), "by_id": {}}
    else:
        discarded_data = {"houses": set(), "by_id": {}}
    
    # Load house IDs mapping
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            house_ids = json.load(f)
    else:
        house_ids = {}
        
    # Find house name from ID
    house_name = get_house_name_from_id(house_id, house_ids)
    
    if not house_name:
        return JSONResponse({"error": f"House not found for ID: {house_id}", "discarded": False}, status_code=404)
    
    # Check if the house is already in the ID map
    is_discarded_by_id = house_id in discarded_data["by_id"]
    
    # Toggle the discarded status
    if is_discarded_by_id:
        # Remove from the ID mapping
        del discarded_data["by_id"][house_id]
        discarded = False
    else:
        discarded_data["by_id"][house_id] = house_name
        discarded = True
    
    # Save changes to file
    save_discarded_houses(discarded_data)
    
    return JSONResponse({"discarded": discarded})

@app.get("/scraper-status")
async def get_scraper_status():
    """Get the status of all scrapers"""
    status_data = {}
    
    # Directory containing scraper status files
    status_dir = Path("data/scraper_status")
    
    # Dynamically find all status files
    if status_dir.exists() and status_dir.is_dir():
        for status_file in status_dir.glob("*_status.json"):
            scraper_name = status_file.stem.replace('_status', '')
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    scraper_data = json.load(f)
                    # Get the most recent status entry
                    if scraper_data and len(scraper_data) > 0:
                        latest = scraper_data[0]  # Assuming the most recent is first
                        # Format the scraper name to be more readable
                        display_name = scraper_name.replace('_', ' ').title()
                        status_data[scraper_name] = {
                            "name": display_name,
                            "status": latest["status"],
                            "timestamp": latest["timestamp"],
                            "houses_processed": latest["houses_processed"],
                            "houses_found": latest["houses_found"],
                            "error_message": latest["error_message"]
                        }
            except Exception as e:
                # Format the scraper name to be more readable
                display_name = scraper_name.replace('_', ' ').title()
                status_data[scraper_name] = {
                    "name": display_name,
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                    "houses_processed": 0,
                    "houses_found": 0,
                    "error_message": str(e)
                }
    
    return JSONResponse(status_data)

@app.post("/toggle-favorite")
async def toggle_favorite(house_id: str):
    # Read current favorite houses directly from the JSON file
    if FAVORITES_PATH.exists():
        with open(FAVORITES_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                favorite_data = {
                    "houses": set(), 
                    "by_id": data.get("by_id", {})
                }
            except Exception as e:
                favorite_data = {"houses": set(), "by_id": {}}
    else:
        favorite_data = {"houses": set(), "by_id": {}}
    
    # Load house IDs mapping
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            house_ids = json.load(f)
    else:
        house_ids = {}
        
    # Find house name from ID
    house_name = get_house_name_from_id(house_id, house_ids)
    
    if not house_name:
        return JSONResponse({"error": f"House not found for ID: {house_id}", "favorite": False}, status_code=404)
    
    # Check if the house is already in the ID map
    is_favorite_by_id = house_id in favorite_data["by_id"]
    
    # Toggle the favorite status
    if is_favorite_by_id:
        # Remove from the ID mapping
        del favorite_data["by_id"][house_id]
        favorite = False
    else:
        favorite_data["by_id"][house_id] = house_name
        favorite = True
    
    # Save changes to file
    save_favorite_houses(favorite_data)
    
    return JSONResponse({"favorite": favorite}) 