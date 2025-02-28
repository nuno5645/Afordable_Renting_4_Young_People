from abc import ABC, abstractmethod
import pandas as pd
import logging
from datetime import datetime
import os
from pathlib import Path
import json
from config.settings import (
    EXCEL_HEADERS,
    NTFY_TOPIC,
    NTFY_NOTIFICATION_ENABLED,
    NTFY_PRICE_THRESHOLD,
    NTFY_FILTER_ROOM_RENTALS,
    ROOM_RENTAL_TITLE_TERMS,
    ROOM_RENTAL_DESCRIPTION_TERMS
)
import csv
from src.messenger.ntfy_sender import NtfySender
from houses.models import House, ScraperRun
import uuid
from django.utils import timezone
from decimal import Decimal, InvalidOperation

class BaseScraper(ABC):
    def __init__(self, logger):
        self.logger = logger
        # Commenting out WhatsApp initialization
        # self.whatsapp = WhatsAppSender() if WHATSAPP_NOTIFICATION_ENABLED else None
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
        # Initialize scraper run
        self.current_run = None
        # Initialize existing URLs set
        self.existing_urls = set()

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

    def _initialize_run(self):
        """Initialize a new scraper run"""
        # Get or create the Scraper object
        
        # Create the ScraperRun object
        self.current_run = ScraperRun.objects.create(
            scraper=self.source,
            status='initialized'
        )
        self._log('info', f"Initialized new scraper run: {self.current_run.id}")
        
    def _start_run(self):
        """Mark the current run as started"""
        if self.current_run:
            self.current_run.status = 'running'
            self.current_run.save()
            
    def _complete_run(self):
        """Mark the current run as completed"""
        if self.current_run:
            self.current_run.status = 'completed'
            self.current_run.end_time = timezone.now()
            self.current_run.save()
            
    def _fail_run(self, error_message):
        """Mark the current run as failed"""
        if self.current_run:
            self.current_run.status = 'failed'
            self.current_run.end_time = timezone.now()
            self.current_run.error_message = error_message
            self.current_run.save()

    def _clean_price(self, price_str):
        """Clean and convert price string to Decimal"""
        if not price_str:
            return Decimal('0')
        
        try:
            # Remove currency symbols, spaces, and monthly suffix
            cleaned = str(price_str).replace('€', '')\
                                  .replace(' ', '')\
                                  .replace('/mês', '')\
                                  .replace('/mes', '')
            
            # Handle decimal numbers (both with . and ,)
            if ',' in cleaned and '.' in cleaned:
                # If both . and , exist, assume European format (1.234,56)
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif '.' in cleaned:
                # If only dot exists and it's a thousands separator (e.g., 1.000)
                if len(cleaned.split('.')[-1]) != 2:  # Not cents (e.g., not 1.50)
                    cleaned = cleaned.replace('.', '')
            elif ',' in cleaned:
                # If only comma exists, treat it as decimal separator
                cleaned = cleaned.replace(',', '.')
            
            # Remove any remaining non-numeric characters except decimal point
            cleaned = ''.join(c for c in cleaned if c.isdigit() or c == '.')
            
            if not cleaned:
                return Decimal('0')
            
            # Convert to Decimal
            price = Decimal(cleaned)
            
            # If price is less than 100, assume it's thousands (e.g., 1.15 means 1150)
            if price < 100:
                price = price * 1000
            
            return price
            
        except (InvalidOperation, ValueError) as e:
            self._log('warning', f"Error converting price '{price_str}': {str(e)}")
            return Decimal('0')

    def _send_notification(self, name, zone, price, url, bedrooms='N/A', area='N/A', floor='N/A', description='N/A'):
        """Send notification for houses under the price threshold"""
        try:
            if not NTFY_NOTIFICATION_ENABLED or self.ntfy_sender is None or price > self.price_threshold:
                return

            # Check if it's a room rental
            if NTFY_FILTER_ROOM_RENTALS:
                name_upper = name.upper()
                if any(name_upper.startswith(term) for term in ROOM_RENTAL_TITLE_TERMS):
                    return
                if description != 'N/A':
                    desc_upper = description.upper()
                    if any(term in desc_upper for term in ROOM_RENTAL_DESCRIPTION_TERMS):
                        return

            message = (
                f"💰 *{price}€* - New Affordable House!\n\n"
                f"🏠 *{name}*\n"
                f"📍 {zone}\n"
            )
            
            if bedrooms != 'N/A':
                message += f"🛏️ {bedrooms}\n"
            if area != 'N/A':
                message += f"📐 {area}\n"
            if floor != 'N/A':
                message += f"🏢 Floor: {floor}\n"
            
            if description != 'N/A':
                desc_text = description[:100] + "..." if len(description) > 100 else description
                message += f"\n📝 {desc_text}\n"
            
            message += f"\n🔎 Source: {self.source}"
            
            self.ntfy_sender.send_notification(
                message=message,
                title=f"€{price} | {name}",
                priority="high",
                tags=["house", "money", "bell"],
                click=url
            )
            
        except Exception as e:
            self._log('error', f"Error sending notification: {str(e)}")

    def save_to_database(self, info_list):
        """Save house information to database"""
        try:
            # Extract and clean data
            name = str(info_list[0]).strip() if len(info_list) > 0 and info_list[0] is not None else ''
            zone = str(info_list[1]).strip() if len(info_list) > 1 and info_list[1] is not None else ''
            price_str = str(info_list[2]).strip() if len(info_list) > 2 and info_list[2] is not None else '0'
            url = str(info_list[3]).strip() if len(info_list) > 3 and info_list[3] is not None else ''
            bedrooms = str(info_list[4]).strip() if len(info_list) > 4 and info_list[4] is not None else ''
            area_str = str(info_list[5]).strip() if len(info_list) > 5 and info_list[5] is not None else '0'
            floor = str(info_list[6]).strip() if len(info_list) > 6 and info_list[6] is not None else ''
            description = str(info_list[7]).strip() if len(info_list) > 7 and info_list[7] is not None else ''
            freguesia = str(info_list[8]).strip() if len(info_list) > 8 and info_list[8] is not None else ''
            concelho = str(info_list[9]).strip() if len(info_list) > 9 and info_list[9] is not None else ''
            source = str(info_list[10]).strip() if len(info_list) > 10 and info_list[10] is not None else self.source
            image_urls = json.loads(info_list[11]) if len(info_list) > 11 and info_list[11] is not None else []

            # Clean price and area
            price = self._clean_price(price_str)
            try:
                area = Decimal(''.join(c for c in area_str if c.isdigit() or c == '.'))
            except:
                area = Decimal('0')

            # Generate house_id
            house_id = str(uuid.uuid4())[:20]

            # Check if house already exists by URL
            if not House.objects.filter(url__iexact=url).exists():
                # Create new house
                house = House.objects.create(
                    name=name,
                    zone=zone,
                    price=price,
                    url=url,
                    bedrooms=bedrooms,
                    area=area,
                    floor=floor if floor and floor != 'N/A' else None,
                    description=description,
                    freguesia=freguesia,
                    concelho=concelho,
                    source=source,
                    scraped_at=timezone.now(),
                    image_urls=image_urls,
                    house_id=house_id
                )
                
                self._log('info', f"New listing found: {name} in {zone} - {price}€")
                
                # Send notification if price is below threshold
                if price > 0 and price <= self.price_threshold:
                    self._send_notification(
                        name=name,
                        zone=zone,
                        price=price,
                        url=url,
                        bedrooms=bedrooms,
                        area=area_str,
                        floor=floor,
                        description=description
                    )
                
                return True
            return False
            
        except Exception as e:
            self._log('error', f"Error saving to database: {str(e)}", exc_info=True)
            return False

    def run(self):
        """Run the scraper - must be implemented by child classes"""
        try:
            # Initialize run if not already initialized
            if not self.current_run:
                self._initialize_run()
            
            # Load existing URLs before starting
            self._load_existing_urls()
            
            self._start_run()
            self.scrape()
            self._complete_run()
        except Exception as e:
            error_message = str(e)
            self._fail_run(error_message)
            raise

    def _load_existing_urls(self):
        """Load existing property URLs from the database to avoid duplicates"""
        self.existing_urls = set()
        try:
            # Get all URLs from the House model where source matches the scraper's source
            urls = House.objects.filter(source=self.source).values_list('url', flat=True)
            self.existing_urls = set(urls)
            self._log('info', f"Loaded {len(self.existing_urls)} existing property URLs from database")
        except Exception as e:
            self._log('warning', f"Error loading existing URLs: {str(e)}")
            # Continue with an empty set if there was an error
            self.existing_urls = set()

    def url_exists(self, url):
        """Check if a URL already exists in the database and update counters
        Args:
            url (str): The URL to check
        Returns:
            bool: True if the URL exists, False otherwise
        """
        # Increment total houses counter since we're checking a house
        if self.current_run:
            self.current_run.total_houses += 1
            self.current_run.save()

        exists = url in self.existing_urls
        
        # If it's a new house (doesn't exist), increment new_houses counter
        if not exists and self.current_run:
            self.current_run.new_houses += 1
            self.current_run.save()
            
        return exists
