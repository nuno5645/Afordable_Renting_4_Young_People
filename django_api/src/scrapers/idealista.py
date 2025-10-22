from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager


class IdealistaScraper(BaseScraper):
    def __init__(self, logger, url, api_key, listing_type='rent'):
        super().__init__(logger, listing_type)
        # Convert single URL to list if needed
        self.url = [url] if isinstance(url, str) else url
        self.api_key = api_key
        self.source = "Idealista"
        self.last_run_file = "data/last_run_times.json"
        self.location_manager = LocationManager()
        self._load_existing_urls()


    def scrape(self):
        """Scrape houses from Idealista website"""
        for url_index, base_url in enumerate(self.url, 1):

            self._log('info', f"Processing URL {url_index}: {base_url}")
            
            # Process first page
            new_houses_on_page1 = self._process_page(1, base_url)

            # Only continue to page 2 if we found new houses on page 1 and haven't hit the request limit
            if new_houses_on_page1:
                self._log('info', "Processing page 2")
                self._process_page(2, base_url)
            elif not new_houses_on_page1:
                self._log('info', "No new houses found on page 1, skipping page 2")
            else:
                self._log('info', "Request limit reached, skipping page 2")

        self._log('info', "Finished processing all URLs")

    def _clean_image_url(self, img_url):
        """Clean up image URL by removing query parameters and normalizing"""
        if not img_url:
            return None
        
        # Remove query parameters
        if '?' in img_url:
            img_url = img_url.split('?')[0]
        
        # Handle srcset with multiple resolutions - take the highest resolution
        if ',' in img_url:
            # Split by comma and take the last (usually highest resolution) URL
            parts = img_url.split(',')
            for part in reversed(parts):
                part = part.strip()
                if part and ('http' in part):
                    img_url = part.split()[0]  # Take URL part, ignore resolution descriptor
                    break
        
        return img_url.strip()

    def _extract_gallery_images(self, house_element):
        """Extract all images from the property gallery on the listing page"""
        image_urls = []
        
        # Find the picture element with the gallery
        picture_elem = house_element.find('picture', class_='item-multimedia')
        if not picture_elem:
            self._log('warning', "No picture element with item-multimedia class found")
            return image_urls
        
        # Check if there's a gallery with multiple images
        gallery_container = picture_elem.find('div', class_='item-gallery')

        if not gallery_container:
            self._log('warning', "No item-gallery container found, trying to extract images directly from picture element")
            return image_urls
        
        # Get total number of images from the counter
        counter_spans = picture_elem.find_all('span')
        total_images = 1  # Default to 1 if we can't find the counter
        
        # Look for the image counter (e.g., "1/13")
        for span in counter_spans:
            span_text = span.get_text().strip()
            if '/' in span_text:
                try:
                    total_images = int(span_text.split('/')[-1])
                    self._log('info', f"Found {total_images} total images in gallery counter")
                    break
                except (ValueError, IndexError):
                    pass
        
        # Get current slide image
        current_slide = gallery_container.find('div', class_='image-gallery-slide center')
        if current_slide:
            img = current_slide.find('img')
            if img and img.get('src'):
                img_url = self._clean_image_url(img.get('src'))
                if img_url and img_url not in image_urls:
                    image_urls.append(img_url)
                    self._log('debug', f"Added image: {img_url}")
        
        # Click through remaining images using next button
        next_button = picture_elem.find('button', class_='image-gallery-right-nav')
        if next_button and total_images > 1:
            for i in range(1, total_images):
                try:
                    # Re-parse to get updated slide
                    soup = BeautifulSoup(picture_elem.prettify(), 'html.parser')
                    current_slide = soup.find('div', class_='image-gallery-slide center')
                    if current_slide:
                        img = current_slide.find('img')
                        if img and img.get('src'):
                            img_url = self._clean_image_url(img.get('src'))
                            if img_url and img_url not in image_urls:
                                image_urls.append(img_url)
                                self._log('debug', f"Added image {i+1}: {img_url}")
                except Exception as e:
                    self._log('warning', f"Error extracting image {i+1}: {str(e)}")
                    break
        return image_urls

    def _process_page(self, page_num, base_url):
        """Process a single page of listings"""

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

        driver = None
        try:
            self._log('info', f"Processing page {page_num}...")
           
           
            # Use Chrome driver like Casa SAPO
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-dev-tools')
            chrome_options.add_argument('--mute-audio')
            chrome_options.add_argument('--no-first-run')
            chrome_options.add_argument('--no-default-browser-check')
            chrome_options.add_argument('--password-store=basic')
            chrome_options.add_argument('--use-gl=swiftshader')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option('prefs', {
                'profile.managed_default_content_settings.images': 2,  # Don't load images
                'disk-cache-size': 4096,  # Minimal disk cache
                'profile.password_manager_enabled': False,
                'profile.default_content_settings.popups': 0,
                'download_restrictions': 3  # No downloads
            })
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                '''
            })
            
            self._log('info', "Chrome driver initialized successfully")
            driver.get(current_url)
            self._log('info', f"Navigated to URL: {current_url}")
            time.sleep(3)  # Wait for page to load
            
            # Get page content
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")
            self._log('info', "Successfully parsed page content with BeautifulSoup")

            houses = soup.find_all("article", class_="item")
            self._log('info', f"Found {len(houses)} house listings on page {page_num}")

            if not houses:
                self._log('warning', f"No houses found on page {page_num}")
                driver.quit()
                return

            # Track if any new houses were processed
            new_houses_found = False
            
            self._log('info', f"Starting to process {len(houses)} houses...")
            
            for house_idx, house in enumerate(houses, 1):
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

                    # Extract image URLs from the gallery
                    image_urls = self._extract_gallery_images(house)
                    
                    # Log image extraction results
                    if image_urls:
                        self._log('info', f"[House {house_idx}/{len(houses)}] Successfully extracted {len(image_urls)} image(s) for property: {name if name else 'N/A'}")
                    else:
                        self._log('warning', f"[House {house_idx}/{len(houses)}] No images found for property: {name if name else 'N/A'}")

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
                    parish_id, county_id, district_id = self.location_manager.extract_location(zone)
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Parish_ID, County_ID, District_ID, Source, ScrapedAt, Image URLs
                    info_list = [
                        name,
                        zone,
                        price,
                        url,
                        bedrooms,
                        area,
                        floor,
                        description,
                        parish_id,      # Parish ID
                        county_id,      # County ID
                        district_id,    # District ID
                        "Idealista",
                        None,  # ScrapedAt will be filled by save_to_excel
                        image_urls  # Add image URLs as the last column
                    ]

                    self._log('info', f"[House {house_idx}/{len(houses)}] Saving property to database...")
                    self.save_to_database(info_list)

                except Exception as e:
                    self._log('error', f"[House {house_idx}/{len(houses)}] ✗ ERROR processing house: {str(e)}")
                    import traceback
                    self._log('error', f"Traceback: {traceback.format_exc()}")
                    continue

            self._log('info', f"Finished processing all {len(houses)} houses on page {page_num}")
            self._log('info', f"New houses found: {new_houses_found}")
            
            # Close driver
            self._log('info', "Closing Chrome driver...")
            driver.quit()
            self._log('info', "Chrome driver closed successfully")
            
            # Return whether new houses were found
            return new_houses_found

        except Exception as e:
            self._log('error', f"✗ CRITICAL ERROR processing page {page_num}: {str(e)}")
            import traceback
            self._log('error', f"Traceback: {traceback.format_exc()}")
            if driver:
                try:
                    self._log('info', "Attempting to close driver after error...")
                    driver.quit()
                    self._log('info', "Driver closed after error")
                except Exception as cleanup_error:
                    self._log('error', f"Error closing driver: {str(cleanup_error)}")
            return False
