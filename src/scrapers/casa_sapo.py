from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
from src.utils.base_scraper import BaseScraper
import re

class CasaSapoScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Casa SAPO"

    def scrape(self):
        """Scrape houses from Casa SAPO website"""
        total_processed = 0
        total_new_listings = 0

        for site_url in self.urls:
            self.logger.info(f"Starting scrape for Casa SAPO URL: {site_url}", extra={'action': 'SCRAPING'})
            page_num = 1
            max_pages = 2  # Safety limit

            while page_num <= max_pages:
                processed, new_listings = self._process_page(site_url, page_num)
                total_processed += processed
                total_new_listings += new_listings
                page_num += 1

        self.logger.info(f"Finished processing all pages for Casa SAPO", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total houses processed: {total_processed}", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total new listings found: {total_new_listings}", extra={'action': 'PROCESSING'})

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}&pn={page_num}"

        try:
            self.logger.info(f"Processing page {page_num}...", extra={'action': 'SCRAPING'})
            if page_num > 1:
                time.sleep(5)  # Wait between pages
                
            # Configure Chrome
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
            driver.get(current_url)
            time.sleep(random.uniform(8, 12))  # Randomized wait
            
            # Wait for property items to be present
            try:
                property_items = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "property-info-content"))
                )
            except Exception as e:
                self.logger.warning(f"No property items found on page {page_num}: {str(e)}")
                driver.quit()
                return 0, 0

            processed = 0
            new_listings = 0

            for property_item in property_items:
                try:
                    processed += 1
                    
                    # Extract basic information
                    property_info = property_item.find_element(By.CLASS_NAME, "property-info")
                    
                    # Get property type and name
                    type_elem = property_info.find_element(By.CLASS_NAME, "property-type")
                    name = type_elem.text.strip() if type_elem else "N/A"
                    
                    # Get URL
                    url = property_info.get_attribute("href")
                    
                    # Get location
                    location_elem = property_info.find_element(By.CLASS_NAME, "property-location")
                    zone = location_elem.text.strip() if location_elem else "N/A"
                    
                    # Get price
                    price_value_elem = property_info.find_element(By.CLASS_NAME, "property-price-value")
                    price = price_value_elem.text.strip() if price_value_elem else "N/A"
                    
                    # Click to get detailed information
                    try:
                        # Click on the property link
                        driver.execute_script("arguments[0].click();", property_info)
                        time.sleep(random.uniform(3, 5))  # Wait for page to load
                        
                        # Wait for the details to be present
                        detail_features = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "detail-main-features-item"))
                        )
                        
                        # Extract area from detailed features
                        area = "N/A"
                        for feature in detail_features:
                            try:
                                title = feature.find_element(By.CLASS_NAME, "detail-main-features-item-title").text
                                if "ÁREA ÚTIL" or "ÁREA BRUTA" in title: ## these are not the same thing
                                    area = feature.find_element(By.CLASS_NAME, "detail-main-features-item-value").text
                                    break
                            except:
                                continue
                        
                        # Get description from detailed view
                        try:
                            description_elem = driver.find_element(By.CLASS_NAME, "property-description")
                            description = description_elem.text.strip()
                        except:
                            description = "N/A"
                        
                        # Go back to the listing page
                        driver.back()
                        time.sleep(random.uniform(2, 4))  # Wait for listing page to reload
                        
                        # Wait for the property list to be present again
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "property-info-content"))
                        )
                        
                    except Exception as detail_error:
                        self.logger.warning(f"Error getting detailed information: {str(detail_error)}")
                        area = "N/A"
                        description = "N/A"
                    
                    # Extract bedrooms from property type (e.g., "Apartamento T2" -> "2")
                    bedrooms = "N/A"
                    if name and "T" in name:
                        try:
                            bedrooms = name.split("T")[1][0]  # Get first character after T
                        except:
                            bedrooms = "N/A"
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Source, ScrapedAt
                    info_list = [
                        name,           # Name
                        zone,           # Zone
                        price,          # Price
                        url,            # URL
                        bedrooms,       # Bedrooms
                        area,           # Area
                        "0",            # Floor (default to "0" as we don't have this info)
                        description,    # Description
                        "Casa SAPO",    # Source
                        None           # ScrapedAt (will be filled by save_to_excel)
                    ]
                    
                    if self.save_to_excel(info_list):
                        new_listings += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing house: {str(e)}", exc_info=True)
                    continue

            driver.quit()
            return processed, new_listings

        except Exception as e:
            self.logger.error(f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return 0, 0

