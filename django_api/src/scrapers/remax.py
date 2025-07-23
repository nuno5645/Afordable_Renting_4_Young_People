from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager
from houses.models import House

class RemaxScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Remax"
        self.location_manager = LocationManager()
        self._load_existing_urls()

    def _extract_detail_page_data(self, url):
        """Extract additional data from property detail page"""
        try:
            # Create new driver for detail page
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            detail_driver = webdriver.Chrome(options=chrome_options)
            detail_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            detail_driver.get(url)
            time.sleep(2)
            detail_soup = BeautifulSoup(detail_driver.page_source, 'html.parser')
            
            # Extract description
            description = "N/A"
            desc_div = detail_soup.find('div', class_='text-sm lg:text-base leading-[170%] text-black text-left inline-block w-full')
            if desc_div:
                description = desc_div.get_text(strip=True)
            
            # Extract image URLs from detail page
            image_urls = []
            img_tags = detail_soup.find_all("img")
            for img in img_tags:
                img_url = img.get("src") or img.get("data-src")
                if img_url and 'maxwork.pt' in img_url and img_url not in image_urls:
                    image_urls.append(img_url)
            
            if not image_urls:
                image_urls = [""]  # fallback_image_url as per rules
            
            detail_driver.quit()
            return {"description": description, "image_urls": image_urls}
        except Exception as e:
            self._log('warning', f"Could not extract detail page data for {url}: {str(e)}")
            if 'detail_driver' in locals():
                detail_driver.quit()
            return {"description": "N/A", "image_urls": [""]}

    def scrape(self):
        """Scrape houses from Remax website"""
        for site_url in self.urls:
            self._process_url(site_url)

        self._log('info', "Finished processing all URLs")

    def _process_url(self, url):
        """Process a single Remax URL"""
        self._log('info', f"Starting scrape for URL: {url}")
        
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
            
            self._log('info', "Accessing website...")
            driver.get(url)
            
            # Scroll to trigger lazy loading
            for _ in range(6):
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                time.sleep(1)
            try: 
                # Wait for actual listing content
                WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id='listing-card-container']"))
                )
            except Exception as e:
                self._log('warning', f"Timeout waiting for listings container: {str(e)}")
                driver.quit()
                return

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self._log('info', "Successfully retrieved page content")

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait 5 seconds to allow dynamic content to load
            time.sleep(5)

            # Find all divs that have an ID starting with 'listing-list-card-'
            house_divs = soup.find_all(lambda tag: tag.name == 'div' and tag.get('id', '').startswith('listing-list-card-'))
            
            self._log('info', f"Found {len(house_divs)} houses to process")
            
            if not house_divs:
                self._log('warning', "No houses found. The website structure might have changed.")
                driver.quit()
                return

            for house_container in house_divs:
                try:
                    self._log('debug', f"Processing house with ID: {house_container.get('id')}")
                    
                    # Find the actual listing container inside the card
                    house = house_container.find('div', attrs={'data-id': 'listing-card-container'})
                    if not house:
                        self._log('warning', f"Could not find listing card container for ID: {house_container.get('id')}")
                        continue

                    # Extract house information with updated selectors
                    name = "N/A"
                    type_elem = house.find("b", class_="relative leading-[160%] truncate")
                    if type_elem and type_elem.text.strip() != "":
                        name = f"{type_elem.text.strip()} Remax"
                    else:
                        # Try alternative selector for property type
                        alt_div = house.find("div", class_="bg-lighter-blue")
                        if alt_div:
                            type_elem = alt_div.find("b")
                            if type_elem and type_elem.text.strip() != "":
                                name = f"{type_elem.text.strip()} Remax"
                    self._log('debug', f"Found property type: {name}")

                    zone = "N/A"
                    location_elem = house.find("div", class_="w-full relative leading-[170%]")
                    if location_elem and location_elem.find("p"):
                        zone = location_elem.find("p").text.strip()
                    else:
                        # Try alternative selector for location
                        location_elem = house.find("p", class_="w-full overflow-hidden text-ellipsis whitespace-nowrap")
                        if location_elem:
                            zone = location_elem.text.strip()
                    self._log('debug', f"Found location: {zone}")

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
                    self._log('debug', f"Found price: {price}")

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
                    self._log('debug', f"Found URL: {url}")

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
                                    
                    self._log('debug', f"Found bedrooms: {bedrooms}, area: {area}")

                    # Extract additional data from detail page
                    detail_data = self._extract_detail_page_data(url) if url != "N/A" else {"description": "N/A", "image_urls": [""]}
                    description = detail_data.get("description", "N/A")
                    image_urls = detail_data.get("image_urls", [""])
                    
                    # Skip listings with no location or price (likely ads or invalid listings)
                    if zone in ["N/A", "-"] or price in ["N/A", "0", "-"] or name in ["- Remax", "N/A"]:
                        self._log('warning', f"Skipping invalid listing - name: {name}, zone: {zone}, price: {price}")
                        continue
                    
                    # Extract freguesia and concelho
                    freguesia, concelho = self.location_manager.extract_location(zone)
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, Image URLs
                    info_list = [
                        name,           # Name
                        zone,           # Zone
                        price,          # Price
                        url,            # URL
                        bedrooms,       # Bedrooms
                        area,           # Area
                        "0",            # Floor (default to "0" as we don't have this info)
                        description,    # Description
                        freguesia if freguesia else "N/A",
                        concelho if concelho else "N/A",
                        "Remax",        # Source
                        None,           # ScrapedAt (will be filled by save_to_excel)
                        image_urls      # Image URLs as list
                    ]
                    
                    self._log('debug', f"Attempting to save listing: {info_list}")
                    self.save_to_database(info_list)
                    
                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                    continue

            # Close driver after all processing is done
            driver.quit()

        except Exception as e:
            self._log('error', f"Error accessing website: {str(e)}", exc_info=True)

    def _extract_location(self, zone):
        """Extract freguesia and concelho from the location string"""
        if " - " in zone:
            parts = zone.split(" - ")
            freguesia = parts[0].strip() if len(parts) > 0 else None
            concelho = parts[1].strip() if len(parts) > 1 else None
            return freguesia, concelho
        else:
            return None, None
