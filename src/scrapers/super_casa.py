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
        # Define the CSV path
        self.csv_path = os.path.join("data", "houses.csv")
        self._load_existing_urls()

    def get_current_time(self):
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

    def _load_existing_urls(self):
        """Load existing property URLs from the CSV file to avoid duplicates"""
        self.existing_urls = set()
        try:
            # Try to read existing URLs from the CSV file
            if os.path.exists(self.csv_path):
                import pandas as pd
                df = pd.read_csv(self.csv_path, on_bad_lines='skip')
                # Check if 'URL' column exists
                if 'URL' in df.columns:
                    # Add all URLs to the set
                    self.existing_urls = set(df['URL'].dropna().tolist())
                    self._log('info', f"Loaded {len(self.existing_urls)} existing property URLs from database")
                else:
                    self._log('warning', "URL column not found in CSV file")
            else:
                self._log('info', "No existing CSV file found, starting fresh")
        except Exception as e:
            self._log('warning', f"Error loading existing URLs: {str(e)}")
            # Continue with an empty set if there was an error
            self.existing_urls = set()

    def scrape(self):
        """Scrape houses from SuperCasa website"""
        total_processed = 0
        total_new_listings = 0
        total_skipped = 0

        for site_url in self.urls:
            self._log('info', f"Starting scrape for URL: {site_url}")
            page_num = 1
            max_pages = 2  # Safety limit

            while page_num <= max_pages:
                processed, new_listings, skipped = self._process_page(site_url, page_num)
                total_processed += processed
                total_new_listings += new_listings
                total_skipped += skipped
                
                # Break the loop if no new listings were found on this page
                if new_listings == 0:
                    self._log('info', f"No new listings found on page {page_num}, stopping pagination")
                    break
                
                page_num += 1

        self._log('info', "Finished processing all pages")
        self._log('info', f"Total houses processed: {total_processed}")
        self._log('info', f"Total new listings found: {total_new_listings}")
        self._log('info', f"Total listings skipped (already in database): {total_skipped}")

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}?page={page_num}"

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
                    return 0, 0, 0

                processed = 0
                new_listings = 0
                skipped = 0

                for property_item in property_items:
                    try:
                        # Get URL first to check if already processed
                        url_elem = property_item.find_element(By.CLASS_NAME, "property-link")
                        url = url_elem.get_attribute("href")
                        
                        # Skip if URL already exists in our database
                        if url in self.existing_urls:
                            self._log('info', f"Skipping already processed property: {url}")
                            skipped += 1
                            continue
                        
                        processed += 1
                        
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
                            # Scroll the property item into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", property_item)
                            # Add a small delay to allow lazy loading to trigger
                            time.sleep(2)
                            
                            # Wait for images to be present with a timeout
                            try:
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swiper-slide img"))
                                )
                            except Exception as wait_error:
                                self._log('warning', f"Timeout waiting for images to load: {str(wait_error)}")
                            
                            # Look for all images in the swiper container
                            image_elements = property_item.find_elements(By.CSS_SELECTOR, ".swiper-slide img")
                            self._log('info', f"Found {len(image_elements)} image elements")

                            for img in image_elements:
                                # Wait for the src attribute to be populated
                                try:
                                    WebDriverWait(driver, 5).until(
                                        lambda x: img.get_attribute("src") is not None
                                    )
                                except:
                                    continue
                                
                                img_url = img.get_attribute("src")
                                if img_url and not img_url.endswith('placeholder.jpg'):  # Skip placeholder images
                                    self._log('info', f"Image URL: {img_url}")
                                    # Get the highest resolution version by replacing the resolution in the URL
                                    high_res_url = img_url.replace("Z360x270", "Z1440x1080")
                                    image_urls.append(high_res_url)
                                else:
                                    self._log('warning', "No valid image URL found or placeholder image detected")
                                    
                            if not image_urls:
                                # Try alternative selectors if no images found
                                alternative_selectors = [
                                    ".property-gallery img",
                                    ".property-image img",
                                    "[data-src]"  # For lazy-loaded images
                                ]
                                for selector in alternative_selectors:
                                    alt_images = property_item.find_elements(By.CSS_SELECTOR, selector)
                                    if alt_images:
                                        for img in alt_images:
                                            img_url = img.get_attribute("src") or img.get_attribute("data-src")
                                            if img_url and not img_url.endswith('placeholder.jpg'):
                                                high_res_url = img_url.replace("Z360x270", "Z1440x1080")
                                                image_urls.append(high_res_url)
                                        if image_urls:
                                            break
                                            
                        except Exception as e:
                            self._log('warning', f"Error extracting image URLs: {str(e)}")
                            
                        # Store the property data
                        # Convert image_urls list to JSON string
                        image_urls_json = json.dumps(image_urls, ensure_ascii=False)
                        
                        # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, ImageURLs
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
                            None,           # ScrapedAt (will be filled by save_to_excel)
                            image_urls_json # Image URLs as JSON string
                        ]
                        
                        if self.save_to_excel(info_list):
                            new_listings += 1
                            # Add the URL to our existing URLs set to avoid duplicates in the same run
                            self.existing_urls.add(url)
                        
                    except Exception as e:
                        self._log('error', f"Error processing property: {str(e)}")
                        continue

                driver.quit()
                return processed, new_listings, skipped

            except Exception as e:
                self._log('error', f"Error initializing Chrome driver: {str(e)}", exc_info=True)
                return 0, 0, 0

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return 0, 0, 0
