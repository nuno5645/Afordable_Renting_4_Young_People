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
import json
import os
from houses.models import House

class ImoVirtualScraper(BaseScraper):
    def __init__(self, logger, urls, listing_type='rent'):
        super().__init__(logger, listing_type)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Imovirtual"
        self.location_manager = LocationManager()
        self._load_existing_urls()
        

    def scrape(self):
        """Scrape houses from ImoVirtual website"""
        for site_url in self.urls:
            self._log('info', f"Starting scrape for URL: {site_url}")
            page_num = 1
            max_pages = 50  # Increased safety limit

            while page_num <= max_pages:
                continue_scraping = self._process_page(site_url, page_num)
                if not continue_scraping:
                    self._log('info', f"Stopping scraping - no more pages or no new listings found")
                    break
                page_num += 1

        self._log('info', "Finished processing all pages")

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}&page={page_num}"

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
                time.sleep(random.uniform(5, 7))  # Randomized wait
                
                # Find and click all description expanders
                try:
                    self._log('info', "Attempting to find articles on the page...")
                    
                    # First, let's see what's actually on the page
                    try:
                        page_source_sample = driver.page_source[:2000]  # First 2000 chars
                        self._log('debug', f"Page source sample: {page_source_sample}")
                        
                        # Check for common blocking indicators
                        if "cloudflare" in page_source_sample.lower():
                            self._log('error', "Cloudflare detected in page source")
                        if "captcha" in page_source_sample.lower():
                            self._log('error', "CAPTCHA detected in page source")
                        if "blocked" in page_source_sample.lower():
                            self._log('error', "Blocked message detected in page source")
                        if "403" in page_source_sample or "forbidden" in page_source_sample.lower():
                            self._log('error', "403/Forbidden detected in page source")
                            
                        # Check for different article selectors
                        alternative_selectors = [
                            "article[data-cy='listing-item']",
                            "article",
                            "div[data-cy='listing-item']",
                            ".listing-item",
                            "[data-testid*='listing']",
                            ".property-item",
                            ".search-result",
                            ".listing"
                        ]
                        
                        for selector in alternative_selectors:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                self._log('debug', f"Selector '{selector}' found {len(elements)} elements")
                                if len(elements) > 0:
                                    # Log some details about the first element
                                    first_elem = elements[0]
                                    self._log('debug', f"First element HTML sample: {first_elem.get_attribute('outerHTML')[:500]}")
                            except Exception as selector_error:
                                self._log('debug', f"Selector '{selector}' failed: {str(selector_error)}")
                        
                        # Check for any divs or sections that might contain listings
                        general_containers = [
                            "main",
                            ".search-results",
                            ".results",
                            ".listings",
                            "#search-results",
                            "[data-testid*='search']",
                            "[data-testid*='result']"
                        ]
                        
                        for container in general_containers:
                            try:
                                elements = driver.find_elements(By.CSS_SELECTOR, container)
                                if len(elements) > 0:
                                    self._log('debug', f"Container '{container}' found with {len(elements)} elements")
                                    # Check if it has children
                                    children = elements[0].find_elements(By.XPATH, ".//*")
                                    self._log('debug', f"Container '{container}' has {len(children)} child elements")
                            except Exception as container_error:
                                self._log('debug', f"Container '{container}' check failed: {str(container_error)}")
                                
                    except Exception as debug_error:
                        self._log('error', f"Error during page debugging: {str(debug_error)}")
                    
                    # Wait for articles to be present with increased timeout
                    # Updated selector based on actual HTML structure
                    articles = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-sentry-component='AdvertCard']"))
                    )
                    self._log('info', f"Successfully found {len(articles)} articles, swipping photos with Selenium (can take a while)")
                    
                    # Process each article with Selenium first
                    selenium_descriptions = []
                    selenium_image_urls = []  # Store image URLs from Selenium interaction
                    
                    for idx, article in enumerate(articles):
                        try:
                            self._log('debug', f"Processing article {idx + 1}/{len(articles)}...")
                            # Extract URL first to check if already processed
                            try:
                                if self.current_run:
                                    self.current_run.total_houses += 1
                                    self.current_run.save()
                                link_elem = article.find_element(By.CSS_SELECTOR, "a[data-cy='listing-item-link']")
                                url = link_elem.get_attribute('href') if link_elem else "N/A"
                                self._log('debug', f"Article {idx + 1} URL: {url}")
                                # Skip if URL already exists in our database
                                if self.url_exists(url):
                                    self._log('info', f"Skipping already processed property in Selenium phase: {url}")
                                    # Add empty placeholders to maintain index alignment
                                    selenium_descriptions.append("N/A")
                                    selenium_image_urls.append([])
                                    continue
                            except Exception as url_error:
                                self._log('warning', f"Error extracting URL in Selenium phase for article {idx + 1}: {str(url_error)}")
                                url = "N/A"  # Could not extract URL, will process anyway
                            
                            # Get all images from the carousel
                            image_urls_for_article = set()  # Use set to avoid duplicates
                            self._log('debug', f"[IMAGE_DEBUG] Starting image collection for article {idx+1}")
                            
                            # First get the visible image
                            try:
                                # Try multiple selectors for the initial image
                                visible_img = None
                                initial_image_selectors = [
                                    "img[data-cy='listing-item-image-source']",
                                    "div.slick-slide.slick-active img",
                                    "div.slick-slide.slick-current img",
                                    "div[aria-hidden='false'] img",
                                    "div.slick-track img",  # More generic selector
                                    "img[alt]",  # Any image with alt attribute
                                    "img"  # Last resort - any image
                                ]
                                
                                for selector in initial_image_selectors:
                                    try:
                                        elements = article.find_elements(By.CSS_SELECTOR, selector)
                                        if elements and len(elements) > 0:
                                            visible_img = elements[0]
                                            break
                                    except:
                                        continue
                                
                                if visible_img:
                                    img_url = visible_img.get_attribute('src')
                                    if img_url:
                                        image_urls_for_article.add(img_url)
                                    else:
                                        self._log('warning', "Initial image found but src attribute is empty")
                                else:
                                    self._log('warning', "Could not find initial image with any selector")
                            except Exception as e:
                                self._log('warning', f"Error getting initial image: {str(e)}")
                            
                            # Find and click next button until we've seen all images
                            try:
                                # Find the total number of images
                                total_images = 1  # Default to 1 if we can't find the counter
                                try:
                                    # Try multiple selectors for the image counter
                                    counter_selectors = [
                                        ".css-kq3ezz",
                                        "div[class*='css-'] span",
                                        "div.slick-slider span",
                                        "div.slick-slider div[class*='css-']"
                                    ]
                                    
                                    for selector in counter_selectors:
                                        try:
                                            elements = article.find_elements(By.CSS_SELECTOR, selector)
                                            for element in elements:
                                                text = element.text.strip()
                                                if '/' in text:  # Format like "1 / 13"
                                                    total_text = text
                                                    # Extract the total number from the format "1 / 13"
                                                    total_images = int(total_text.split('/')[-1].strip())
                                                    break
                                            if total_images > 1:
                                                break
                                        except:
                                            continue
                                    
                                    if total_images == 1:
                                        # Check if there's a next button as a fallback
                                        next_buttons = article.find_elements(By.CSS_SELECTOR, "button[aria-label='Next slide']")
                                        if next_buttons and len(next_buttons) > 0:
                                            total_images = 100  # Assume there are multiple images if next button exists (high limit)
                                except Exception as counter_error:
                                    self._log('warning', f"Error finding image counter: {str(counter_error)}")
                                    total_images = 1  # Default to 1 if we can't find the counter
                                
                                # Find next button
                                next_button = None
                                try:
                                    next_buttons = article.find_elements(By.CSS_SELECTOR, "button[aria-label='Next slide']")
                                    if next_buttons and len(next_buttons) > 0:
                                        next_button = next_buttons[0]
                                    else:
                                        self._log('warning', "Next button not found")
                                except Exception as button_error:
                                    self._log('warning', f"Error finding next button: {str(button_error)}")
                                
                                # Click through remaining images
                                if next_button:
                                    for i in range(total_images - 1):  # -1 because we already have the first image, no limit
                                        try:
                                            driver.execute_script("arguments[0].click();", next_button)
                                            
                                            # Get the current image from the next div - try multiple selectors
                                            try:
                                                # Try different selectors for the current image
                                                current_img = None
                                                selectors = [
                                                    "div[aria-selected='true'] img[data-cy='listing-item-image-source']",
                                                    "div[aria-hidden='false'] img[data-cy='listing-item-image-source']",
                                                    "div.slick-active img[data-cy='listing-item-image-source']",
                                                    "div.slick-current img[data-cy='listing-item-image-source']",
                                                    "div[aria-selected='true'] img",
                                                    "div.slick-active img",
                                                    "img[data-cy='listing-item-image-source']"  # Fallback to any image
                                                ]
                                                
                                                for selector in selectors:
                                                    try:
                                                        elements = article.find_elements(By.CSS_SELECTOR, selector)
                                                        if elements and len(elements) > 0:
                                                            current_img = elements[0]
                                                            break
                                                    except:
                                                        continue
                                                
                                                if current_img:
                                                    img_url = current_img.get_attribute('src')
                                                    if img_url and img_url not in image_urls_for_article:
                                                        image_urls_for_article.add(img_url)
                                                else:
                                                    self._log('warning', f"Could not find image {i+2} with any selector")
                                            except Exception as img_error:
                                                self._log('warning', f"Error getting image {i+2}: {str(img_error)}")
                                        except Exception as click_error:
                                            self._log('warning', f"Error clicking for image {i+2}: {str(click_error)}")
                                            break
                                else:
                                    self._log('info', "No next button found, using only the initial image")
                                
                            except Exception as e:
                                self._log('warning', f"Error cycling through images: {str(e)}")
                            
                            selenium_image_urls.append(list(image_urls_for_article))
                            
                            # Find and click "Ver descrição do anúncio"
                            try:
                                self._log('debug', f"Searching for description button in article {idx + 1}...")
                                # Updated selector for the description button
                                description_button = None
                                button_selectors = [
                                    ".//div[contains(@class, 'css-1s259kx') and text()='Ver descrição do anúncio']",
                                    ".//div[text()='Ver descrição do anúncio']",
                                    ".//button[contains(text(), 'Ver descrição')]",
                                    ".//div[contains(text(), 'Ver descrição')]"
                                ]
                                
                                for selector_idx, selector in enumerate(button_selectors):
                                    try:
                                        elements = article.find_elements(By.XPATH, selector)
                                        if elements and len(elements) > 0:
                                            description_button = elements[0]
                                            self._log('debug', f"Found description button using selector {selector_idx + 1}: {selector}")
                                            break
                                    except Exception as selector_error:
                                        self._log('debug', f"Selector {selector_idx + 1} failed: {str(selector_error)}")
                                        continue
                                
                                if description_button:
                                    self._log('debug', f"Clicking description button for article {idx + 1}...")
                                    driver.execute_script("arguments[0].click()", description_button)
                                    time.sleep(random.uniform(0.8, 1.2))  # Increased wait for description to load
                                    self._log('debug', f"Description button clicked successfully for article {idx + 1}")
                                else:
                                    self._log('warning', f"Description button not found with any selector for article {idx + 1}")
                                
                                # Try multiple selectors for the description text
                                self._log('debug', f"Searching for description text in article {idx + 1}...")
                                description_text = ""
                                selectors = [
                                    "div.css-1b63dzw",  # Old selector
                                    "div[class*='e1u1ec23']",  # Alternate old selector
                                    "div.e3rj9t1 > div",  # New possible selector
                                    "details[class*='e3rj9t1'] > div",  # Another possible selector
                                    "details > div",  # Generic details content
                                    "div[class*='css-'] > p",  # Generic paragraph in a div
                                    "details p",  # Paragraphs inside details
                                    "details",  # Entire details element
                                    "div.css-1s259kx + div"  # Div after the button
                                ]
                                
                                for desc_selector_idx, selector in enumerate(selectors):
                                    try:
                                        elements = article.find_elements(By.CSS_SELECTOR, selector)
                                        if elements and len(elements) > 0:
                                            for element_idx, element in enumerate(elements):
                                                text = element.text.strip()
                                                if text and "Ver descrição do anúncio" not in text:
                                                    description_text = text
                                                    self._log('debug', f"Found description using selector {desc_selector_idx + 1}, element {element_idx + 1}: {text[:100]}...")
                                                    break
                                            if description_text:
                                                break
                                    except Exception as desc_selector_error:
                                        self._log('debug', f"Description selector {desc_selector_idx + 1} failed: {str(desc_selector_error)}")
                                        continue
                                
                                # If still no description, try a more generic approach
                                if not description_text:
                                    try:
                                        self._log('debug', f"Trying fallback method for description in article {idx + 1}...")
                                        # Wait for the details to expand
                                        time.sleep(0.5)
                                        # Get all text from the details element
                                        details_elem = article.find_element(By.CSS_SELECTOR, "details")
                                        description_text = details_elem.text.replace("Ver descrição do anúncio", "").strip()
                                        if description_text:
                                            self._log('debug', f"Found description using fallback method: {description_text[:100]}...")
                                        else:
                                            self._log('warning', f"Fallback method returned empty description for article {idx + 1}")
                                    except Exception as fallback_error:
                                        self._log('warning', f"Fallback description method failed for article {idx + 1}: {str(fallback_error)}")
                                        pass
                                
                                if not description_text:
                                    self._log('warning', f"No description found for article {idx + 1} after trying all methods")
                                
                            except Exception as click_error:
                                self._log('error', f"Error clicking or getting description for article {idx + 1}: {str(click_error)}")
                                description_text = "N/A"
                            
                            selenium_descriptions.append(description_text if description_text else "N/A")
                        except Exception as e:
                            self._log('error', f"Error processing article {idx + 1}: {str(e)}")
                            selenium_descriptions.append("N/A")
                            selenium_image_urls.append([])

                    # Wait a bit for all descriptions to be fully expanded
                    self._log('debug', "Waiting for all descriptions to be fully expanded...")
                    time.sleep(2)
                    self._log('debug', f"Successfully processed {len(selenium_descriptions)} descriptions")
                except Exception as e:
                    self._log('error', f"Error expanding descriptions - Full details: {str(e)}")
                    self._log('error', f"Error type: {type(e).__name__}")
                    self._log('error', f"Error args: {e.args}")
                    
                    # Try to get more context about the current state
                    try:
                        current_url = driver.current_url
                        self._log('error', f"Current URL when error occurred: {current_url}")
                        page_title = driver.title
                        self._log('error', f"Page title when error occurred: {page_title}")
                        
                        # Get full page source to analyze
                        full_page_source = driver.page_source
                        self._log('error', f"Full page source length: {len(full_page_source)} characters")
                        
                        # Save page source to file for debugging
                        debug_file = "/tmp/imovirtual_debug.html"
                        try:
                            with open(debug_file, 'w', encoding='utf-8') as f:
                                f.write(full_page_source)
                            self._log('error', f"Page source saved to: {debug_file}")
                        except Exception as save_error:
                            self._log('error', f"Could not save page source: {str(save_error)}")
                        
                        # Check if we can still find articles
                        articles_check = driver.find_elements(By.CSS_SELECTOR, "article[data-sentry-component='AdvertCard']")
                        self._log('error', f"Articles still visible: {len(articles_check)}")
                        
                        # Try alternative selectors one more time
                        alternative_selectors_final = [
                            "article",
                            "div[data-cy*='listing']",
                            ".listing",
                            "[class*='listing']",
                            "[data-testid*='listing']"
                        ]
                        
                        for selector in alternative_selectors_final:
                            try:
                                alt_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                if len(alt_elements) > 0:
                                    self._log('error', f"Alternative selector '{selector}' found {len(alt_elements)} elements")
                                    # Show sample of first element
                                    sample_html = alt_elements[0].get_attribute('outerHTML')[:300]
                                    self._log('error', f"Sample HTML: {sample_html}")
                            except Exception as alt_error:
                                self._log('error', f"Alternative selector '{selector}' failed: {str(alt_error)}")
                        
                        # Check for any error messages on the page
                        error_messages = driver.find_elements(By.XPATH, "//*[contains(text(), 'erro') or contains(text(), 'error') or contains(text(), 'blocked') or contains(text(), 'captcha') or contains(text(), 'forbidden')]")
                        if error_messages:
                            for msg in error_messages[:5]:  # Limit to first 5 messages
                                msg_text = msg.text.strip()
                                if msg_text:  # Only log non-empty messages
                                    self._log('error', f"Error message found on page: {msg_text}")
                        
                        # Check specific error patterns in the page source
                        error_patterns = [
                            "cloudflare",
                            "captcha", 
                            "blocked",
                            "forbidden",
                            "403",
                            "rate limit",
                            "too many requests",
                            "access denied",
                            "bot detection"
                        ]
                        
                        for pattern in error_patterns:
                            if pattern.lower() in full_page_source.lower():
                                self._log('error', f"Found '{pattern}' in page source")
                        
                    except Exception as context_error:
                        self._log('error', f"Could not get additional context: {str(context_error)}")
                    
                    selenium_descriptions = []
                    selenium_image_urls = []
                
                page_content = driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')
                
                driver.quit()
                
                # Check for blocking
                if "Request blocked" in page_content or "ERROR: The request could not be satisfied" in page_content:
                    self._log('error', "Access blocked by CloudFront - possible bot detection")
                    return False

                # Updated selector to match actual HTML structure
                articles = soup.find_all('article', {'data-sentry-component': 'AdvertCard'})
                if not articles:
                    self._log('warning', f"No articles found on page {page_num}")
                    
                    # Additional debugging for BeautifulSoup parsing
                    self._log('debug', f"BeautifulSoup parsed {len(soup)} total elements")
                    
                    # Try alternative selectors with BeautifulSoup
                    alt_articles = soup.find_all('article')
                    self._log('debug', f"Found {len(alt_articles)} article elements (any type)")
                    
                    listing_divs = soup.find_all('div', {'class': lambda x: x and 'listing' in str(x).lower()})
                    self._log('debug', f"Found {len(listing_divs)} divs with 'listing' in class")
                    
                    data_cy_elements = soup.find_all(attrs={'data-cy': True})
                    self._log('debug', f"Found {len(data_cy_elements)} elements with data-cy attribute")
                    
                    # Log some data-cy values to see what's available
                    cy_values = [elem.get('data-cy') for elem in data_cy_elements[:10]]
                    self._log('debug', f"Sample data-cy values: {cy_values}")
                    
                    return False

                found_new_listing = False

                for idx, article in enumerate(articles):
                    try:
                        # Extract URL first to check if already processed
                        link_elem = article.find('a', {'data-cy': 'listing-item-link'})
                        url = f"https://www.imovirtual.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else "N/A"
                        
                        # Normalize URL to handle /pt/ and /hpr/pt/ variations
                        normalized_url = url.replace('/hpr/pt/', '/pt/')
                        
                        # Skip if URL already exists in our database
                        if self.url_exists(normalized_url):
                            self._log('info', f"Skipping already processed property: {url}")
                            continue
                        
                        found_new_listing = True
                        
                        # Extract house information
                        title_elem = article.find('p', {'data-cy': 'listing-item-title'})
                        name = title_elem.text.strip() if title_elem else "N/A"
                        
                        # Use the image URLs collected by Selenium
                        image_urls = selenium_image_urls[idx] if idx < len(selenium_image_urls) else []
                        self._log('debug', f"[IMAGE_DEBUG] Raw image URLs for {name}: {image_urls}")
                        self._log('debug', f"[IMAGE_DEBUG] Number of images found: {len(image_urls)}")
                        
                        # Ensure image_urls is a list of strings
                        image_urls = [str(url) for url in image_urls if url]
                        
                        # No need to convert to JSON string anymore - we'll pass the list directly
                        self._log('debug', f"[IMAGE_DEBUG] Image URLs to pass: {image_urls}")
                        
                        price_elem = article.find('span', {'data-sentry-element': 'MainPrice'})
                        price = price_elem.text.strip() if price_elem else "N/A"
                        
                        location_elem = article.find('p', {'data-sentry-element': 'StyledParagraph'})
                        zone = location_elem.text.strip() if location_elem else "N/A"
                        
                        details_elem = article.find('dl')
                        if details_elem:
                            dd_elements = details_elem.find_all('dd')
                            bedrooms = "N/A"
                            area = "N/A"
                            floor = "N/A"
                            
                            # Extract bedrooms, area and floor from dd elements
                            for dd in dd_elements:
                                dd_text = dd.text.strip()
                                # Check for bedrooms (T0, T1, T2, etc.)
                                if dd_text.startswith('T') and bedrooms == "N/A":
                                    bedrooms = dd_text
                                # Check for area (contains m²)
                                elif 'm²' in dd_text and area == "N/A":
                                    area = dd_text
                                # Check for floor information
                                elif floor == "N/A":
                                    if "rés do chão" in dd_text.lower():
                                        floor = "0"
                                    elif "piso" in dd_text.lower():
                                        # Extract number from "X piso" format
                                        try:
                                            floor = dd_text.split()[0]
                                        except:
                                            floor = dd_text
                        else:
                            bedrooms = area = floor = "N/A"
                        
                        # Get description from selenium results
                        description = selenium_descriptions[idx] if idx < len(selenium_descriptions) else "N/A"
                        
                        # Extract parish, county and district IDs from address
                        self._log('warning', f"Zone to process found: {zone}")
                        parish_id, county_id, district_id = self.location_manager.extract_location(zone)
                        
                        # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Parish_ID, County_ID, District_ID, Source, ScrapedAt, ImageURLs
                        info_list = [
                            name,           # Name
                            zone,           # Zone
                            price,          # Price
                            normalized_url,  # Use normalized URL
                            bedrooms,       # Bedrooms
                            area,           # Area
                            floor,          # Floor (now extracted from the listing)
                            description,    # Description
                            parish_id,      # Parish ID
                            county_id,      # County ID
                            district_id,    # District ID
                            "Imovirtual",   # Source
                            None,           # ScrapedAt (will be filled by save_to_excel)
                            image_urls      # Pass the list of image URLs directly
                        ]
                        
                        # =============================================
                        # 🟨 DEBUG INFO FOR HOUSE LISTING 🟨
                        # =============================================
                        self._log('debug', f"\033[93m{'='*50}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Name: {info_list[0]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Zone: {info_list[1]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Price: {info_list[2]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] URL: {info_list[3]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Bedrooms: {info_list[4]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Area: {info_list[5]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Floor: {info_list[6]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Description: {info_list[7][:100]}...\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Parish ID: {info_list[8]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] County ID: {info_list[9]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] District ID: {info_list[10]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Source: {info_list[11]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] ScrapedAt: {info_list[11]}\033[0m")
                        self._log('debug', f"\033[93m[DEBUG] Image URLs: {info_list[12]}\033[0m")
                        self._log('debug', f"\033[93m{'='*50}\033[0m")
                        # =============================================
                        
                        
                        self._log('debug', f"[IMAGE_DEBUG] Image URLs in info_list[12]: {info_list[12]}")
                        
                        if self.save_to_database(info_list):
                            # Add the URL to our existing URLs set to avoid duplicates in the same run
                            self.existing_urls.add(normalized_url)
                            self._log('debug', f"[IMAGE_DEBUG] House saved with image URLs: {image_urls}")
                        
                    except Exception as e:
                        self._log('error', f"Error processing house: {str(e)}")
                        continue

                # Check if there's a next page
                has_next_page = False
                try:
                    # Look for pagination component
                    pagination = soup.find('ul', {'data-cy': 'nexus-pagination-component'})
                    if pagination:
                        # Find current page (aria-selected="true")
                        current_page_elem = pagination.find('li', {'aria-selected': 'true'})
                        current_page = int(current_page_elem.text.strip()) if current_page_elem else page_num
                        
                        # Check for next page button (not disabled)
                        next_button = pagination.find('li', {'aria-label': 'Go to next Page'})
                        if next_button and next_button.get('aria-disabled') != 'true':
                            has_next_page = True
                            self._log('info', f"Next page available after page {current_page}")
                        else:
                            self._log('info', f"No more pages after page {current_page}")
                    else:
                        self._log('warning', "Pagination component not found")
                except Exception as pagination_error:
                    self._log('warning', f"Error checking pagination: {str(pagination_error)}")

                return found_new_listing and has_next_page

            except Exception as e:
                self._log('error', f"Error initializing Chrome: {str(e)}")
                return False

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}")
            return False
