from abc import ABC, abstractmethod
import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path
import json
from config.settings import (
    WHATSAPP_GROUP_ID, 
    WHATSAPP_NOTIFICATION_ENABLED, 
    EXCEL_HEADERS,
    NTFY_TOPIC,
    NTFY_NOTIFICATION_ENABLED,
    NTFY_PRICE_THRESHOLD,
    NTFY_FILTER_ROOM_RENTALS,
    ROOM_RENTAL_TITLE_TERMS,
    ROOM_RENTAL_DESCRIPTION_TERMS
)
from openpyxl.styles import PatternFill
import csv
from src.messenger.ntfy_sender import NtfySender

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
        # Create scraper_status directory
        self.status_dir = self.data_dir / 'scraper_status'
        self.status_dir.mkdir(exist_ok=True)
        self.excel_file = self.data_dir / 'houses.xlsx'
        # Initialize ntfy sender if enabled
        self.ntfy_sender = NtfySender(topic=NTFY_TOPIC, logger=logger) if NTFY_NOTIFICATION_ENABLED else None
        # Price threshold for notifications
        self.price_threshold = NTFY_PRICE_THRESHOLD

    def _initialize_status(self):
        """Initialize the status file after source has been set by child class"""
        self.status_file = self.status_dir / f'{self.source.lower()}_status.json'
        self._update_status("initialized")

    def _log(self, level, message, **kwargs):
        """Wrapper for logging that adds the scraper tag"""
        tagged_message = f"[{self.source}] {message}"
        if hasattr(self.logger, level):
            log_method = getattr(self.logger, level)
            log_method(tagged_message, **kwargs)

    def _update_status(self, status, error_message=None):
        """Update the scraper's status in its dedicated JSON file, maintaining history"""
        try:
            if not hasattr(self, 'status_file'):
                self._initialize_status()

            # Read existing history or create new
            history = []
            if os.path.exists(self.status_file):
                try:
                    with open(self.status_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            history = json.loads(content)
                            if not isinstance(history, list):
                                history = []
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    self._log('warning', f"Could not read status history, starting fresh: {str(e)}")
                    history = []

            # Add new status entry
            status_entry = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'houses_processed': self.houses_processed,
                'houses_found': self.houses_found,
                'error_message': error_message
            }
            
            # Add to beginning of list (most recent first)
            history.insert(0, status_entry)
            
            # Keep only last 100 entries to prevent file from growing too large
            history = history[:100]
            
            # Write with proper encoding and ensure directory exists
            self.status_dir.mkdir(exist_ok=True)
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self._log('error', f"Error updating status: {str(e)}", exc_info=True)

    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by each website scraper"""
        pass

    def run(self):
        """Wrapper method to handle scraping with status updates"""
        try:
            self._update_status("running")
            self.scrape()
            self._update_status("completed")
        except Exception as e:
            error_message = str(e)
            self._update_status("failed", error_message)
            raise

    def _clean_price(self, price_str):
        """Convert price string to integer by removing currency symbols and non-numeric characters"""
        try:
            # Remove currency symbols, dots, spaces and other non-numeric characters
            cleaned = ''.join(c for c in price_str if c.isdigit())
            return int(cleaned) if cleaned else 0
        except Exception as e:
            self._log('error', f"Error converting price: {str(e)}", exc_info=True)
            return 0

    def save_to_excel(self, info_list):
        """Save house information to CSV file"""
        try:
            # Use Path for proper path handling
            csv_file = self.data_dir / 'houses.csv'
            
            # Read existing CSV file or create new DataFrame if file doesn't exist
            try:
                if csv_file.exists():
                    try:
                        # First attempt with standard settings
                        df = pd.read_csv(csv_file, dtype=str, quoting=csv.QUOTE_ALL, escapechar='\\')
                    except Exception as e:
                        self._log('warning', f"Error reading CSV, attempting fallback: {str(e)}")
                        try:
                            # Second attempt with error handling
                            df = pd.read_csv(csv_file, dtype=str, on_bad_lines='skip')
                            self._log('info', "Used fallback CSV reading with skipping bad lines")
                        except Exception as e2:
                            self._log('error', f"CSV reading failed completely: {str(e2)}")
                            # Create a new DataFrame as last resort
                            df = pd.DataFrame(columns=EXCEL_HEADERS)
                            self._log('warning', "Created new DataFrame due to CSV read errors")
                else:
                    df = pd.DataFrame(columns=EXCEL_HEADERS)
            except Exception as e:
                self._log('error', f"Error reading CSV: {str(e)}", exc_info=True)
                df = pd.DataFrame(columns=EXCEL_HEADERS)
            
            url = str(info_list[3]).strip() if len(info_list) > 3 and info_list[3] is not None else ''  # Ensure URL is string and stripped
            self.houses_processed += 1
            
            # Check if house already exists (case-insensitive)
            if not any(existing_url.lower() == url.lower() for existing_url in df['URL'].fillna('')):
                self.houses_found += 1
                
                # Create a clean dictionary with all expected fields
                new_house_data = dict.fromkeys(EXCEL_HEADERS)
                
                # Clean and prepare the data
                name = str(info_list[0]).strip() if len(info_list) > 0 and info_list[0] is not None else ''
                zone = str(info_list[1]).strip() if len(info_list) > 1 and info_list[1] is not None else ''
                price = str(info_list[2]).strip() if len(info_list) > 2 and info_list[2] is not None else ''
                price_clean = self._clean_price(price)
                
                # Update the dictionary with cleaned values
                min_length = min(len(info_list), len(EXCEL_HEADERS))
                for i in range(min_length):
                    value = info_list[i]
                    # Clean the value - remove control characters that might cause CSV issues
                    if value is not None:
                        value = str(value).strip()
                        # Replace control characters with spaces
                        value = ''.join(ch if ord(ch) >= 32 or ch in '\n\r\t' else ' ' for ch in value)
                    else:
                        value = ''
                    new_house_data[EXCEL_HEADERS[i]] = value
                
                # Override price with cleaned integer
                new_house_data[EXCEL_HEADERS[2]] = price_clean
                
                self._log('info', f"New listing found: {name} in {zone} - {price_clean}", extra={'action': 'SAVING'})
                
                # Send notification if price is below threshold
                if price_clean > 0 and price_clean <= self.price_threshold:
                    # Check if we should filter room rentals
                    is_room_rental = False
                    
                    if NTFY_FILTER_ROOM_RENTALS:
                        # Check if the listing is for a room rental by looking for common room rental terms
                        name_upper = name.upper()
                        is_room_rental = any(name_upper.startswith(term) for term in ROOM_RENTAL_TITLE_TERMS)
                        
                        # Also check if the description contains room rental indicators
                        description_text = str(info_list[7]).upper() if len(info_list) > 7 and info_list[7] is not None else ""
                        is_room_rental = is_room_rental or any(indicator in description_text for indicator in ROOM_RENTAL_DESCRIPTION_TERMS)
                    
                    if is_room_rental:
                        self._log('info', f"Skipping notification for room rental: {name}", extra={'action': 'SKIP_NOTIFICATION'})
                    else:
                        # Extract additional information for notification
                        bedrooms = info_list[4] if len(info_list) > 4 and info_list[4] is not None else 'N/A'
                        area = info_list[5] if len(info_list) > 5 and info_list[5] is not None else 'N/A'
                        floor = info_list[6] if len(info_list) > 6 and info_list[6] is not None else 'N/A'
                        description = info_list[7] if len(info_list) > 7 and info_list[7] is not None else 'N/A'
                        freguesia = info_list[8] if len(info_list) > 8 and info_list[8] is not None else 'N/A'
                        concelho = info_list[9] if len(info_list) > 9 and info_list[9] is not None else 'N/A'
                        
                        # Create a location string combining freguesia and concelho if available
                        location = zone
                        if freguesia != 'N/A' and concelho != 'N/A':
                            location = f"{freguesia}, {concelho}"
                        elif freguesia != 'N/A':
                            location = freguesia
                        elif concelho != 'N/A':
                            location = concelho
                        
                        self._send_notification(
                            name=name, 
                            zone=location, 
                            price=price_clean, 
                            url=url, 
                            bedrooms=bedrooms, 
                            area=area,
                            floor=floor,
                            description=description
                        )
                
                # Create new row and append to DataFrame
                new_row = pd.DataFrame([new_house_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Save to CSV with proper quoting and escaping
                try:
                    # Create a backup before saving
                    if csv_file.exists():
                        backup_file = csv_file.with_suffix('.csv.bak')
                        csv_file.rename(backup_file)
                    
                    # Save with robust error handling
                    df.to_csv(csv_file, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL, escapechar='\\')
                    
                    # Remove backup if save was successful
                    if 'backup_file' in locals() and backup_file.exists():
                        backup_file.unlink()
                        
                except Exception as save_error:
                    self._log('error', f"Error saving to CSV: {str(save_error)}", exc_info=True)
                    # Restore from backup if save failed
                    if 'backup_file' in locals() and backup_file.exists() and not csv_file.exists():
                        backup_file.rename(csv_file)
                        self._log('info', "Restored original CSV from backup after save error")
                
                return True
            return False
            
        except Exception as e:
            self._log('error', f"Error in save_to_excel: {str(e)}", exc_info=True)
            return False
            
    def _send_notification(self, name, zone, price, url, bedrooms='N/A', area='N/A', floor='N/A', description='N/A'):
        """Send notification for houses under the price threshold"""
        try:
            # Skip if notifications are disabled or ntfy_sender is not initialized
            if not NTFY_NOTIFICATION_ENABLED or self.ntfy_sender is None:
                return
                
            # Format the message with emoji and better structure
            message = (
                f"💰 *{price}€* - Affordable House!\n\n"
                f"🏠 *{name}*\n"
                f"📍 {zone}\n"
            )
            
            # Add optional details if available
            if bedrooms != 'N/A':
                message += f"🛏️ {bedrooms} bedroom(s)\n"
            if area != 'N/A':
                message += f"📐 {area}\n"
            if floor != 'N/A' and floor:
                message += f"🏢 Floor: {floor}\n"
                
            # Add description (truncated if too long)
            if description != 'N/A' and description:
                # Truncate description if it's too long (max 100 chars)
                desc_text = description
                if len(desc_text) > 100:
                    desc_text = desc_text[:97] + "..."
                message += f"\n📝 {desc_text}\n"
                
            # Add source
            message += f"\n🔎 *Source:* {self.source}"
            
            # Add timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message += f"\n⏱️ Found: {current_time}"
            
            # message += f"\n\n🔗 *View Property:*\n{url}"
            
            # Create view action button
            view_action = f"view, View Property, {url}"
            
            # Send notification via ntfy.sh
            self.ntfy_sender.send_notification(
                message=message,
                title=f"€{price} | {name}",
                priority="high",
                tags=["house", "money", "bell"],
                click=url,  # Make the entire notification clickable
                actions=[view_action]  # Add a view button
            )
            
            self._log('info', f"Sent notification for affordable house: {price}€ in {zone}")
        except Exception as e:
            self._log('error', f"Error sending notification: {str(e)}", exc_info=True)
