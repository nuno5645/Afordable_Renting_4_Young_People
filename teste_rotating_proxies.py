# import random
# import time
# import logging
# import json
# import traceback
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import re

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler('scraper.log'), logging.StreamHandler()]
# )

# # Proxy configuration
# PROXY = "pt-pr.oxylabs.io:10000"
# PROXY_USER = "nuno5645_lEtvV"
# PROXY_PASS = "Qf9ZcCL3Vc_sDsZ"

# # Simplified configurations
# MAX_RETRIES = 3
# TIMEOUT = 30
# MAX_PAGES = 2
# USER_AGENTS = [
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
# ]

# class PropertyScraper:
#     def __init__(self):
#         self.listings_data = []
#         self.current_page = 1

#         chrome_options = Options()
        
#         # Configure browser options
#         # chrome_options.add_argument('--headless')
#         chrome_options.add_argument('--no-sandbox')
#         chrome_options.add_argument('--disable-dev-shm-usage')
#         chrome_options.add_argument('--disable-javascript')
#         chrome_options.add_argument('--blink-settings=imagesEnabled=false')
#         chrome_options.add_argument('--block-new-web-contents')
#         chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        
#         # Set user agent
#         user_agent = random.choice(USER_AGENTS)
#         chrome_options.add_argument(f'--user-agent={user_agent}')
#         logging.debug(f"Using User-Agent: {user_agent}")

#         # Configure Selenium Wire options with proxy
#         seleniumwire_options = {
#             'proxy': {
#                 'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY}',
#                 'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY}'
#             }
#         }

#         self.driver = webdriver.Chrome(
#             options=chrome_options,
#             seleniumwire_options=seleniumwire_options
#         )
#         logging.info("Chrome driver initialized successfully")

#     def __del__(self):
#         if hasattr(self, 'driver'):
#             logging.info("Closing Chrome driver")
#             self.driver.quit()

#     def save_results(self):
#         filename = f'property_listings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(self.listings_data, f, ensure_ascii=False, indent=2)
#         logging.info(f"Saved {len(self.listings_data)} listings to {filename}")

#     def make_request(self, url):
#         """Handle requests with JavaScript enabled for image loading"""
#         try:
#             logging.info(f"Requesting URL: {url}")
#             self.driver.get(url)
            
#             # Wait for listings to load
#             WebDriverWait(self.driver, TIMEOUT).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'article.item'))
#             )
#             logging.debug("Listings container loaded")
            
#             # Additional wait for images
#             WebDriverWait(self.driver, TIMEOUT).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'picture img'))
#             )
#             logging.debug("Images loaded")
#             return True
            
#         except Exception as e:
#             logging.error(f"Request failed for {url}: {str(e)}\n{traceback.format_exc()}")
#             return False

#     def parse_listing(self, element):
#         """Enhanced listing parser with image handling"""
#         try:
#             # Get basic listing info
#             listing_data = {
#                 'title': element.find_element(By.CSS_SELECTOR, 'a.item-link').text.strip(),
#                 'price': element.find_element(By.CSS_SELECTOR, '.item-price').text.strip(),
#                 'url': element.find_element(By.CSS_SELECTOR, 'a.item-link').get_attribute('href'),
#                 'scraped_at': datetime.now().isoformat(),
#                 'images': set()  # Using set to avoid duplicates
#             }
            
#             # Get initial visible images
#             images = element.find_elements(By.CSS_SELECTOR, 'picture img')
#             for img in images:
#                 src = img.get_attribute('src')
#                 if src and not src.endswith(('placeholder.png', 'placeholder.webp')):
#                     clean_url = re.sub(r'/blur/\d+_\d+_[^/]+/', '/', src)
#                     listing_data['images'].add(clean_url)
            
#             # Click through image slider if present
#             try:
#                 total_images_element = element.find_element(By.CSS_SELECTOR, '.item-multimedia-pictures')
#                 total_text = total_images_element.text  # Format: "1/9"
#                 total = int(total_text.split('/')[1]) if '/' in total_text else 1
                
#                 if total > 1:
#                     # Updated selector to match the exact button class
#                     next_button = element.find_element(
#                         By.CSS_SELECTOR, 
#                         'button.image-gallery-icon.image-gallery-right-nav.icon-arrow-right'
#                     )
                    
#                     for _ in range(total - 1):
#                         next_button.click()
#                         time.sleep(1)  # Increased delay to ensure image loads
                        
#                         new_images = element.find_elements(By.CSS_SELECTOR, 'picture img')
#                         for img in new_images:
#                             src = img.get_attribute('src')
#                             if src and not src.endswith(('placeholder.png', 'placeholder.webp')):
#                                 clean_url = re.sub(r'/blur/\d+_\d+_[^/]+/', '/', src)
#                                 listing_data['images'].add(clean_url)
            
#             except Exception as e:
#                 logging.warning(f"Error navigating image slider: {str(e)}")
            
#             # Convert set to list for JSON serialization
#             listing_data['images'] = list(listing_data['images'])
#             return listing_data

#         except Exception as e:
#             logging.error(f"Error parsing listing: {str(e)}")
#             return None

#     def scrape_pages(self):
#         """Main scraping logic"""
#         try:
#             logging.info(f"Starting scraping process for {MAX_PAGES} pages")
#             for page in range(1, MAX_PAGES + 1):
#                 logging.info(f"Processing page {page}/{MAX_PAGES}")
                
#                 for attempt in range(MAX_RETRIES):
#                     logging.debug(f"Attempt {attempt + 1}/{MAX_RETRIES} for page {page}")
#                     url = f'https://www.idealista.pt/arrendar-casas/lisboa/pagina-{page}' if page > 1 else 'https://www.idealista.pt/arrendar-casas/lisboa/'
                    
#                     if self.make_request(url):
#                         listings = self.driver.find_elements(By.CSS_SELECTOR, 'article.item')
#                         parsed_listings = list(filter(None, map(self.parse_listing, listings)))
#                         self.listings_data.extend(parsed_listings)
#                         logging.info(f"Page {page} scraped successfully. Found {len(listings)} elements, parsed {len(parsed_listings)} listings")
#                         time.sleep(random.uniform(1, 3))
#                         break
#                     else:
#                         logging.warning(f"Retry {attempt + 1} failed for page {page}")
#                         time.sleep(5)
#                 else:
#                     logging.error(f"Failed to scrape page {page} after {MAX_RETRIES} attempts")
                
#                 if page % 5 == 0:
#                     logging.info(f"Intermediate save at page {page}")
#                     self.save_results()

#             logging.info("Final results save")
#             self.save_results()
#             logging.info("Scraping completed successfully")

#         except Exception as e:
#             logging.error(f"Scraping failed: {str(e)}\n{traceback.format_exc()}")
#         finally:
#             logging.info("Cleaning up resources")
#             self.driver.quit()

# if __name__ == "__main__":
#     scraper = PropertyScraper()
#     scraper.scrape_pages()

import urllib.request
import random

# Using the full proxy URL with session ID and time
proxy_url = 'https://customer-nuno5645_lEtvV-cc-pt-city-lisbon:FQe4vnhF26_wSgy@pr.oxylabs.io:7777'


# Create a proxy handler with the full URL
proxy_handler = urllib.request.ProxyHandler({
    'http': proxy_url,
    'https': proxy_url,
})

# Build and install the opener
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

# Make a request to check if it's working
try:
    response = urllib.request.urlopen('https://ip.oxylabs.io/location')
    print(response.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")