from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
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

# Setup templates directory
templates = Jinja2Templates(directory="api/templates")

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
                # Support both old format (list of house names) and new format (dict of house_id to house_name)
                if isinstance(data, list):
                    # Old format - convert to dict with empty house_ids
                    return {"houses": set(data), "by_id": {}}
                else:
                    # New format - ensure both keys exist
                    return {
                        "houses": set(data.get("houses", [])), 
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
        print(f"[DEBUG] Created new empty contacted houses file at {CONTACTED_PATH}")
        
    return {"houses": set(), "by_id": {}}

def save_contacted_houses(contacted_data):
    """Save contacted houses to JSON file"""
    try:
        with open(CONTACTED_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": list(contacted_data["houses"]),
                "by_id": contacted_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Successfully saved {len(data_to_save['houses'])} contacted houses and {len(data_to_save['by_id'])} IDs")
    except Exception as e:
        print(f"[ERROR] Failed to save contacted houses: {str(e)}")

def load_discarded_houses():
    """Load discarded houses from JSON file, create if doesn't exist"""
    if DISCARDED_PATH.exists():
        with open(DISCARDED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support both old format (list of house names) and new format (dict of house_id to house_name)
                if isinstance(data, list):
                    # Old format - convert to dict with empty house_ids
                    return {"houses": set(data), "by_id": {}}
                else:
                    # New format - ensure both keys exist
                    return {
                        "houses": set(data.get("houses", [])), 
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
        print(f"[DEBUG] Created new empty discarded houses file at {DISCARDED_PATH}")
        
    return {"houses": set(), "by_id": {}}

def save_discarded_houses(discarded_data):
    """Save discarded houses to JSON file"""
    try:
        with open(DISCARDED_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": list(discarded_data["houses"]),
                "by_id": discarded_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Successfully saved {len(data_to_save['houses'])} discarded houses and {len(data_to_save['by_id'])} IDs")
    except Exception as e:
        print(f"[ERROR] Failed to save discarded houses: {str(e)}")

def load_favorite_houses():
    """Load favorite houses from JSON file, create if doesn't exist"""
    if FAVORITES_PATH.exists():
        with open(FAVORITES_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support both old format (list of house names) and new format (dict of house_id to house_name)
                if isinstance(data, list):
                    # Old format - convert to dict with empty house_ids
                    return {"houses": set(data), "by_id": {}}
                else:
                    # New format - ensure both keys exist
                    return {
                        "houses": set(data.get("houses", [])), 
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
        print(f"[DEBUG] Created new empty favorite houses file at {FAVORITES_PATH}")
        
    return {"houses": set(), "by_id": {}}

def save_favorite_houses(favorite_data):
    """Save favorite houses to JSON file"""
    try:
        with open(FAVORITES_PATH, 'w', encoding='utf-8') as f:
            data_to_save = {
                "houses": list(favorite_data["houses"]),
                "by_id": favorite_data["by_id"]
            }
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Successfully saved {len(data_to_save['houses'])} favorite houses and {len(data_to_save['by_id'])} IDs")
    except Exception as e:
        print(f"[ERROR] Failed to save favorite houses: {str(e)}")

def generate_house_id(house_data):
    """Generate a unique ID"""
    # Create a hash and return a shortened version (first 10 characters)
    return hashlib.md5(str(uuid.uuid4().hex[:10]).encode('utf-8')).hexdigest()[:10]

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
        print(f"[DEBUG] Created new empty house IDs file at {HOUSE_IDS_PATH}")
        
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
    """Process houses data and prepare for API or HTML response"""
    # Try to read the CSV file with houses
    if not Path(EXCEL_PATH).exists():
        print(f"CSV file {EXCEL_PATH} does not exist")
        return {"houses": [], "by_id": {}}, False, {}
        
    try:
        contacted_data = load_contacted_houses()
        discarded_data = load_discarded_houses()
        favorite_data = load_favorite_houses()
            
        # Debug prints
        print(f"Loaded {len(contacted_data['houses'])} contacted houses")
        print(f"Loaded {len(discarded_data['houses'])} discarded houses")
        print(f"Loaded {len(favorite_data['houses'])} favorite houses (before filtering)")
    except Exception as e:
        print(f"Error loading house states: {e}")
        # Initialize with empty data
        contacted_data = {"houses": set(), "by_id": {}}
        discarded_data = {"houses": set(), "by_id": {}}
        favorite_data = {"houses": set(), "by_id": {}}
    
    try:
        # Read the DataFrame from CSV (not Excel)
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

        # Flag to track if any Casa SAPO house IDs need regeneration
        regenerate_casa_sapo_ids = False
            
        # Add house_id to each house and check states
        for index, row in df.iterrows():
            house_data = row.to_dict()
            
            # Generate house ID if not already assigned
            house_name = house_data.get('Name', '')
            if house_name in house_ids:
                # Check if it's a Casa SAPO house that needs a UUID
                if house_data.get('Source') == 'Casa SAPO' and not house_ids[house_name].startswith(''):
                    # Regenerate ID using UUID for Casa SAPO houses
                    house_ids[house_name] = str(uuid.uuid4())[:10]
                    house_ids_updated = True
                    regenerate_casa_sapo_ids = True
                house_data['house_id'] = house_ids[house_name]
            else:
                # Generate new ID
                house_data['house_id'] = generate_house_id(house_data)
                house_ids[house_name] = house_data['house_id']
                house_ids_updated = True
            
            # Set initial states
            house_data['contacted'] = house_name in contacted_data['houses'] or house_data['house_id'] in contacted_data['by_id']
            house_data['discarded'] = house_name in discarded_data['houses'] or house_data['house_id'] in discarded_data['by_id']
            house_data['favorite'] = house_name in favorite_data['houses'] or house_data['house_id'] in favorite_data['by_id']
            
            # Update the DataFrame with the house_id
            df.at[index, 'house_id'] = house_data['house_id']
        
        # If we regenerated Casa SAPO IDs, update the state data
        if regenerate_casa_sapo_ids:
            # Update favorite_data, contacted_data, and discarded_data with new IDs
            update_states_with_new_ids(df, house_ids, favorite_data, contacted_data, discarded_data)
        
        # Deduplicate image URLs if available
        if 'Image URLs' in df.columns:
            df['Image URLs'] = df['Image URLs'].apply(deduplicate_image_urls)
        
        # Save updated house IDs
        if house_ids_updated:
            save_house_ids(house_ids)
            
        # Create a temporary column with house_ids for filtering
        df['temp_house_id'] = df['house_id']
            
        # Filter out discarded houses
        if len(discarded_data['houses']) > 0 or len(discarded_data['by_id']) > 0:
            discarded_houses = set(discarded_data['houses'])
            discarded_ids = set(discarded_data['by_id'].keys())
            
            # Filter out houses that are in either set
            df = df[~df['Name'].isin(discarded_houses) & ~df['temp_house_id'].isin(discarded_ids)]
            
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
        print(f"Error processing houses data: {e}")
        import traceback
        traceback.print_exc()
        return {"houses": [], "by_id": {}}, False, {}

def update_states_with_new_ids(df, house_ids, favorite_data, contacted_data, discarded_data):
    """Update the state data with new IDs"""
    print(f"Updating states with new IDs for Casa SAPO houses")
    
    # Create mapping of house names to new IDs
    name_to_id_map = {}
    for index, row in df.iterrows():
        if row.get('Source') == 'Casa SAPO':
            name = row.get('Name')
            house_id = row.get('house_id')
            if name and house_id:
                name_to_id_map[name] = house_id
    
    # Update favorite_data
    new_favorite_by_id = {}
    for name in favorite_data['houses']:
        if name in name_to_id_map:
            new_favorite_by_id[name_to_id_map[name]] = name
    favorite_data['by_id'].update(new_favorite_by_id)
    
    # Update contacted_data
    new_contacted_by_id = {}
    for name in contacted_data['houses']:
        if name in name_to_id_map:
            new_contacted_by_id[name_to_id_map[name]] = name
    contacted_data['by_id'].update(new_contacted_by_id)
    
    # Update discarded_data
    new_discarded_by_id = {}
    for name in discarded_data['houses']:
        if name in name_to_id_map:
            new_discarded_by_id[name_to_id_map[name]] = name
    discarded_data['by_id'].update(new_discarded_by_id)
    
    # Save updated state data
    save_favorite_houses(favorite_data)
    save_contacted_houses(contacted_data)
    save_discarded_houses(discarded_data)
    
    print(f"Updated states with new IDs for Casa SAPO houses")

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
        print(f"[DEBUG] Updated house IDs mapping, now contains {len(house_ids)} entries")
    
    return JSONResponse({"houses": houses})

@app.get("/sort/{column}")
async def sort_houses(column: str, order: str = "asc"):
    # Redirect to the new endpoint since sorting is now handled in frontend
    return await get_houses()

@app.get("/", response_class=HTMLResponse)
async def read_houses(
    request: Request, 
    sort_column: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    if not EXCEL_PATH.exists():
        return templates.TemplateResponse(
            "houses2.html",
            {
                "request": request,
                "houses": [],
                "sort_column": sort_column,
                "sort_order": sort_order,
                "houses_json": json.dumps([])
            }
        )
    
    # Use the common process_houses_data function
    houses, updated_ids, house_ids = process_houses_data(sort_column, sort_order)
    
    # Add HTML-specific debug messages
    favorite_count = sum(1 for house in houses if house['favorite'])
    for house in houses:
        if house['favorite']:
            print(f"[DEBUG] House marked as favorite in HTML template: {house['Name']} (ID: {house['house_id']})")
    
    print(f"[DEBUG] Total houses marked as favorites in HTML: {favorite_count} out of {len(houses)}")
    
    # Save the updated house IDs if any new ones were added
    if updated_ids:
        save_house_ids(house_ids)
        print(f"[DEBUG] Updated house IDs mapping, now contains {len(house_ids)} entries")
    
    return templates.TemplateResponse(
        "houses2.html",
        {
            "request": request,
            "houses": houses,
            "sort_column": sort_column,
            "sort_order": sort_order,
            "houses_json": json.dumps(houses)
        }
    )

@app.post("/toggle-contacted")
async def toggle_contacted(house_id: str):
    print(f"[DEBUG] Toggle contacted request for house ID: '{house_id}'")
    
    # Read current contacted houses directly from the JSON file
    if CONTACTED_PATH.exists():
        with open(CONTACTED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support both old format (list of house names) and new format (dict)
                if isinstance(data, list):
                    contacted_data = {"houses": set(data), "by_id": {}}
                    print(f"[DEBUG] Loaded contacted using old format: {len(contacted_data['houses'])} houses")
                else:
                    contacted_data = {
                        "houses": set(data.get("houses", [])), 
                        "by_id": data.get("by_id", {})
                    }
                    print(f"[DEBUG] Loaded contacted using new format: {len(contacted_data['houses'])} houses, {len(contacted_data['by_id'])} IDs")
            except Exception as e:
                print(f"[DEBUG] Error loading contacted: {str(e)}")
                contacted_data = {"houses": set(), "by_id": {}}
    else:
        contacted_data = {"houses": set(), "by_id": {}}
        print(f"[DEBUG] No contacted file found before toggle.")
    
    # Load house IDs mapping
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            house_ids = json.load(f)
    else:
        house_ids = {}
        
    # Find house name from ID
    house_name = get_house_name_from_id(house_id, house_ids)
    
    if not house_name:
        print(f"[DEBUG] House not found for ID: {house_id}")
        return JSONResponse({"error": f"House not found for ID: {house_id}", "contacted": False}, status_code=404)
    
    print(f"[DEBUG] Found house name: {house_name} for ID: {house_id}")
    
    # Check if the house is already in either by name or ID
    is_contacted_by_name = house_name in contacted_data["houses"]
    is_contacted_by_id = house_id in contacted_data["by_id"]
    
    print(f"[DEBUG] Is contacted by name: {is_contacted_by_name}, Is contacted by ID: {is_contacted_by_id}")
    
    # Toggle the contacted status
    if is_contacted_by_name or is_contacted_by_id:
        # Remove from both old and new data structures
        if is_contacted_by_name:
            contacted_data["houses"].remove(house_name)
            print(f"[DEBUG] Removed house from contacted (by name): '{house_name}'")
        if is_contacted_by_id:
            del contacted_data["by_id"][house_id]
            print(f"[DEBUG] Removed house from contacted (by ID): '{house_id}'")
        contacted = False
        print(f"[DEBUG] Removed house from contacted: '{house_name}' (ID: {house_id})")
    else:
        contacted_data["houses"].add(house_name)
        contacted_data["by_id"][house_id] = house_name
        contacted = True
        print(f"[DEBUG] Added house to contacted: '{house_name}' (ID: {house_id})")
    
    # Save changes to file
    save_contacted_houses(contacted_data)
    print(f"[DEBUG] Updated contacted after toggle. Now contains {len(contacted_data['houses'])} houses, {len(contacted_data['by_id'])} IDs")
    print(f"[DEBUG] Returning contacted={contacted}")
    
    return JSONResponse({"contacted": contacted})

@app.post("/toggle-discarded")
async def toggle_discarded(house_id: str):
    print(f"[DEBUG] Toggle discarded request for house ID: '{house_id}'")
    
    # Read current discarded houses directly from the JSON file
    if DISCARDED_PATH.exists():
        with open(DISCARDED_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support both old format (list of house names) and new format (dict)
                if isinstance(data, list):
                    discarded_data = {"houses": set(data), "by_id": {}}
                    print(f"[DEBUG] Loaded discarded using old format: {len(discarded_data['houses'])} houses")
                else:
                    discarded_data = {
                        "houses": set(data.get("houses", [])), 
                        "by_id": data.get("by_id", {})
                    }
                    print(f"[DEBUG] Loaded discarded using new format: {len(discarded_data['houses'])} houses, {len(discarded_data['by_id'])} IDs")
            except Exception as e:
                print(f"[DEBUG] Error loading discarded: {str(e)}")
                discarded_data = {"houses": set(), "by_id": {}}
    else:
        discarded_data = {"houses": set(), "by_id": {}}
        print(f"[DEBUG] No discarded file found before toggle.")
    
    # Load house IDs mapping
    if HOUSE_IDS_PATH.exists():
        with open(HOUSE_IDS_PATH, 'r', encoding='utf-8') as f:
            house_ids = json.load(f)
    else:
        house_ids = {}
        
    # Find house name from ID
    house_name = get_house_name_from_id(house_id, house_ids)
    
    if not house_name:
        print(f"[DEBUG] House not found for ID: {house_id}")
        return JSONResponse({"error": f"House not found for ID: {house_id}", "discarded": False}, status_code=404)
    
    print(f"[DEBUG] Found house name: {house_name} for ID: {house_id}")
    
    # Check if the house is already in either by name or ID
    is_discarded_by_name = house_name in discarded_data["houses"]
    is_discarded_by_id = house_id in discarded_data["by_id"]
    
    print(f"[DEBUG] Is discarded by name: {is_discarded_by_name}, Is discarded by ID: {is_discarded_by_id}")
    
    # Toggle the discarded status
    if is_discarded_by_name or is_discarded_by_id:
        # Remove from both old and new data structures
        if is_discarded_by_name:
            discarded_data["houses"].remove(house_name)
            print(f"[DEBUG] Removed house from discarded (by name): '{house_name}'")
        if is_discarded_by_id:
            del discarded_data["by_id"][house_id]
            print(f"[DEBUG] Removed house from discarded (by ID): '{house_id}'")
        discarded = False
        print(f"[DEBUG] Removed house from discarded: '{house_name}' (ID: {house_id})")
    else:
        discarded_data["houses"].add(house_name)
        discarded_data["by_id"][house_id] = house_name
        discarded = True
        print(f"[DEBUG] Added house to discarded: '{house_name}' (ID: {house_id})")
    
    # Save changes to file
    save_discarded_houses(discarded_data)
    print(f"[DEBUG] Updated discarded after toggle. Now contains {len(discarded_data['houses'])} houses, {len(discarded_data['by_id'])} IDs")
    print(f"[DEBUG] Returning discarded={discarded}")
    
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
    print(f"[DEBUG] Toggle favorite request for house ID: '{house_id}'")
    
    # Read current favorite houses directly from the JSON file
    if FAVORITES_PATH.exists():
        with open(FAVORITES_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Support both old format (list of house names) and new format (dict)
                if isinstance(data, list):
                    favorite_data = {"houses": set(data), "by_id": {}}
                    print(f"[DEBUG] Loaded favorites using old format: {len(favorite_data['houses'])} houses")
                else:
                    favorite_data = {
                        "houses": set(data.get("houses", [])), 
                        "by_id": data.get("by_id", {})
                    }
                    print(f"[DEBUG] Loaded favorites using new format: {len(favorite_data['houses'])} houses, {len(favorite_data['by_id'])} IDs")
            except Exception as e:
                print(f"[DEBUG] Error loading favorites: {str(e)}")
                favorite_data = {"houses": set(), "by_id": {}}
    else:
        favorite_data = {"houses": set(), "by_id": {}}
        print(f"[DEBUG] No favorites file found before toggle.")
    
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
    
    print(f"[DEBUG] Found house name: {house_name} for ID: {house_id}")
    
    # Toggle the favorite status
    if house_name in favorite_data["houses"] or house_id in favorite_data["by_id"]:
        # Remove from both old and new data structures
        if house_name in favorite_data["houses"]:
            favorite_data["houses"].remove(house_name)
        if house_id in favorite_data["by_id"]:
            del favorite_data["by_id"][house_id]
        favorite = False
        print(f"[DEBUG] Removed house from favorites: '{house_name}' (ID: {house_id})")
    else:
        favorite_data["houses"].add(house_name)
        favorite_data["by_id"][house_id] = house_name
        favorite = True
        print(f"[DEBUG] Added house to favorites: '{house_name}' (ID: {house_id})")
    
    # Save changes to file
    save_favorite_houses(favorite_data)
    print(f"[DEBUG] Updated favorites after toggle. Now contains {len(favorite_data['houses'])} houses.")
    
    return JSONResponse({"favorite": favorite}) 