from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from src.utils.base_scraper import BaseScraper
from src.utils.location_manager import LocationManager
import json
import os
from houses.models import House

class ImoVirtualScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Imovirtual"
        self.location_manager = LocationManager()
        self._initialize_status()
        self._load_existing_urls()
        

    def scrape(self):
        """Scrape houses from ImoVirtual website"""
        for site_url in self.urls:
            self._log('info', f"Starting scrape for URL: {site_url}")
            page_num = 1
            max_pages = 2  # Safety limit

            while page_num <= max_pages:
                if not self._process_page(site_url, page_num):
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
                    # Wait for articles to be present with increased timeout
                    articles = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-cy='listing-item']"))
                    )
                    self._log('info', f"Found {len(articles)} articles")
                    
                    # Process each article with Selenium first
                    selenium_descriptions = []
                    selenium_image_urls = []  # Store image URLs from Selenium interaction
                    
                    for article in articles:
                        try:
                            # Extract URL first to check if already processed
                            try:
                                link_elem = article.find_element(By.CSS_SELECTOR, "a[data-cy='listing-item-link']")
                                url = link_elem.get_attribute('href') if link_elem else "N/A"
                                self._log('info', f"Extracted URL: {url}")
                                # Skip if URL already exists in our database
                                if self.url_exists(url):
                                    self._log('info', f"Skipping already processed property in Selenium phase: {url}")
                                    # Add empty placeholders to maintain index alignment
                                    selenium_descriptions.append("N/A")
                                    selenium_image_urls.append([])
                                    continue
                            except Exception as url_error:
                                self._log('warning', f"Error extracting URL in Selenium phase: {str(url_error)}")
                                url = "N/A"  # Could not extract URL, will process anyway
                            
                            # Get all images from the carousel
                            image_urls_for_article = set()  # Use set to avoid duplicates
                            
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
                                        self._log('info', f"Found initial image: {img_url}")
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
                                                    self._log('info', f"Found image counter text: {total_text}, total: {total_images}")
                                                    break
                                            if total_images > 1:
                                                break
                                        except:
                                            continue
                                    
                                    if total_images == 1:
                                        # Check if there's a next button as a fallback
                                        next_buttons = article.find_elements(By.CSS_SELECTOR, "button[aria-label='Next slide']")
                                        if next_buttons and len(next_buttons) > 0:
                                            total_images = 10  # Assume there are multiple images if next button exists
                                            self._log('info', f"No counter found, but next button exists. Assuming {total_images} images.")
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
                                    for i in range(min(total_images - 1, 9)):  # -1 because we already have the first image, limit to 10 total
                                        try:
                                            driver.execute_script("arguments[0].click();", next_button)
                                            time.sleep(0.5)  # Increased wait for image to load
                                            
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
                                                        self._log('info', f"Found image {i+2}/{total_images}: {img_url}")
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
                            
                            self._log('info', f"Total unique images collected: {len(image_urls_for_article)}")
                            selenium_image_urls.append(list(image_urls_for_article))
                            
                            # Find and click "Ver descrição do anúncio"
                            try:
                                # Updated selector for the description button
                                description_button = None
                                button_selectors = [
                                    ".//div[contains(@class, 'css-1s259kx') and text()='Ver descrição do anúncio']",
                                    ".//div[text()='Ver descrição do anúncio']",
                                    ".//button[contains(text(), 'Ver descrição')]",
                                    ".//div[contains(text(), 'Ver descrição')]"
                                ]
                                
                                for selector in button_selectors:
                                    try:
                                        elements = article.find_elements(By.XPATH, selector)
                                        if elements and len(elements) > 0:
                                            description_button = elements[0]
                                            break
                                    except:
                                        continue
                                
                                if description_button:
                                    driver.execute_script("arguments[0].click()", description_button)
                                    time.sleep(random.uniform(0.8, 1.2))  # Increased wait for description to load
                                else:
                                    self._log('warning', "Description button not found with any selector")
                                
                                # Try multiple selectors for the description text
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
                                
                                for selector in selectors:
                                    try:
                                        elements = article.find_elements(By.CSS_SELECTOR, selector)
                                        if elements and len(elements) > 0:
                                            for element in elements:
                                                text = element.text.strip()
                                                if text and "Ver descrição do anúncio" not in text:
                                                    description_text = text
                                                    break
                                            if description_text:
                                                break
                                    except:
                                        continue
                                
                                # If still no description, try a more generic approach
                                if not description_text:
                                    try:
                                        # Wait for the details to expand
                                        time.sleep(0.5)
                                        # Get all text from the details element
                                        details_elem = article.find_element(By.CSS_SELECTOR, "details")
                                        description_text = details_elem.text.replace("Ver descrição do anúncio", "").strip()
                                    except:
                                        pass
                                
                            except Exception as click_error:
                                self._log('warning', f"Error clicking or getting description: {str(click_error)}")
                                description_text = "N/A"
                            
                            selenium_descriptions.append(description_text if description_text else "N/A")
                        except Exception as e:
                            self._log('warning', f"Error processing article: {str(e)}")
                            selenium_descriptions.append("N/A")
                            selenium_image_urls.append([])

                    # Wait a bit for all descriptions to be fully expanded
                    time.sleep(2)
                except Exception as e:
                    self._log('warning', f"Error expanding descriptions: {str(e)}")
                    selenium_descriptions = []
                    selenium_image_urls = []
                
                page_content = driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')
                
                driver.quit()
                
                # Check for blocking
                if "Request blocked" in page_content or "ERROR: The request could not be satisfied" in page_content:
                    self._log('error', "Access blocked by CloudFront - possible bot detection", exc_info=True)
                    return False

                articles = soup.find_all('article', {'data-cy': 'listing-item'})
                if not articles:
                    self._log('warning', f"No articles found on page {page_num}")
                    return False

                found_new_listing = False

                for idx, article in enumerate(articles):
                    try:
                        # Extract URL first to check if already processed
                        link_elem = article.find('a', {'data-cy': 'listing-item-link'})
                        url = f"https://www.imovirtual.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else "N/A"
                        
                        # Skip if URL already exists in our database
                        if self.url_exists(url):
                            self._log('info', f"Skipping already processed property: {url}")
                            continue
                        
                        found_new_listing = True
                        
                        # Extract house information
                        title_elem = article.find('p', {'data-cy': 'listing-item-title'})
                        name = title_elem.text.strip() if title_elem else "N/A"
                        
                        # Use the image URLs collected by Selenium
                        image_urls = selenium_image_urls[idx] if idx < len(selenium_image_urls) else []
                        image_urls_str = json.dumps(image_urls) if image_urls else "[]"
                        
                        price_elem = article.find('span', {'direction': 'horizontal'})
                        price = price_elem.text.strip() if price_elem else "N/A"
                        
                        location_elem = article.find('p', {'class': 'css-42r2ms eejmx80'})
                        zone = location_elem.text.strip() if location_elem else "N/A"
                        
                        details_elem = article.find('dl')
                        if details_elem:
                            dd_elements = details_elem.find_all('dd')
                            bedrooms = dd_elements[0].text.strip() if len(dd_elements) > 0 else "N/A"
                            area = dd_elements[1].text.strip() if len(dd_elements) > 1 else "N/A"
                        else:
                            bedrooms = area = "N/A"
                        
                        # Get description from selenium results
                        description = selenium_descriptions[idx] if idx < len(selenium_descriptions) else "N/A"
                        
                        # Extract freguesia and concelho
                        freguesia, concelho = self.location_manager.extract_location(zone)
                        
                        # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, ImageURLs
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
                            "Imovirtual",   # Source
                            None,           # ScrapedAt (will be filled by save_to_excel)
                            image_urls_str  # Image URLs as JSON string
                        ]
                        
                        if self.save_to_excel(info_list):
                            # Add the URL to our existing URLs set to avoid duplicates in the same run
                            self.existing_urls.add(url)
                        
                    except Exception as e:
                        self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                        continue

                return found_new_listing

            except Exception as e:
                self._log('error', f"Error initializing Chrome: {str(e)}", exc_info=True)
                return False

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return False
