import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
from src.utils.base_scraper import BaseScraper
from config.settings import IDEALISTA_MAX_REQUESTS_PER_HOUR


class IdealistaScraper(BaseScraper):
    def __init__(self, logger, url, api_key):
        super().__init__(logger)
        self.url = url
        self.api_key = api_key
        self.source = "Idealista"
        self.last_run_file = "data/last_run_times.json"
        self._load_request_history()

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
            self.logger.error(f"Error loading request history: {str(e)}")
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
            self.logger.error(f"Error saving request history: {str(e)}")

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
        total_processed = 0
        total_new_listings = 0

        for url_index, base_url in enumerate(self.url, 1):
            if not self.can_make_request():
                self.logger.info(
                    f"Reached maximum requests per hour ({IDEALISTA_MAX_REQUESTS_PER_HOUR}), waiting for next hour",
                    extra={"action": "PROCESSING"},
                )
                break

            self.logger.info(
                f"Processing URL {url_index}: {base_url}",
                extra={"action": "PROCESSING"},
            )
            
            # Process first page
            processed, new_listings = self._process_page(1, base_url)
            total_processed += processed
            total_new_listings += new_listings

            # Only continue to page 2 if we found more than 30 listings on page 1
            # and we haven't hit the request limit
            if processed > 30 and self.can_make_request():
                self.logger.info(
                    "Found more than 30 listings, processing page 2",
                    extra={"action": "PROCESSING"},
                )
                processed_page2, new_listings_page2 = self._process_page(2, base_url)
                total_processed += processed_page2
                total_new_listings += new_listings_page2
            else:
                if not self.can_make_request():
                    self.logger.info(
                        "Request limit reached, skipping page 2",
                        extra={"action": "PROCESSING"},
                    )
                else:
                    self.logger.info(
                        f"Only found {processed} listings, skipping page 2",
                        extra={"action": "PROCESSING"},
                    )

        self.logger.info(
            f"Finished processing all URLs for Idealista",
            extra={"action": "PROCESSING"},
        )
        self.logger.info(
            f"Total houses processed: {total_processed}", extra={"action": "PROCESSING"}
        )
        self.logger.info(
            f"Total new listings found: {total_new_listings}",
            extra={"action": "PROCESSING"},
        )

    def _process_page(self, page_num, base_url):
        """Process a single page of listings"""
        if not self.can_make_request():
            return 0, 0

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

        self.logger.info(
            f"Constructed URL for page {page_num}: {current_url}",
            extra={"action": "PROCESSING"},
        )

        try:
            self.logger.info(
                f"Processing page {page_num}...", extra={"action": "SCRAPING"}
            )
            if page_num > 1:
                self.logger.info(
                    "Waiting 10 seconds before next request...",
                    extra={"action": "PROCESSING"},
                )
                time.sleep(10)  # Wait between pages

            payload = {"api_key": self.api_key, "url": current_url, "autoparse": "true"}
            self.logger.info(
                "Making request to ScraperAPI...", extra={"action": "SCRAPING"}
            )
            
            # Track the request before making it
            self.track_request()
            r = requests.get("https://api.scraperapi.com/", params=payload)
            
            self.logger.info(
                f"ScraperAPI response status code: {r.status_code}",
                extra={"action": "PROCESSING"},
            )

            if r.status_code != 200:
                self.logger.error(
                    f"Failed to get page. Status code: {r.status_code}",
                    extra={"action": "SCRAPING"},
                )
                self.logger.error(
                    f"Response content: {r.text[:500]}...", extra={"action": "SCRAPING"}
                )
                return 0, 0

            soup = BeautifulSoup(r.text, "html.parser")
            self.logger.info(
                "Successfully parsed page content with BeautifulSoup",
                extra={"action": "PROCESSING"},
            )

            houses = soup.find_all("article", class_="item")
            self.logger.info(
                f"Found {len(houses)} house listings on page {page_num}",
                extra={"action": "PROCESSING"},
            )

            if not houses:
                self.logger.warning(
                    f"No houses found on page {page_num}",
                    extra={"action": "PROCESSING"},
                )
                return 0, 0

            processed = 0
            new_listings = 0

            for house in houses:
                try:
                    processed += 1

                    title_link = house.find("a", class_="item-link")
                    if not title_link:
                        continue

                    name = title_link.get("title", "N/A")
                    url = f"https://www.idealista.pt{title_link.get('href', '')}"

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

                    desc_elem = house.find("div", class_="item-description")
                    description = desc_elem.text.strip() if desc_elem else "N/A"

                    info_list = [name, zone, price, url, bedrooms, area, floor, description]

                    if self.save_to_excel(info_list):
                        new_listings += 1

                except Exception as e:
                    self.logger.error(
                        f"Error processing house: {str(e)}", exc_info=True
                    )
                    continue

            return processed, new_listings

        except Exception as e:
            self.logger.error(
                f"Error processing page {page_num}: {str(e)}", exc_info=True
            )
            return 0, 0
