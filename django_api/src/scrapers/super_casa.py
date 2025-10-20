from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager
import os
import json
import re

class SuperCasaScraper(BaseScraper):
    def __init__(self, logger, urls, listing_type='rent'):
        super().__init__(logger, listing_type)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "SuperCasa"
        self.location_manager = LocationManager()
        self.driver = None  # Reusable driver instance
        self._load_existing_urls()

    def run(self):
        """Run the scraper with proper initialization and status handling"""
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
        finally:
            # Always cleanup driver
            if self.driver:
                try:
                    self.driver.quit()
                    self._log('info', "Chrome driver closed successfully")
                except Exception as e:
                    self._log('warning', f"Error closing driver: {str(e)}")

    def scrape(self):
        """Scrape houses from SuperCasa website"""
        try:
            # Create driver once for all URLs
            self.driver = self._create_driver()
            
            for site_url in self.urls:
                self._log('info', f"Starting scrape for URL: {site_url}")
                page_num = 1
                max_pages = 50  # Increased safety limit, but pagination check will stop before this

                while page_num <= max_pages:
                    if not self._process_page(site_url, page_num):
                        self._log('info', f"Stopping at page {page_num} - no more pages or no new listings found")
                        break
                    self._log('info', f"Successfully processed page {page_num}, moving to next page")
                    page_num += 1

            self._log('info', "Finished processing all pages")
        except Exception as e:
            self._log('error', f"Error during scraping: {str(e)}")
            raise
    
    def _create_driver(self):
        """Create and configure Chrome driver once"""
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
        return driver

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            # Insert pagination before query parameters
            # Split URL at the '?' to separate base URL from query params
            if '?' in url:
                base_url, query_params = url.split('?', 1)
                current_url = f"{base_url}/pagina-{page_num}?{query_params}"
            else:
                # No query params, just append pagination
                if url.endswith('/'):
                    current_url = f"{url}pagina-{page_num}"
                else:
                    current_url = f"{url}/pagina-{page_num}"

        try:
            self._log('info', f"Processing page {page_num}...")
            if page_num > 1:
                time.sleep(random.uniform(3, 6))  # Random wait between pages (3-6 seconds)
                
            self.driver.get(current_url)
            self._log('info', f"Navigated to URL: {current_url}")

            # Wait for property listings to be present (explicit wait instead of sleep)
            try:
                property_items = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.list-properties > .property"))
                )
                self._log('info', f"Found {len(property_items)} property items")
            except Exception as e:
                self._log('warning', f"No property items found on page {page_num}: {str(e)}")
                return False

            found_new_listing = True

            for property_item in property_items:
                try:
                    if self.current_run:
                        self.current_run.total_houses += 1
                        self.current_run.save()
                    # Get URL first to check if already processed
                    url_elem = property_item.find_element(By.CLASS_NAME, "property-link")
                    url = url_elem.get_attribute("href")
                    
                    # If URL is relative, convert to absolute URL
                    if url and url.startswith('/'):
                        url = f"https://supercasa.pt{url}"
                    
                    # Skip if URL already exists in our database
                    if self.url_exists(url):
                        # self._log('info', f"Skipping already processed property: {url}")
                        continue
                    
                    found_new_listing = True
                    
                    # Extract property information
                    try:
                        name = property_item.find_element(By.CLASS_NAME, "property-list-title").text.strip()
                    except:
                        name = "N/A"
                        
                    try:
                        title_elem = property_item.find_element(By.CSS_SELECTOR, ".property-list-title a")
                        title_text = title_elem.get_attribute("title")
                        # Extract T0, T1, T2, etc. from the title
                        bedrooms_match = re.search(r'(T\d+)', title_text) if title_text else None
                        bedrooms = bedrooms_match.group(1) if bedrooms_match else "N/A"
                    except:
                        bedrooms = "N/A"
                        
                    # Get the full title which contains location information
                    try:
                        title_elem = property_item.find_element(By.CLASS_NAME, "property-link")
                        zone_attr = title_elem.get_attribute("title")
                        zone = zone_attr.strip() if zone_attr else "N/A"
                    except:
                        zone = "N/A"
                        
                    # Extract parish, county and district IDs from address
                    parish_id, county_id, district_id = self.location_manager.extract_location(zone)
                    
                    try:
                        price_elem = property_item.find_element(By.CSS_SELECTOR, ".property-price span")
                        price = price_elem.text.strip()
                    except:
                        price = "N/A"
                        
                    # Get area from property-features spans
                    try:
                        feature_spans = property_item.find_elements(By.CSS_SELECTOR, ".property-features span")
                        area_span = next((span.text for span in feature_spans if "m²" in span.text), None)
                        if area_span:
                            match = re.search(r'(\d+)', area_span)
                            area = match.group(1) if match else "0"
                        else:
                            area = "0"
                    except:
                        area = "0"
                        
                    # Get floor (if available)
                    floor = "N/A"  # SuperCasa typically doesn't show floor information in listings
                    
                    # Get description
                    try:
                        description = property_item.find_element(By.CLASS_NAME, "property-description-text").text.strip()
                    except:
                        description = "N/A"
                        
                    # Get image URLs - simplified and faster
                    image_urls = []
                    try:
                        # Find swiper container in the property
                        swiper_container = property_item.find_element(By.CSS_SELECTOR, ".property-media.swiper-container")
                        
                        # Scroll to the swiper container with human-like behavior
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", swiper_container)
                        
                        # Wait briefly for initial image
                        WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".swiper-slide img"))
                        )
                        
                        # Get the current active/loaded image
                        try:
                            active_img = swiper_container.find_element(By.CSS_SELECTOR, ".swiper-slide img")
                            img_url = active_img.get_attribute("src") or active_img.get_attribute("data-src")
                            if img_url and not img_url.endswith('no-pic.png'):
                                # Convert to high resolution
                                high_res_url = img_url.replace("Z360x270", "Z1440x1080").replace("Z720x540", "Z1440x1080")
                                image_urls.append(high_res_url)
                        except:
                            pass
                        
                        # Get next button and click through carousel (limit to 5 images for speed)
                        try:
                            next_button = swiper_container.find_element(By.CSS_SELECTOR, ".swiper-next")
                            max_images = 30 
                            
                            for i in range(max_images - 1):
                                try:
                                    # Check if next button is disabled (end of carousel)
                                    button_class = next_button.get_attribute("class") or ""
                                    if "swiper-button-disabled" in button_class:
                                        break
                                        
                                    # Click next button with human-like delay
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    
                                    # Get the new active image
                                    new_active_img = swiper_container.find_element(By.CSS_SELECTOR, ".swiper-slide-active img")
                                    new_img_url = new_active_img.get_attribute("src") or new_active_img.get_attribute("data-src")
                                    
                                    if new_img_url and not new_img_url.endswith('no-pic.png'):
                                        # Convert to high resolution
                                        high_res_url = new_img_url.replace("Z360x270", "Z1440x1080").replace("Z720x540", "Z1440x1080")
                                        if high_res_url not in image_urls:  # Avoid duplicates
                                            image_urls.append(high_res_url)
                                    
                                except Exception as e:
                                    # Break if we can't get more images
                                    break
                        except:
                            pass
                            
                    except Exception as e:
                        self._log('warning', f"Error extracting image URLs: {str(e)}")
                        image_urls = []
                        
                    # Match Imovirtual scraper structure exactly: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Parish_ID, County_ID, District_ID, Source, ScrapedAt, ImageURLs
                    info_list = [
                        name,           # Name
                        zone,           # Zone
                        price,          # Price
                        url,            # URL
                        bedrooms,       # Bedrooms
                        area,           # Area
                        floor,          # Floor
                        description,    # Description
                        parish_id,      # Parish ID
                        county_id,      # County ID
                        district_id,    # District ID
                        self.source,    # Source
                        None,           # ScrapedAt (will be filled by save_to_database)
                        image_urls      # Image URLs as list
                    ]
                    
                    if self.save_to_database(info_list):
                        # Add the URL to our existing URLs set to avoid duplicates in the same run
                        self.existing_urls.add(url)
                    
                except Exception as e:
                    self._log('error', f"Error processing property: {str(e)}")
                    continue

            # Check if pagination exists and if there's a next page before returning
            has_next_page = self._check_pagination(self.driver, page_num)
            
            # Only return True (continue to next page) if we found new listings AND pagination exists
            return found_new_listing and has_next_page

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return False
    def _check_pagination(self, driver, page_num):
        """Check if pagination exists and if there's a next page available"""
        try:
            # Check if pagination element exists
            pagination = driver.find_elements(By.CLASS_NAME, "list-pagination")
            if not pagination:
                self._log('info', "No pagination element found. This is the last page.")
                return False
                
            # Check if there's a link to the next page
            next_page_link = driver.find_elements(By.CLASS_NAME, "list-pagination-next")
            if not next_page_link:
                self._log('info', "No next page link found. This is the last page.")
                return False
                
            # Verify that the current page has a link to page_num+1
            next_page_url = f"/pagina-{page_num + 1}"
            pagination_links = driver.find_elements(By.CSS_SELECTOR, f".list-pagination-page[href*='{next_page_url}']")
            if not pagination_links:
                self._log('info', f"No link to page {page_num + 1} found. This is the last page.")
                return False
                
            self._log('info', f"Pagination found with link to page {page_num + 1}")
            return True
            
        except Exception as e:
            self._log('warning', f"Error checking pagination: {str(e)}")
            return False
