from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import json
from pathlib import Path
from typing import Optional
import csv

app = FastAPI(title="Houses API")

# Setup templates directory
templates = Jinja2Templates(directory="api/templates")

# File paths
EXCEL_PATH = Path("data/houses.csv")
CONTACTED_PATH = Path("data/contacted_houses.json")
DISCARDED_PATH = Path("data/discarded_houses.json")

def load_contacted_houses():
    """Load contacted houses from JSON file, create if doesn't exist"""
    if CONTACTED_PATH.exists():
        with open(CONTACTED_PATH, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_contacted_houses(contacted_houses):
    """Save contacted houses to JSON file"""
    with open(CONTACTED_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(contacted_houses), f, ensure_ascii=False, indent=2)

def load_discarded_houses():
    """Load discarded houses from JSON file, create if doesn't exist"""
    if DISCARDED_PATH.exists():
        with open(DISCARDED_PATH, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_discarded_houses(discarded_houses):
    """Save discarded houses to JSON file"""
    with open(DISCARDED_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(discarded_houses), f, ensure_ascii=False, indent=2)

# Initialize houses from files
contacted_houses = load_contacted_houses()
discarded_houses = load_discarded_houses()

@app.get("/sort/{column}")
async def sort_houses(column: str, order: str = "asc"):
    if not EXCEL_PATH.exists():
        return JSONResponse({"error": "Houses data file not found"})
    
    print(EXCEL_PATH)
    
    df = pd.read_csv(EXCEL_PATH, 
                    quoting=csv.QUOTE_ALL, 
                    escapechar='\\',
                    lineterminator='\n',
                    on_bad_lines='warn')
    
    # Filter out discarded houses
    df = df[~df['Name'].isin(discarded_houses)]
    
    #remove all non-numeric characters from the column and convert to int
    df[column] = df[column].astype(str).str.replace(r'[^0-9]', '', regex=True).astype(int)
    
    # Convert price to numbers by removing currency symbols and converting to float
    if column == 'Price':
        # Keep only numbers
        df[column] = (
            df[column]
            .astype(str)
            .str.replace(r'[^0-9]', '', regex=True)  # Remove non-numeric characters
        )

        # Drop rows where the column is empty after cleaning
        df = df[df[column] != '']

        # Convert the column to integers
        df[column] = df[column].astype(int)

        # Sort the DataFrame by the column
        ascending = order == "asc"
        df = df.sort_values(column, ascending=ascending, na_position='last')

    elif column == 'Area':
        df['Area'] = df['Area'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
    elif column == 'Bedrooms':
        # Extract just the number from bedroom strings (e.g., "T2" -> 2)
        df['Bedrooms'] = df['Bedrooms'].astype(str).str.extract(r'(\d+)').astype(float)
    
    # Sort dataframe
    ascending = order == "asc"
    df = df.sort_values(column, ascending=ascending, na_position='last')
    
    # Convert to records and handle NA values
    houses = df.replace({pd.NA: None}).to_dict('records')
    
    # Add contacted and discarded state to each house
    for house in houses:
        house['contacted'] = house['Name'] in contacted_houses
        house['discarded'] = house['Name'] in discarded_houses
        # Ensure price is an integer
        if 'Price' in house and house['Price'] is not None:
            house['Price'] = int(house['Price'])
    
    return JSONResponse({"houses": houses})

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
    
    df = pd.read_csv(EXCEL_PATH, 
                    quoting=csv.QUOTE_ALL, 
                    escapechar='\\',
                    lineterminator='\n',
                    on_bad_lines='warn')
    
    # Filter out discarded houses
    df = df[~df['Name'].isin(discarded_houses)]
    
    # Convert and sort data if needed
    if sort_column:
        if sort_column == 'Price':
            df['Price'] = df['Price'].replace('', pd.NA)
            mask = df['Price'].notna()
            df.loc[mask, 'Price'] = df.loc[mask, 'Price'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        elif sort_column == 'Area':
            df['Area'] = df['Area'].replace('', pd.NA)
            mask = df['Area'].notna()
            df.loc[mask, 'Area'] = df.loc[mask, 'Area'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
        elif sort_column == 'Bedrooms':
            df['Bedrooms'] = df['Bedrooms'].replace('', pd.NA)
            mask = df['Bedrooms'].notna()
            df.loc[mask, 'Bedrooms'] = df.loc[mask, 'Bedrooms'].astype(str).str.extract(r'(\d+)').astype(float)
        
        ascending = sort_order == "asc"
        df = df.sort_values(sort_column, ascending=ascending, na_position='last')
    
    # Ensure price is properly formatted
    if 'Price' in df.columns:
        # Replace empty strings with NaN first
        df['Price'] = df['Price'].replace('', pd.NA)
        # Only convert non-NA values
        mask = df['Price'].notna()
        df.loc[mask, 'Price'] = df.loc[mask, 'Price'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float).astype(int)
    
    houses = df.replace({pd.NA: None}).to_dict('records')
    
    # Add contacted and discarded state to each house
    for house in houses:
        house['contacted'] = house['Name'] in contacted_houses
        house['discarded'] = house['Name'] in discarded_houses
    
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

@app.post("/toggle-contacted/{house_name}")
async def toggle_contacted(house_name: str):
    global contacted_houses
    
    if house_name in contacted_houses:
        contacted_houses.remove(house_name)
        contacted = False
    else:
        contacted_houses.add(house_name)
        contacted = True
    
    # Save changes to file
    save_contacted_houses(contacted_houses)
    
    return JSONResponse({"contacted": contacted})

@app.post("/toggle-discarded/{house_name}")
async def toggle_discarded(house_name: str):
    global discarded_houses
    
    if house_name in discarded_houses:
        discarded_houses.remove(house_name)
        discarded = False
    else:
        discarded_houses.add(house_name)
        discarded = True
    
    # Save changes to file
    save_discarded_houses(discarded_houses)
    
    return JSONResponse({"discarded": discarded}) 