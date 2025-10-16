from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime
from pathlib import Path
try:
    from config.settings import (
        EXCEL_HEADERS,
        NTFY_TOPIC,
        NTFY_NOTIFICATION_ENABLED,
        NTFY_PRICE_THRESHOLD,
        NTFY_FILTER_ROOM_RENTALS,
        ROOM_RENTAL_TITLE_TERMS,
        ROOM_RENTAL_DESCRIPTION_TERMS
    )
    from src.messenger.ntfy_sender import NtfySender
except ImportError:
    # Fallback for relative imports
    import sys
    from pathlib import Path
    
    # Add parent directories to path if not already there
    current_dir = Path(__file__).parent.parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from config.settings import (
        EXCEL_HEADERS,
        NTFY_TOPIC,
        NTFY_NOTIFICATION_ENABLED,
        NTFY_PRICE_THRESHOLD,
        NTFY_FILTER_ROOM_RENTALS,
        ROOM_RENTAL_TITLE_TERMS,
        ROOM_RENTAL_DESCRIPTION_TERMS
    )
    from messenger.ntfy_sender import NtfySender
import csv
from houses.models import House, ScraperRun
import uuid
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import time
import random
import threading

# Create a global lock for database operations
db_lock = threading.Lock()

class BaseScraper(ABC):
    def __init__(self, logger):
        # Store the ScraperLogger instance directly
        if hasattr(logger, 'logger'):
            # It's a ScraperLogger instance
            self.logger = logger
        else:
            # It's a regular logger, wrap it
            from utils.logger import ScraperLogger
            self.logger = ScraperLogger(f"house_scrapers.{self.__class__.__name__}")
        # Commenting out WhatsApp 
        # self.whatsapp = WhatsAppSender() if WHATSAPP_NOTIFICATION_ENABLED else None
        self.source = "Unknown"  # Default source, should be overridden by child classes
        # Create data directory if it doesn't exist
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.excel_file = self.data_dir / 'houses.xlsx'
        # Initialize ntfy sender if enabled
        self.ntfy_sender = NtfySender(topic=NTFY_TOPIC, logger=logger) if NTFY_NOTIFICATION_ENABLED else None
        # Price threshold for notifications
        self.price_threshold = NTFY_PRICE_THRESHOLD
        # Initialize scraper run
        self.current_run = None
        self.main_run = None
        # Initialize existing URLs set
        self.existing_urls = set()



    def _log(self, level, message, **kwargs):
        """Wrapper for logging that adds the scraper tag and uses color coding"""
        tagged_message = f"[{self.source}] {message}"
        
        # Map common log levels to colored methods
        if level == 'info':
            self.logger.info(tagged_message, **kwargs)
        elif level == 'warning':
            self.logger.warning(tagged_message, **kwargs)
        elif level == 'error':
            self.logger.error(tagged_message, **kwargs)
        elif level == 'debug':
            self.logger.debug(tagged_message, **kwargs)
        else:
            # For specific action levels, use the colored methods
            if level == 'scraping':
                self.logger.scraping(tagged_message, **kwargs)
            elif level == 'processing':
                self.logger.processing(tagged_message, **kwargs)
            elif level == 'saving':
                self.logger.saving(tagged_message, **kwargs)
            elif level == 'loading':
                self.logger.loading(tagged_message, **kwargs)
            elif level == 'initializing':
                self.logger.initializing(tagged_message, **kwargs)
            elif level == 'filtering':
                self.logger.filtering(tagged_message, **kwargs)
            elif level == 'analyzing':
                self.logger.analyzing(tagged_message, **kwargs)
            else:
                # Fallback to info
                self.logger.info(tagged_message, **kwargs)

    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by each website scraper"""
        pass

    def set_main_run(self, main_run):
        """Set the main run for this scraper instance"""
        self.main_run = main_run

    def _initialize_run(self):
        """Initialize a new scraper run"""
        if not self.main_run:
            raise ValueError("Main run must be set before initializing a scraper run")
            
        # Use lock for database operations
        with db_lock:
            # Create the ScraperRun object
            self.current_run = ScraperRun.objects.create(
                scraper=self.source,
                status='initialized',
                main_run=self.main_run
            )
            self._log('initializing', f"Initialized new scraper run: {self.current_run.id}")
        
    def _start_run(self):
        """Mark the current run as started"""
        if self.current_run:
            with db_lock:
                self.current_run.status = 'running'
                self.current_run.save()
            
    def _complete_run(self):
        """Mark the current run as completed"""
        if self.current_run:
            with db_lock:
                self.current_run.status = 'completed'
                self.current_run.end_time = timezone.now()
                self.current_run.save()
            
    def _fail_run(self, error_message):
        """Mark the current run as failed"""
        if self.current_run:
            with db_lock:
                self.current_run.status = 'failed'
                self.current_run.error_message = error_message
                self.current_run.end_time = timezone.now()
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
                click=url,
                actions=[f"view, View Property, {url}"]
            )
            
        except Exception as e:
            self._log('error', f"Error sending notification: {str(e)}")

    def save_to_database(self, info_list):
        """Save house information to database"""
        
        self._log('debug', f"Saving house information to database: {info_list}")
        
        try:
            # Extract and clean data
            name = str(info_list[0]).strip() if len(info_list) > 0 and info_list[0] is not None else ''
            zone = str(info_list[1]).strip() if len(info_list) > 1 and info_list[1] is not None else ''
            price_str = str(info_list[2]).strip() if len(info_list) > 2 and info_list[2] is not None else '0'
            url = str(info_list[3]).strip() if len(info_list) > 3 and info_list[3] is not None else ''
            bedrooms = str(info_list[4]).strip() if len(info_list) > 4 and info_list[4] is not None else ''
            area = str(info_list[5]).strip() if len(info_list) > 5 and info_list[5] is not None else '0'
            floor = str(info_list[6]).strip() if len(info_list) > 6 and info_list[6] is not None else ''
            description = str(info_list[7]).strip() if len(info_list) > 7 and info_list[7] is not None else ''
            parish_id = info_list[8] if len(info_list) > 8 and info_list[8] is not None else None
            county_id = info_list[9] if len(info_list) > 9 and info_list[9] is not None else None
            district_id = info_list[10] if len(info_list) > 10 and info_list[10] is not None else None
            source = str(info_list[11]).strip() if len(info_list) > 11 and info_list[11] is not None else self.source
            # Get image URLs - ensure it's a list
            image_urls = info_list[13] if len(info_list) > 13 and info_list[13] is not None else info_list[12] if len(info_list) > 12 and info_list[12] is not None else []
            # Clean price and area
            price = self._clean_price(price_str)
            area = area.replace('m²', '').strip()

            # Generate house_id
            house_id = str(uuid.uuid4())[:20]

            # Normalize URL to handle /pt/ and /hpr/pt/ variations for Imovirtual
            normalized_url = url
            if 'imovirtual.com' in url:
                normalized_url = url.replace('/hpr/pt/', '/pt/')

            self._log('debug', f"[IMAGE_DEBUG] Image URLs to save: {image_urls}")

            # Use lock for database operations
            with db_lock:
                # Check if house already exists by URL (using normalized URL)
                if not House.objects.filter(url__iexact=normalized_url).exists():
                    # Update counters when we actually find and save a new house
                    if self.current_run:
                        self.current_run.new_houses += 1
                        self.current_run.save()

                    # Create new house
                    house = House(
                        name=name,
                        zone=zone,
                        price=price,
                        url=normalized_url,  # Use normalized URL
                        bedrooms=bedrooms,
                        area=area,
                        floor=floor if floor and floor != 'N/A' else None,
                        description=description,
                        parish_id=parish_id,
                        county_id=county_id,
                        district_id=district_id,
                        source=source,
                        scraped_at=timezone.now(),
                        house_id=house_id
                    )
                    
                    self._log('debug', f"House object: {house}")
                    
                    # Save the house
                    house.save()

                    # Save Photo objects for each image URL
                    for idx, img_url in enumerate(image_urls):
                        if img_url:
                            house.photos.create(image_url=img_url, order=idx)
                    
                    self._log('scraping', f"New listing found: {name} in {zone} - {price}€")
                    
                    # Send notification if price is below threshold
                    if price > 0 and price <= self.price_threshold:
                        self._send_notification(
                            name=name,
                            zone=zone,
                            price=price,
                            url=url,
                            bedrooms=bedrooms,
                            area=area,
                            floor=floor,
                            description=description
                        )
                    
                    return True
                return False
            
        except Exception as e:
            self._log('error', f"Error saving to database: {str(e)}")

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
            
            # Normalize URLs for Imovirtual
            normalized_urls = []
            for url in urls:
                if 'imovirtual.com' in url:
                    normalized_urls.append(url.replace('/hpr/pt/', '/pt/'))
                else:
                    normalized_urls.append(url)
                    
            self.existing_urls = set(normalized_urls)
            self._log('loading', f"Loaded {len(self.existing_urls)} existing property URLs from database")
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
        # Normalize URL to handle /pt/ and /hpr/pt/ variations for Imovirtual
        normalized_url = url
        if 'imovirtual.com' in url:
            normalized_url = url.replace('/hpr/pt/', '/pt/')

        return normalized_url in self.existing_urls
