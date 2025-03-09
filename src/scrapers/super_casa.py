from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
from src.utils.base_scraper import BaseScraper
from src.utils.location_manager import LocationManager
import os
import json
import re

class SuperCasaScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "SuperCasa"
        self.location_manager = LocationManager()
        self._initialize_status()
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

    def scrape(self):
        """Scrape houses from SuperCasa website"""
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

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            # Use the "/pagina-X" format for pagination instead of "?page=X"
            if url.endswith('/'):
                current_url = f"{url}pagina-{page_num}"
            else:
                current_url = f"{url}/pagina-{page_num}"

        try:
            self._log('info', f"Processing page {page_num}...")
            if page_num > 1:
                time.sleep(5)  # Wait between pages
                
            # Configure Chrome
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
            
            try:
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
                time.sleep(random.uniform(8, 12))  # Randomized wait
                
                # Wait for property listings to be present
                try:
                    property_items = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "property"))
                    )
                    self._log('info', f"Found {len(property_items)} property items")
                except Exception as e:
                    self._log('warning', f"No property items found on page {page_num}: {str(e)}")
                    driver.quit()
                    return False

                found_new_listing = False

                for property_item in property_items:
                    try:
                        # Get URL first to check if already processed
                        url_elem = property_item.find_element(By.CLASS_NAME, "property-link")
                        url = url_elem.get_attribute("href")
                        
                        # If URL is relative, convert to absolute URL
                        if url and url.startswith('/'):
                            url = f"https://supercasa.pt{url}"
                        
                        # Skip if URL already exists in our database
                        if self.url_exists(url):
                            self._log('info', f"Skipping already processed property: {url}")
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
                            bedrooms_match = re.search(r'(T\d+)', title_text)
                            bedrooms = bedrooms_match.group(1) if bedrooms_match else "N/A"
                        except:
                            bedrooms = "N/A"
                            
                        # Get the full title which contains location information
                        try:
                            title_elem = property_item.find_element(By.CLASS_NAME, "property-link")
                            zone = title_elem.get_attribute("title").strip()
                        except:
                            zone = "N/A"
                            
                        # Extract freguesia and concelho
                        freguesia, concelho = self.location_manager.extract_location(zone)
                        
                        try:
                            price_elem = property_item.find_element(By.CSS_SELECTOR, ".property-price span")
                            price = price_elem.text.strip()
                        except:
                            price = "N/A"
                            
                        # Get area from features
                        try:
                            feature_elements = property_item.find_elements(By.CSS_SELECTOR, ".property-features span")
                            # Find the element containing "Área"
                            area_text = next((feat.text.strip() for feat in feature_elements if "Área" in feat.text), "N/A")
                            if area_text != "N/A":
                                # Extract just the number and m² using regex
                                area_match = re.search(r'(\d+)\s*m²', area_text)
                                area = f"{area_match.group(1)} m²" if area_match else "N/A"
                            else:
                                area = "N/A"
                        except:
                            area = "N/A"
                            
                        # Get floor (if available)
                        floor = "N/A"  # SuperCasa typically doesn't show floor information in listings
                        
                        # Get description
                        try:
                            description = property_item.find_element(By.CLASS_NAME, "property-description-text").text.strip()
                        except:
                            description = "N/A"
                            
                        # Get image URLs
                        image_urls = []
                        try:
                            # Wait for images to be present
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".swiper-slide img"))
                            )
                            
                            # Look for all images in the swiper container
                            image_elements = property_item.find_elements(By.CSS_SELECTOR, ".swiper-slide img")
                            self._log('info', f"Found {len(image_elements)} image elements")

                            for img in image_elements:
                                try:
                                    # Wait for the src attribute to be populated
                                    WebDriverWait(driver, 5).until(
                                        lambda x: img.get_attribute("src") is not None
                                    )
                                    
                                    img_url = img.get_attribute("src")
                                    if img_url and not img_url.endswith('placeholder.jpg'):
                                        self._log('info', f"Image URL: {img_url}")
                                        # Get the highest resolution version
                                        high_res_url = img_url.replace("Z360x270", "Z1440x1080")
                                        image_urls.append(high_res_url)
                                except:
                                    continue
                                    
                            # If no images found, try alternative selectors
                            if not image_urls:
                                alternative_selectors = [
                                    ".property-gallery img",
                                    ".property-image img",
                                    "[data-src]"
                                ]
                                for selector in alternative_selectors:
                                    alt_images = property_item.find_elements(By.CSS_SELECTOR, selector)
                                    for img in alt_images:
                                        img_url = img.get_attribute("src") or img.get_attribute("data-src")
                                        if img_url and not img_url.endswith('placeholder.jpg'):
                                            high_res_url = img_url.replace("Z360x270", "Z1440x1080")
                                            image_urls.append(high_res_url)
                                    if image_urls:
                                        break
                                        
                            # Limit the number of images to prevent excessive data
                            if len(image_urls) > 10:
                                image_urls = image_urls[:10]
                                self._log('info', "Limited to 10 images")
                                
                            # Add placeholder if no images found
                            if not image_urls:
                                image_urls = ["https://supercasa.pt/img/no-image.jpg"]  # Update with actual placeholder URL
                                
                        except Exception as e:
                            self._log('warning', f"Error extracting image URLs: {str(e)}")
                            image_urls = ["https://supercasa.pt/img/no-image.jpg"]  # Update with actual placeholder URL
                            
                        # Convert image_urls list to JSON string
                        image_urls_json = json.dumps(image_urls, ensure_ascii=False)
                        
                        # Store the property data
                        info_list = [
                            name,           # Name
                            zone,           # Zone
                            price,          # Price
                            url,            # URL
                            bedrooms,       # Bedrooms
                            area,           # Area
                            floor,          # Floor
                            description,    # Description
                            freguesia if freguesia else "N/A",  # Freguesia
                            concelho if concelho else "N/A",    # Concelho
                            self.source,    # Source
                            None,           # ScrapedAt (will be filled by save_to_database)
                            image_urls_json # Image URLs as JSON string
                        ]
                        
                        if self.save_to_database(info_list):
                            # Add the URL to our existing URLs set to avoid duplicates in the same run
                            self.existing_urls.add(url)
                        
                    except Exception as e:
                        self._log('error', f"Error processing property: {str(e)}")
                        continue

                # Check if pagination exists and if there's a next page before returning
                has_next_page = self._check_pagination(driver, page_num)
                driver.quit()
                
                # Only return True (continue to next page) if we found new listings AND pagination exists
                return found_new_listing and has_next_page

            except Exception as e:
                self._log('error', f"Error initializing Chrome driver: {str(e)}", exc_info=True)
                return False

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
