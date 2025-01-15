from abc import ABC, abstractmethod
import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path
# Commenting out WhatsApp functionality as it's not suitable for headless environments
# from src.whatsapp_sender import WhatsAppSender
from config.settings import WHATSAPP_GROUP_ID, WHATSAPP_NOTIFICATION_ENABLED, EXCEL_HEADERS
from openpyxl.styles import PatternFill

class BaseScraper(ABC):
    def __init__(self, logger):
        self.logger = logger
        # Commenting out WhatsApp initialization
        # self.whatsapp = WhatsAppSender() if WHATSAPP_NOTIFICATION_ENABLED else None
        self.houses_processed = 0
        self.houses_found = 0
        self.source = "Unknown"  # Default source, should be overridden by child classes
        # Create data directory if it doesn't exist
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.excel_file = self.data_dir / 'houses.xlsx'

    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by each website scraper"""
        pass

    def _clean_price(self, price_str):
        """Convert price string to integer by removing currency symbols and non-numeric characters"""
        try:
            # Remove currency symbols, dots, spaces and other non-numeric characters
            cleaned = ''.join(c for c in price_str if c.isdigit())
            return int(cleaned) if cleaned else 0
        except Exception as e:
            self.logger.error(f"Error converting price: {str(e)}", exc_info=True)
            return 0

    def save_to_excel(self, info_list):
        """Save house information to CSV file"""
        try:
            # Use Path for proper path handling
            csv_file = self.data_dir / 'houses.csv'
            
            # Read existing CSV file or create new DataFrame if file doesn't exist
            try:
                df = pd.read_csv(csv_file, dtype=str)  # Read all columns as strings initially
            except FileNotFoundError:
                df = pd.DataFrame(columns=EXCEL_HEADERS)
            
            url = str(info_list[3]).strip()  # Ensure URL is string and stripped
            self.houses_processed += 1
            
            # Check if house already exists (case-insensitive)
            if not df['URL'].str.lower().str.contains(url.lower(), na=False).any():
                self.houses_found += 1
                
                # Create a clean dictionary with all expected fields
                new_house_data = dict.fromkeys(EXCEL_HEADERS)
                
                # Clean and prepare the data
                name, zone, price = [str(x).strip() if x is not None else '' for x in info_list[0:3]]
                price_clean = self._clean_price(price)
                
                # Update the dictionary with cleaned values
                min_length = min(len(info_list), len(EXCEL_HEADERS))
                for i in range(min_length):
                    new_house_data[EXCEL_HEADERS[i]] = str(info_list[i]).strip() if info_list[i] is not None else ''
                
                # Override price with cleaned integer
                new_house_data[EXCEL_HEADERS[2]] = price_clean
                
                # Add source and timestamp
                new_house_data[EXCEL_HEADERS[-2]] = self.source
                new_house_data[EXCEL_HEADERS[-1]] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.logger.info(f"New listing found: {name} in {zone} - {price_clean}", extra={'action': 'SAVING'})
                
                # Create new row and append to DataFrame
                new_row = pd.DataFrame([new_house_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Save to CSV with proper encoding
                df.to_csv(csv_file, index=False, encoding='utf-8')
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}", exc_info=True)
            return False
