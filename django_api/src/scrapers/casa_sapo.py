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
    def __init__(self, logger, urls):
        super().__init__(logger)
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
            max_pages = 2  # Safety limit

            while page_num <= max_pages:
                # Stop if page processing returns False (no properties found)
                if not self._process_page(site_url, page_num):
                    break
                page_num += 1

        self._log('analyzing', "Finished processing all pages for Casa SAPO")

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}&pn={page_num}"

        try:
            self._log('scraping', f"Processing page {page_num}...")
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
                
                self._log('initializing', "Chrome driver initialized successfully")
                driver.get(current_url)
                self._log('loading', f"Navigated to URL: {current_url}")
                time.sleep(random.uniform(8, 12))  # Randomized wait
                
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
                    
                    # Get price
                    price_value_elem = property_info.find_element(By.CLASS_NAME, "property-price-value")
                    price = price_value_elem.text.strip() if price_value_elem else "N/A"

                    # Get description of property-description
                    property_info = property_item.find_element(By.CLASS_NAME, "property-info")

                    description = "N/A"  # Default value
                    try:
                        description_elem = property_item.find_element(By.CLASS_NAME, "property-description")
                        description = description_elem.text.strip() if description_elem else "N/A"
                    except Exception as description_error:
                        self._log('error', f"Error extracting description: {str(description_error)}")

                    # Initialize image URLs list
                    image_urls = []
                    
                    # Click to get detailed information
                    try:
                        # Click on the property link
                        driver.execute_script("arguments[0].click();", property_info)
                        time.sleep(random.uniform(2, 3))  # Wait for page to load
                        
                        # Wait for the details to be present
                        detail_features = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "detail-main-features-item"))
                        )
                        
                        # Extract area from detailed features
                        area = "N/A"
                        for feature in detail_features:
                            try:
                                title = feature.find_element(By.CLASS_NAME, "detail-main-features-item-title").text
                                if "ÁREA ÚTIL" in title or "ÁREA BRUTA" in title:
                                    area = feature.find_element(By.CLASS_NAME, "detail-main-features-item-value").text
                                    break
                            except:
                                continue
                            
                        # Collect image URLs
                        try:
                            # Wait longer for images to load
                            time.sleep(random.uniform(1, 2))  # Additional wait for images
                            
                            # First try: Get images from swiper-wrapper (main approach)
                            try:
                                # Completely different approach: check if element exists without waiting
                                swiper_exists = False
                                try:
                                    # Use a very short explicit wait with explicit TimeoutException handling
                                    try:
                                        # Very short timeout to quickly check if swiper exists
                                        WebDriverWait(driver, 3).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, "swiper-wrapper"))
                                        )
                                        swiper_exists = True
                                        self._log('info', "Swiper wrapper found quickly")
                                    except TimeoutException:
                                        # If timeout occurs, swiper doesn't exist or takes too long to load
                                        self._log('info', "No swiper found (timeout), moving to fallbacks")
                                        swiper_exists = False
                                except Exception as e:
                                    # Handle any other exceptions
                                    self._log('info', f"Error checking for swiper: {str(e)}")
                                    swiper_exists = False
                                
                                # Only proceed with swiper approach if swiper_exists is True
                                if swiper_exists:
                                    # Get all swiper wrappers (there might be multiple on the page)
                                    swiper_wrappers = driver.find_elements(By.CLASS_NAME, "swiper-wrapper")
                                    self._log('info', f"Found {len(swiper_wrappers)} swiper wrappers")
                                    
                                    # Process all swiper wrappers
                                    for swiper in swiper_wrappers:
                                        try:
                                            slide_elements = swiper.find_elements(By.CLASS_NAME, "swiper-slide")
                                            
                                            if slide_elements:
                                                self._log('info', f"Found {len(slide_elements)} slide elements")
                                                
                                                # Extract images from slides
                                                for slide in slide_elements:
                                                    try:
                                                        # Try to find images inside slides
                                                        img_elements = slide.find_elements(By.TAG_NAME, "img")
                                                        for img in img_elements:
                                                            src = img.get_attribute("src")
                                                            if src and src not in image_urls:
                                                                # Skip if URL contains any of the skip strings
                                                                if not any(skip_str in src.lower() for skip_str in self.skip_image_strings):
                                                                    image_urls.append(src)
                                                                
                                                        # Also try to find picture elements inside slides
                                                        picture_elements = slide.find_elements(By.TAG_NAME, "picture")
                                                        for picture in picture_elements:
                                                            # Try to get source elements first
                                                            source_elements = picture.find_elements(By.TAG_NAME, "source")
                                                            for source in source_elements:
                                                                srcset = source.get_attribute("srcset")
                                                                if srcset:  # Check for srcset attribute
                                                                    urls = srcset.split(",")
                                                                    highest_res_url = None
                                                                    
                                                                    # Try to find highest resolution (4x or the last one)
                                                                    for url_part in urls:
                                                                        if "4x" in url_part:
                                                                            highest_res_url = url_part.split(" ")[0].strip()
                                                                            break
                                                                    
                                                                    # If no 4x, take the last one (usually highest resolution)
                                                                    if not highest_res_url and urls:
                                                                        highest_res_url = urls[-1].split(" ")[0].strip()
                                                                    
                                                                    if highest_res_url and highest_res_url not in image_urls:
                                                                        # Skip if URL contains any of the skip strings
                                                                        if not any(skip_str in highest_res_url.lower() for skip_str in self.skip_image_strings):
                                                                            image_urls.append(highest_res_url)
                                                            
                                                            # Fallback to img tag inside picture
                                                            if not source_elements:
                                                                img_elements = picture.find_elements(By.TAG_NAME, "img")
                                                                for img in img_elements:
                                                                    src = img.get_attribute("src")
                                                                    if src and src not in image_urls:
                                                                        # Skip if URL contains any of the skip strings
                                                                        if not any(skip_str in src.lower() for skip_str in self.skip_image_strings):
                                                                            image_urls.append(src)
                                                    except Exception as e:
                                                        self._log('warning', f"Error processing slide: {str(e)}")
                                                        continue
                                        except Exception as e:
                                            self._log('warning', f"Error processing swiper wrapper: {str(e)}")
                                else:
                                    self._log('info', "Skipping swiper approach, moving to fallbacks")
                                    
                                    # For problematic properties where swiper doesn't exist, immediately try page source extraction
                                    # This is our most reliable fallback
                                    try:
                                        self._log('info', "Immediately trying page source extraction as first fallback")
                                        # Get page source
                                        page_source = driver.page_source
                                        
                                        # Use regex to find image URLs in the page source
                                        img_patterns = [
                                            r'https://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*',
                                            r'https://casa\.sapo\.pt/[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*',
                                            r'https://images-casa\.sapo\.pt/[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*'
                                        ]
                                        
                                        found_urls = []
                                        for pattern in img_patterns:
                                            found_urls.extend(re.findall(pattern, page_source))
                                        
                                        # Filter and clean URLs
                                        for url in found_urls:
                                            # Clean URL (remove query parameters, etc.)
                                            clean_url = url.split('?')[0].split('#')[0]
                                            if clean_url and clean_url not in image_urls:
                                                # Skip if URL contains any of the skip strings
                                                if not any(skip_str in clean_url.lower() for skip_str in self.skip_image_strings):
                                                    # Only add URLs that look like they might be property images
                                                    if any(term in clean_url.lower() for term in ['photo', 'image', 'imag', 'foto', 'media']):
                                                        image_urls.append(clean_url)
                                        
                                        self._log('info', f"Direct page source extraction found {len(image_urls)} images")
                                    except Exception as e:
                                        self._log('info', f"Direct page source extraction failed: {str(e)}")
                            except Exception as e:
                                self._log('info', f"Swiper approach failed: {str(e)}")
                                # Continue to next approach
                            
                            # Second try: Fallback to gallery items
                            if not image_urls:
                                try:
                                    # Try with multiple selectors that might contain images
                                    gallery_selectors = [
                                        ".gallery-item", 
                                        ".gallery img", 
                                        ".photo-gallery img",
                                        ".photos img",
                                        ".property-photos img",
                                        "[class*='gallery'] img",
                                        "[class*='slider'] img",
                                        "[class*='carousel'] img"
                                    ]
                                    
                                    # Join selectors with commas for a single query
                                    combined_selector = ", ".join(gallery_selectors)
                                    gallery_items = driver.find_elements(By.CSS_SELECTOR, combined_selector)
                                    
                                    self._log('info', f"Gallery approach found {len(gallery_items)} items")
                                    
                                    for item in gallery_items:
                                        try:
                                            # Try multiple attributes that might contain image URLs
                                            for attr in ["src", "data-src", "data-original", "data-lazy-src"]:
                                                src = item.get_attribute(attr)
                                                if src and src not in image_urls and not src.endswith(('.svg', '.ico', '.gif')):
                                                    # Skip if URL contains any of the skip strings
                                                    if not any(skip_str in src.lower() for skip_str in self.skip_image_strings):
                                                        image_urls.append(src)
                                                        break
                                        except Exception as e:
                                            self._log('warning', f"Error processing gallery item: {str(e)}")
                                except Exception as e:
                                    self._log('info', f"Gallery approach failed: {str(e)}")
                            
                            # Third try: Generic image search
                            if not image_urls:
                                try:
                                    # Try finding all images with suitable CSS classes that might indicate property photos
                                    img_elements = driver.find_elements(By.CSS_SELECTOR, "img[class*='photo'], img[class*='image'], img[class*='property'], img[src*='photo']")
                                    for img in img_elements:
                                        try:
                                            src = img.get_attribute("src")
                                            if src and src not in image_urls and not src.endswith(('.svg', '.ico', '.gif')):
                                                # Skip if URL contains any of the skip strings
                                                if not any(skip_str in src.lower() for skip_str in self.skip_image_strings):
                                                    image_urls.append(src)
                                        except Exception as e:
                                            self._log('warning', f"Error processing generic image: {str(e)}")
                                except Exception as e:
                                    self._log('info', f"Generic image search failed: {str(e)}")
                            
                            # Fourth try: Last resort - get all images on the page
                            if not image_urls:
                                try:
                                    # Get all images on the page as a last resort
                                    all_images = driver.find_elements(By.TAG_NAME, "img")
                                    for img in all_images:
                                        try:
                                            src = img.get_attribute("src")
                                            # Filter out small icons and logos
                                            if src and src not in image_urls and not src.endswith(('.svg', '.ico', '.gif')):
                                                # Skip if URL contains any of the skip strings
                                                if not any(skip_str in src.lower() for skip_str in self.skip_image_strings):
                                                    # Try to get image dimensions to filter out small icons
                                                    width = img.get_attribute("width")
                                                    height = img.get_attribute("height")
                                                    if width and height:
                                                        if int(width) > 100 and int(height) > 100:
                                                            image_urls.append(src)
                                                    else:
                                                        # If no dimensions available, add it anyway
                                                        image_urls.append(src)
                                        except Exception as e:
                                            self._log('warning', f"Error processing fallback image: {str(e)}")
                                except Exception as e:
                                    self._log('info', f"All images fallback failed: {str(e)}")
                            
                            # Fifth try: Extract image URLs from page source (most aggressive approach)
                            if not image_urls:
                                try:
                                    # Get page source
                                    page_source = driver.page_source
                                    
                                    # Use regex to find image URLs in the page source
                                    # Look for patterns like: url("https://...")
                                    self._log('info', "Trying to extract images from page source")
                                    img_patterns = [
                                        r'https://[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*',
                                        r'https://casa\.sapo\.pt/[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*',
                                        r'https://images-casa\.sapo\.pt/[^"\']+\.(?:jpg|jpeg|png|webp)[^"\'\)]*'
                                    ]
                                    
                                    found_urls = []
                                    for pattern in img_patterns:
                                        found_urls.extend(re.findall(pattern, page_source))
                                    
                                    # Filter and clean URLs
                                    for url in found_urls:
                                        # Clean URL (remove query parameters, etc.)
                                        clean_url = url.split('?')[0].split('#')[0]
                                        if clean_url and clean_url not in image_urls:
                                            # Skip if URL contains any of the skip strings
                                            if not any(skip_str in clean_url.lower() for skip_str in self.skip_image_strings):
                                                # Only add URLs that look like they might be property images
                                                if any(term in clean_url.lower() for term in ['photo', 'image', 'imag', 'foto', 'media']):
                                                    image_urls.append(clean_url)
                                    
                                    self._log('info', f"Extracted {len(image_urls)} images from page source")
                                except Exception as e:
                                    self._log('info', f"Page source extraction failed: {str(e)}")
                            
                            # Log the result
                            self._log('info', f"Found {len(image_urls)} images for property")
                            
                            # Safety check - if no images found at all, add a placeholder
                            if not image_urls:
                                self._log('warning', "No images found after all attempts, using placeholder")
                                image_urls = ["https://casa.sapo.pt/img/sem-imagem.jpg"]
                            
                        except Exception as e:
                            self._log('warning', f"Error collecting image URLs: {str(e)}")
                            # Add placeholder image URL in case of complete failure
                            image_urls = ["https://casa.sapo.pt/img/sem-imagem.jpg"]
                        
                        # Go back to the listing page
                        driver.back()
                        time.sleep(random.uniform(1, 2))  # Wait for listing page to reload
                        
                        # Wait for the property list to be present again
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "property-info-content"))
                        )
                        
                    except Exception as detail_error:
                        self._log('warning', f"Error getting detailed information: {str(detail_error)}")
                        area = "N/A"
                    
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
                    
                    self._log('debug', "Building info_list...")
                    # Check if we have the new format (IDs) or old format (names)
                    if parish_id is not None:
                        # New format: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Parish_ID, County_ID, District_ID, Source, ScrapedAt, ImageURLs
                        self._log('debug', "Using new format with Parish/County/District IDs")
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
                    else:
                        # Old format fallback: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, ImageURLs
                        self._log('debug', "Using old format with Freguesia/Concelho names")
                        info_list = [
                            name,           # Name
                            zone,           # Zone
                            price,          # Price
                            property_url,   # URL
                            bedrooms,       # Bedrooms
                            area,           # Area
                            "N/A",          # Floor (not available in Casa SAPO)
                            description,    # Description
                            freguesia if freguesia else "N/A",  # Freguesia
                            concelho if concelho else "N/A",    # Concelho
                            "Casa SAPO",    # Source
                            None,           # ScrapedAt (will be filled by save_to_excel)
                            image_urls      # Image URLs as list
                        ]
                    
                    self._log('debug', f"info_list created with {len(info_list)} elements: {[type(x).__name__ for x in info_list]}")
                    self._log('debug', f"Attempting to save to database...")
                    
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
