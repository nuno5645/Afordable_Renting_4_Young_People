import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
from src.utils.base_scraper import BaseScraper
from src.utils.location_manager import LocationManager
from config.settings import IDEALISTA_MAX_REQUESTS_PER_HOUR
from houses.models import House


class IdealistaScraper(BaseScraper):
    def __init__(self, logger, url, api_key):
        super().__init__(logger)
        # Convert single URL to list if needed
        self.url = [url] if isinstance(url, str) else url
        self.api_key = api_key
        self.source = "Idealista"
        self.last_run_file = "data/last_run_times.json"
        self.location_manager = LocationManager()
        self._load_request_history()
        self._load_existing_urls()

    def _load_existing_urls(self):
        """Load existing property URLs from the database to avoid duplicates"""
        self.existing_urls = set()
        try:
            # Get all URLs from the House model where source is Idealista
            urls = House.objects.filter(source="Idealista").values_list('url', flat=True)
            self.existing_urls = set(urls)
            self._log('info', f"Loaded {len(self.existing_urls)} existing property URLs from database")
        except Exception as e:
            self._log('warning', f"Error loading existing URLs: {str(e)}")
            # Continue with an empty set if there was an error
            self.existing_urls = set()

    def _load_request_history(self):
        """Load the request history from JSON file"""
        try:
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    data = json.load(f)
                    history = data.get('idealista_requests', [])
                    # Convert string timestamps to datetime objects and filter last hour
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    self.request_history = [
                        datetime.fromisoformat(ts) for ts in history
                        if datetime.fromisoformat(ts) > one_hour_ago
                    ]
            else:
                self.request_history = []
        except Exception as e:
            self._log('error', f"Error loading request history: {str(e)}")
            self.request_history = []

    def _save_request_history(self):
        """Save the request history to JSON file"""
        try:
            data = {}
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    data = json.load(f)
            
            # Only keep timestamps from the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            self.request_history = [ts for ts in self.request_history if ts > one_hour_ago]
            
            # Convert datetime objects to ISO format strings
            data['idealista_requests'] = [ts.isoformat() for ts in self.request_history]
            
            with open(self.last_run_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self._log('error', f"Error saving request history: {str(e)}")

    def can_make_request(self):
        """Check if we can make another request within the hourly limit"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        # Filter requests from the last hour
        self.request_history = [ts for ts in self.request_history if ts > one_hour_ago]
        return len(self.request_history) < IDEALISTA_MAX_REQUESTS_PER_HOUR

    def track_request(self):
        """Track a new request"""
        self.request_history.append(datetime.now())
        self._save_request_history()

    def scrape(self):
        """Scrape houses from Idealista website"""
        for url_index, base_url in enumerate(self.url, 1):
            if not self.can_make_request():
                self._log('info', f"Reached maximum requests per hour ({IDEALISTA_MAX_REQUESTS_PER_HOUR}), waiting for next hour")
                break

            self._log('info', f"Processing URL {url_index}: {base_url}")
            
            # Process first page
            new_houses_on_page1 = self._process_page(1, base_url)

            # Only continue to page 2 if we found new houses on page 1 and haven't hit the request limit
            if new_houses_on_page1 and self.can_make_request():
                self._log('info', "Processing page 2")
                self._process_page(2, base_url)
            elif not new_houses_on_page1:
                self._log('info', "No new houses found on page 1, skipping page 2")
            else:
                self._log('info', "Request limit reached, skipping page 2")

        self._log('info', "Finished processing all URLs")

    def _process_page(self, page_num, base_url):
        """Process a single page of listings"""
        if not self.can_make_request():
            return

        if page_num == 1:
            current_url = base_url
        else:
            if "pagina-" not in base_url:
                # Add a trailing slash if it doesn't exist
                if not base_url.endswith('/'):
                    base_url += '/'
                current_url = base_url + f"pagina-{page_num}/"
            else:
                current_url = base_url.replace(
                    f"pagina-{page_num-1}", f"pagina-{page_num}"
                )

        self._log('info', f"Constructed URL for page {page_num}: {current_url}")

        try:
            self._log('info', f"Processing page {page_num}...")
           
            payload = {"api_key": self.api_key, "url": current_url, "autoparse": "true"}
            self._log('info', "Making request to ScraperAPI...")
            
            # Track the request before making it
            self.track_request()
            r = requests.get("https://api.scraperapi.com/", params=payload)
            
            self._log('info', f"ScraperAPI response status code: {r.status_code}")

            if r.status_code != 200:
                self._log('error', f"Failed to get page. Status code: {r.status_code}")
                self._log('error', f"Response content: {r.text[:500]}...")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            self._log('info', "Successfully parsed page content with BeautifulSoup")

            houses = soup.find_all("article", class_="item")
            self._log('info', f"Found {len(houses)} house listings on page {page_num}")

            if not houses:
                self._log('warning', f"No houses found on page {page_num}")
                return

            # Track if any new houses were processed
            new_houses_found = False
            
            for house in houses:
                try:
                    title_link = house.find("a", class_="item-link")
                    if not title_link:
                        continue
                    
                    if self.current_run:
                        self.current_run.total_houses += 1
                        self.current_run.save()

                    name = title_link.get("title", "N/A")
                    url = f"https://www.idealista.pt{title_link.get('href', '')}"
                    
                    # Skip if URL already exists in the database
                    if self.url_exists(url):
                        self._log('info', f"Skipping already processed property: {url}")
                        continue

                    # If we get here, we found at least one new house
                    new_houses_found = True
                    
                    price_elem = house.find("span", class_="item-price")
                    price = price_elem.text.strip() if price_elem else "N/A"

                    details = house.find_all("span", class_="item-detail")
                    bedrooms = details[0].text.strip() if len(details) > 0 else "N/A"
                    area = (
                        details[1].text.strip().replace(" área bruta", "")
                        if len(details) > 1
                        else "N/A"
                    )
                    
                    # Extract floor directly from item-detail
                    floor = "N/A"
                    for detail in details:
                        if "andar" in detail.text.lower():
                            floor = detail.text.strip()
                            break

                    # Extract image URLs
                    image_urls = []
                    picture_elem = house.find('picture')
                    if picture_elem:
                        # Try to get webp source first
                        webp_source = picture_elem.find('source', type='image/webp')
                        if webp_source and webp_source.get('srcset'):
                            image_urls.append(webp_source.get('srcset'))
                        # Fallback to jpg source
                        jpg_source = picture_elem.find('source', type='image/jpeg')
                        if jpg_source and jpg_source.get('srcset'):
                            image_urls.append(jpg_source.get('srcset'))
                        # Final fallback to img tag
                        img = picture_elem.find('img')
                        if img and img.get('src') and not img.get('src').endswith('.gif'):
                            image_urls.append(img.get('src'))

                    zone_elem = house.find("a", class_="item-link")
                    if zone_elem and zone_elem.get("title"):
                        zone_words = zone_elem["title"].split()
                        try:
                            location_start = (
                                zone_words.index("em")
                                if "em" in zone_words
                                else zone_words.index("na")
                            )
                            zone = " ".join(zone_words[location_start + 1 :])
                        except ValueError:
                            zone = "N/A"
                    else:
                        zone = "N/A"

                    # Get description from item-description div
                    description_elem = house.find("div", class_="item-description")
                    description = description_elem.text.strip() if description_elem else "N/A"

                    # Extract freguesia and concelho
                    freguesia, concelho = self.location_manager.extract_location(zone)
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, Image URLs
                    info_list = [
                        name,
                        zone,
                        price,
                        url,
                        bedrooms,
                        area,
                        floor,
                        description,
                        freguesia if freguesia else "N/A",
                        concelho if concelho else "N/A",
                        "Idealista",
                        None,  # ScrapedAt will be filled by save_to_excel
                        json.dumps(image_urls)  # Add image URLs as the last column
                    ]

                    self.save_to_database(info_list)

                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                    continue

            # Return whether new houses were found
            return new_houses_found

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return False
