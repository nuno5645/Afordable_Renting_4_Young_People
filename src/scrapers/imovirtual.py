from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from src.utils.base_scraper import BaseScraper

class ImoVirtualScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Imovirtual"

    def scrape(self):
        """Scrape houses from ImoVirtual website"""
        total_processed = 0
        total_new_listings = 0

        for site_url in self.urls:
            self.logger.info(f"Starting scrape for ImoVirtual URL: {site_url}", extra={'action': 'SCRAPING'})
            page_num = 1
            max_pages = 2  # Safety limit

            while page_num <= max_pages:
                processed, new_listings = self._process_page(site_url, page_num)
                total_processed += processed
                total_new_listings += new_listings
                page_num += 1

        self.logger.info(f"Finished processing all pages for ImoVirtual", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total houses processed: {total_processed}", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total new listings found: {total_new_listings}", extra={'action': 'PROCESSING'})

    def _process_page(self, url, page_num):
        """Process a single page of listings"""
        if page_num == 1:
            current_url = url
        else:
            current_url = f"{url}&page={page_num}"

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
            
            # Find and click all description expanders
            try:
                # Wait for articles to be present
                articles = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-cy='listing-item']"))
                )
                
                # Process each article with Selenium first
                selenium_descriptions = []
                for article in articles:
                    try:
                        # Find and click "Ver descrição do anúncio"
                        try:
                            description_button = article.find_element(By.XPATH, ".//div[text()='Ver descrição do anúncio']")
                            driver.execute_script("arguments[0].click()", description_button)
                            time.sleep(random.uniform(0.5, 1))  # Wait for description to load
                            
                            # Now get the expanded description
                            description_text = article.find_element(By.CSS_SELECTOR, "div.css-1b63dzw").text
                            self.logger.info(f"Raw description text: {description_text}", extra={'action': 'DEBUG'})
                            
                            if not description_text:
                                # Try alternate selector if first one is empty
                                description_text = article.find_element(By.CSS_SELECTOR, "div[class*='e1u1ec23']").text
                                self.logger.info(f"Alternate description text: {description_text}", extra={'action': 'DEBUG'})
                            
                            # Clean up the text
                            description_text = description_text.strip()
                            self.logger.info(f"Final cleaned description for listing: {description_text}", extra={'action': 'DEBUG'})
                            
                        except Exception as click_error:
                            self.logger.warning(f"Error clicking or getting description: {str(click_error)}")
                            description_text = "N/A"
                        
                        selenium_descriptions.append(description_text if description_text else "N/A")
                    except Exception as e:
                        self.logger.warning(f"Error processing article: {str(e)}")
                        selenium_descriptions.append("N/A")
                # Wait a bit for all descriptions to be fully expanded
                time.sleep(2)
            except Exception as e:
                self.logger.warning(f"Error expanding descriptions: {str(e)}")
                selenium_descriptions = []
            
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
            driver.quit()
            
            # Check for blocking
            if "Request blocked" in page_content or "ERROR: The request could not be satisfied" in page_content:
                self.logger.error("Access blocked by CloudFront - possible bot detection", exc_info=True)
                return 0, 0
            
            articles = soup.find_all('article', {'data-cy': 'listing-item'})
            if not articles:
                self.logger.warning(f"No articles found on page {page_num}")
                return 0, 0

            processed = 0
            new_listings = 0

            for idx, article in enumerate(articles):
                try:
                    processed += 1
                    
                    # Extract house information
                    title_elem = article.find('p', {'data-cy': 'listing-item-title'})
                    name = title_elem.text.strip() if title_elem else "N/A"
                    
                    link_elem = article.find('a', {'data-cy': 'listing-item-link'})
                    url = f"https://www.imovirtual.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else "N/A"
                    
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
                    
                    # Debug logging for descriptions
                    self.logger.info(f"Description for {name}: {description}", extra={'action': 'DEBUG'})
                    
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
                        "Imovirtual",   # Source
                        None           # ScrapedAt (will be filled by save_to_excel)
                    ]
                    
                    if self.save_to_excel(info_list):
                        new_listings += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing house: {str(e)}", exc_info=True)
                    continue

            return processed, new_listings

        except Exception as e:
            self.logger.error(f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return 0, 0
