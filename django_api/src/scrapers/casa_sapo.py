from calendar import c
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import random
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager
import re
import json
import os
from houses.models import House

class CasaSapoScraper(BaseScraper):
    def __init__(self, logger, urls, listing_type='rent'):
        super().__init__(logger, listing_type)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Casa SAPO"
        self.location_manager = LocationManager()
        self._load_existing_urls()
        # List of strings to skip in image URLs
        self.skip_image_strings = [
            'apple-icon',
            'android-icon', 
            'Male',
            'avatar',
            'logo',
            'favicon',
            'sem-imagem'
        ]

    def scrape(self):
        """Scrape houses from Casa SAPO website"""
        for site_url in self.urls:
            self._log('initializing', f"Starting scrape for Casa SAPO URL: {site_url}")
            page_num = 1
            max_pages = 10  # Safety limit

            while page_num <= max_pages:
                # Stop if page processing returns False (no properties found)
                if not self._process_page(site_url, page_num):
                    break
                page_num += 1

        self._log('analyzing', "Finished processing all pages for Casa SAPO")

    def get_detail_page_info(self, driver, property_url):
        """Navigate to detail page and extract area and images"""
        area = "N/A"
        image_urls = []
        
        try:
            # Navigate to detail page
            driver.get(property_url)
            time.sleep(random.uniform(0.5, 0.8))
            
            # Extract area from detailed features
            try:
                detail_features = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "detail-main-features-item"))
                )
                
                for feature in detail_features:
                    try:
                        title = feature.find_element(By.CLASS_NAME, "detail-main-features-item-title").text
                        if "ÁREA ÚTIL" in title or "ÁREA BRUTA" in title:
                            area = feature.find_element(By.CLASS_NAME, "detail-main-features-item-value").text
                            break
                    except:
                        continue
            except Exception as e:
                self._log('warning', f"Error extracting area: {str(e)}")
            
            # Extract images from detail-media-imgs div
            try:
                media_div = driver.find_element(By.CLASS_NAME, "detail-media-imgs")
                swiper_slides = media_div.find_elements(By.CSS_SELECTOR, "div[data-swiper-slide-index]")
                
                for idx, slide in enumerate(swiper_slides):
                    try:
                        img = slide.find_element(By.TAG_NAME, "img")
                        src = img.get_attribute("data-src")
                        
                        if not src:
                            ## use src instead of data-src
                            src = img.get_attribute("src")

                            if not src:
                                self._log('info', f"Slide {idx+1}: Skipped - src is None or empty")
                                continue
                            
                        if src in image_urls:
                            continue
                        
                        # Check if URL contains any skip strings
                        skip_matches = [skip_str for skip_str in self.skip_image_strings if skip_str in src.lower()]
                        if skip_matches:
                            continue
                        
                        image_urls.append(src)
                        
                    except Exception as e:
                        self._log('warning', f"Slide {idx+1}: Error extracting image from slide: {str(e)}")
                        continue
                        
            except Exception as e:
                self._log('warning', f"Error extracting images from detail-media-imgs: {str(e)}")
        
        except Exception as e:
            self._log('error', f"Error navigating to detail page: {str(e)}")
        
        return area, image_urls

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}&pn={page_num}"

        try:
            self._log('scraping', f"Processing page {page_num}...")
                
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
                
                self._log('initializing', "Chrome driver initialized successfully")
                driver.get(current_url)
                self._log('loading', f"Navigated to URL: {current_url}")
                time.sleep(random.uniform(2, 3))  # Randomized wait
                
                # Wait for property items to be present
                try:
                    property_items = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "property-info-content"))
                    )
                    self._log('processing', f"Found {len(property_items)} property items")
                    if len(property_items) == 0:
                        self._log('analyzing', "No properties found on this page, stopping pagination")
                        driver.quit()
                        return False  # Signal to stop pagination
                except Exception as e:
                    self._log('warning', f"No property items found on page {page_num}: {str(e)}")
                    driver.quit()
                    return False  # Signal to stop pagination

            except Exception as e:
                self._log('error', f"Error initializing Chrome driver: {str(e)}")
                return False  # Signal to stop pagination

            for property_item in property_items:
                try:
                    self._log('debug', "=== Starting new property processing ===")
                    if self.current_run:
                        self.current_run.total_houses += 1
                        self.current_run.save()
                    # Extract basic information
                    self._log('debug', "Finding property-info element...")
                    property_info = property_item.find_element(By.CLASS_NAME, "property-info")
                    self._log('debug', "property-info element found")
                    
                    # Get URL first to check if already processed - improved extraction
                    self._log('debug', "Extracting property URL...")
                    try:
                        # Direct href attribute extraction
                        href = property_info.get_attribute("href")
                        
                        # Handle different URL formats
                        if href:
                            # Handle relative URLs (starting with /)
                            if href.startswith('/'):
                                url = f"https://casa.sapo.pt{href}"
                            # Handle redirect URLs with l= parameter
                            elif 'l=' in href:
                                url = href.split('l=')[1].split('&')[0] if '&' in href.split('l=')[1] else href.split('l=')[1]
                                url = url.replace('&amp;', '&')
                            # Handle direct URLs
                            elif href.startswith('http'):
                                url = href
                            else:
                                url = None
                        else:
                            url = None
                            
                        # If URL extraction failed, try to get from onclick attribute
                        if not url or any(skip_str in url.lower() for skip_str in self.skip_image_strings):
                            onclick_attr = property_info.get_attribute("onclick")
                            if onclick_attr and "Search.setLastSearch" in onclick_attr:
                                # Extract property ID from onclick attribute
                                try:
                                    property_id = onclick_attr.split("'")[1] if "'" in onclick_attr else onclick_attr.split('"')[1]
                                    # Construct URL from property ID
                                    url = f"https://casa.sapo.pt/alugar-imovel-{property_id}.html"
                                except:
                                    self._log('warning', f"Could not extract property ID from onclick: {onclick_attr}")
                        
                        # Final validation - skip URLs that contain image file extensions or skip strings
                        if not url or not url.startswith('http') or '.jpg' in url or '.png' in url or any(skip_str in url.lower() for skip_str in self.skip_image_strings):
                            self._log('warning', f"Invalid property URL found: {url}, skipping")
                            continue
                            
                        # Store the property URL securely
                        property_url = url
                        self._log('processing', f"Extracted property URL: {property_url}")
                    except Exception as e:
                        self._log('warning', f"Error extracting property URL: {str(e)}")
                        continue
                    
                    # Skip if URL already exists in our database
                    if self.url_exists(property_url):
                        self._log('filtering', f"Skipping already processed property: {property_url}")
                        continue
                    
                    # Get property type and name
                    type_elem = property_info.find_element(By.CLASS_NAME, "property-type")
                    name = type_elem.text.strip() if type_elem else "N/A"
                    
                    # Get location
                    self._log('debug', "Extracting location information...")
                    location_elem = property_info.find_element(By.CLASS_NAME, "property-location")
                    zone = location_elem.text.strip() if location_elem else "N/A"
                    self._log('debug', f"Zone extracted: {zone}")
                    
                    # Initialize variables
                    parish_id = county_id = district_id = None
                    freguesia = concelho = None
                    
                    # Extract parish, county and district IDs
                    self._log('debug', f"Calling extract_location with zone: {zone}")
                    try:
                        location_result = self.location_manager.extract_location(zone)
                        self._log('debug', f"extract_location returned: {location_result} (type: {type(location_result)})")
                        
                        # Check how many values were returned
                        if isinstance(location_result, tuple):
                            self._log('debug', f"Number of values returned: {len(location_result)}")
                            
                            # Unpack based on what's returned
                            if len(location_result) == 3:
                                # New format: (parish_id, county_id, district_id)
                                parish_id, county_id, district_id = location_result
                                self._log('debug', f"Unpacked 3 values - Parish ID: {parish_id}, County ID: {county_id}, District ID: {district_id}")
                            elif len(location_result) == 2:
                                # Old format: (freguesia, concelho)
                                freguesia, concelho = location_result
                                self._log('debug', f"Unpacked 2 values - Freguesia: {freguesia}, Concelho: {concelho}")
                            else:
                                self._log('error', f"Unexpected number of return values: {len(location_result)}")
                        else:
                            self._log('error', f"extract_location did not return a tuple: {type(location_result)}")
                    except Exception as location_error:
                        self._log('error', f"Error in extract_location: {str(location_error)}")
                        import traceback
                        self._log('error', f"Traceback: {traceback.format_exc()}")
                    
                    # Get price (only the direct text, not nested spans)
                    try:
                        price_value_elem = property_info.find_element(By.CLASS_NAME, "property-price-value")
                        # Get only the direct text node (first child text)
                        price = driver.execute_script("""
                            return arguments[0].childNodes[0].textContent.trim();
                        """, price_value_elem)
                    except:
                        price = "N/A"

                    # Get description of property-description
                    property_info = property_item.find_element(By.CLASS_NAME, "property-info")

                    description = "N/A"  # Default value
                    try:
                        description_elem = property_item.find_element(By.CLASS_NAME, "property-description")
                        description = description_elem.text.strip() if description_elem else "N/A"
                    except Exception as description_error:
                        self._log('error', f"Error extracting description: {str(description_error)}")

                    # Get detail page info (area and images)
                    area, image_urls = self.get_detail_page_info(driver, property_url)
                    
                    # Go back to the listing page
                    driver.back()
                    time.sleep(random.uniform(0.5, 0.8))
                    
                    # Wait for the property list to be present again
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "property-info-content"))
                    )
                    
                    # Extract bedrooms from property type (e.g., "Apartamento T2" -> "2")
                    self._log('debug', "Extracting bedrooms from property type...")
                    bedrooms = "N/A"
                    if name and "T" in name:
                        try:
                            bedrooms = name.split("T")[1][0]  # Get first character after T
                            self._log('debug', f"Extracted bedrooms: {bedrooms}")
                        except Exception as bedroom_error:
                            self._log('debug', f"Error extracting bedrooms: {str(bedroom_error)}")
                            bedrooms = "N/A"
                    
                    info_list = [
                        name,           # Name
                        zone,           # Zone
                        price,          # Price
                        property_url,   # URL
                        bedrooms,       # Bedrooms
                        area,           # Area
                        "N/A",          # Floor (not available in Casa SAPO)
                        description,    # Description
                        parish_id,      # Parish ID
                        county_id,      # County ID
                        district_id,    # District ID
                        "Casa SAPO",    # Source
                        None,           # ScrapedAt (will be filled by save_to_excel)
                        image_urls      # Image URLs as list
                    ]
                    
                    if self.save_to_database(info_list):
                        # Add the URL to our existing URLs set to avoid duplicates in the same run
                        self.existing_urls.add(property_url)
                    
                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}")
                    continue

            driver.quit()
            return True  # Signal to continue pagination

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}")
            return False  # Signal to stop pagination
