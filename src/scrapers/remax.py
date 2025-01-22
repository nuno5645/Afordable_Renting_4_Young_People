from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from src.utils.base_scraper import BaseScraper

class RemaxScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Remax"

    def scrape(self):
        """Scrape houses from Remax website"""
        total_processed = 0
        total_new_listings = 0

        for site_url in self.urls:
            processed, new_listings = self._process_url(site_url)
            total_processed += processed
            total_new_listings += new_listings

        self.logger.info(f"Finished processing all Remax URLs", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total houses processed: {total_processed}", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total new listings found: {total_new_listings}", extra={'action': 'PROCESSING'})

    def _process_url(self, url):
        """Process a single Remax URL"""
        self.logger.info(f"Starting scrape for Remax URL: {url}", extra={'action': 'SCRAPING'})
        
        try:
            # Configure Chrome with anti-bot detection
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("Accessing website...", extra={'action': 'SCRAPING'})
            driver.get(url)
            time.sleep(30)  # Fixed 30-second wait for page load

            # Wait for the listings container to be present
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id='listing-card-container']"))
                )
            except Exception as e:
                self.logger.warning(f"Timeout waiting for listings container: {str(e)}")
                driver.quit()
                return 0, 0

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self.logger.info("Successfully retrieved page content", extra={'action': 'PROCESSING'})

            driver.quit()

            # Find all divs that have an ID starting with 'listing-list-card-'
            house_divs = soup.find_all(lambda tag: tag.name == 'div' and tag.get('id', '').startswith('listing-list-card-'))
            
            self.logger.info(f"Found {len(house_divs)} houses to process", extra={'action': 'PROCESSING'})
            
            if not house_divs:
                self.logger.warning("No houses found. The website structure might have changed.")
                return 0, 0

            processed = 0
            new_listings = 0

            for house_container in house_divs:
                try:
                    processed += 1
                    self.logger.debug(f"Processing house with ID: {house_container.get('id')}", extra={'action': 'DEBUG'})
                    
                    # Find the actual listing container inside the card
                    house = house_container.find('div', attrs={'data-id': 'listing-card-container'})
                    if not house:
                        self.logger.warning(f"Could not find listing card container for ID: {house_container.get('id')}", extra={'action': 'DEBUG'})
                        continue

                    # Extract house information with updated selectors
                    name = "N/A"
                    type_elem = house.find("b", class_="relative leading-[160%] truncate")
                    if type_elem and type_elem.text.strip() != "":
                        name = f"{type_elem.text.strip()} Remax"
                    else:
                        # Try alternative selector for property type
                        type_elem = house.find("div", class_="bg-lighter-blue").find("b")
                        if type_elem and type_elem.text.strip() != "":
                            name = f"{type_elem.text.strip()} Remax"
                    self.logger.info(f"Found property type: {name}", extra={'action': 'DEBUG'})

                    zone = "N/A"
                    location_elem = house.find("div", class_="w-full relative leading-[170%]")
                    if location_elem and location_elem.find("p"):
                        zone = location_elem.find("p").text.strip()
                    else:
                        # Try alternative selector for location
                        location_elem = house.find("p", class_="w-full overflow-hidden text-ellipsis whitespace-nowrap")
                        if location_elem:
                            zone = location_elem.text.strip()
                    self.logger.info(f"Found location: {zone}", extra={'action': 'DEBUG'})

                    price = "N/A"
                    price_elem = house.find("b", class_="relative leading-[140%]")
                    if price_elem:
                        price_text = price_elem.text.strip()
                        # Extract just the numeric price value
                        if "€" in price_text:
                            price = price_text.split("/")[0].strip().replace(" ", "")
                    else:
                        # Try alternative selector for price
                        price_elem = house.find("span", class_="")
                        if price_elem and "€" in price_elem.text:
                            price = price_elem.text.strip().split("/")[0].strip().replace(" ", "")
                    self.logger.info(f"Found price: {price}", extra={'action': 'DEBUG'})

                    url = "N/A"
                    # First try finding the link in the immediate parent
                    link_elem = house.find_parent("a", attrs={"data-id": "listing-card-link"})
                    if not link_elem:
                        # If not found, try searching in the entire card container
                        link_elem = house.find("a", attrs={"data-id": "listing-card-link"})
                        if not link_elem:
                            # Try finding any parent a tag with href
                            link_elem = house.find_parent("a", href=True)
                    if link_elem and 'href' in link_elem.attrs:
                        url = f"https://www.remax.pt{link_elem['href']}"
                    self.logger.info(f"Found URL: {url}", extra={'action': 'DEBUG'})

                    bedrooms = "N/A"
                    area = "N/A"
                    features_div = house.find("div", class_="flex flex-row items-start justify-start gap-[0rem_0.75rem]")
                    if features_div:
                        # Find all feature items with their icons
                        feature_items = features_div.find_all("div", class_="flex flex-row items-center justify-start gap-[0rem_0.25rem]")
                        for item in feature_items:
                            value_elem = item.find("b", class_="relative leading-[160%] whitespace-nowrap")
                            if not value_elem:
                                continue
                            
                            value = value_elem.text.strip()
                            if not value:
                                continue

                            # Check icon to determine feature type
                            icon = item.find("svg")
                            if icon:
                                icon_path = icon.find("path")
                                if icon_path:
                                    path_d = icon_path.get("d", "")
                                    # Area icon (house icon)
                                    if "m8.597.732" in path_d or any(keyword in path_d for keyword in ["house", "home"]):
                                        area = value
                                    # Bedrooms icon (bed icon)
                                    elif ".742 4.943" in path_d or any(keyword in path_d for keyword in ["bed", "room"]):
                                        bedrooms = f"T{value}"
                                    # Bathrooms icon
                                    elif ".51 2.5" in path_d or "bath" in path_d:
                                        pass  # Can add bathroom info if needed
                            else:
                                # Fallback: try to identify by text content
                                if "m²" in value:
                                    area = value
                                elif value.isdigit():
                                    bedrooms = f"T{value}"
                    
                    self.logger.info(f"Found bedrooms: {bedrooms}, area: {area}", extra={'action': 'DEBUG'})

                    description = "N/A"  # Remax doesn't show description in listing cards
                    
                    # Skip listings with no location or price (likely ads or invalid listings)
                    if zone in ["N/A", "-"] or price in ["N/A", "0", "-"] or name in ["- Remax", "N/A"]:
                        self.logger.warning(f"Skipping invalid listing - name: {name}, zone: {zone}, price: {price}", extra={'action': 'DEBUG'})
                        continue
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Source, ScrapedAt
                    info_list = [
                        name,           # Name
                        zone,           # Zone
                        price,          # Price
                        url,            # URL
                        bedrooms,       # Bedrooms
                        area,           # Area
                        "0",            # Floor (default to "0" as we don't have this info)
                        description,    # Description
                        "Remax",        # Source
                        None           # ScrapedAt (will be filled by save_to_excel)
                    ]
                    
                    self.logger.info(f"Attempting to save listing: {info_list}", extra={'action': 'DEBUG'})
                    save_result = self.save_to_excel(info_list)
                    self.logger.info(f"Save result: {save_result}", extra={'action': 'DEBUG'})
                    
                    if save_result:
                        new_listings += 1
                        self.logger.info(f"Successfully saved new listing", extra={'action': 'DEBUG'})
                    else:
                        self.logger.info(f"Listing was not saved (possibly duplicate)", extra={'action': 'DEBUG'})
                    
                except Exception as e:
                    self.logger.error(f"Error processing house: {str(e)}", exc_info=True)
                    continue

            return processed, new_listings

        except Exception as e:
            self.logger.error(f"Error accessing website: {str(e)}", exc_info=True)
            return 0, 0
