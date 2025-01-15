from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from src.utils.base_scraper import BaseScraper

class RemaxScraper(BaseScraper):
    def __init__(self, logger, urls):
        super().__init__(logger)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.source = "Remax"

    def scrape(self):
        """Scrape houses from Remax website"""
        total_processed = 0
        total_new_listings = 0

        for site_url in self.urls:
            processed, new_listings = self._process_url(site_url)
            total_processed += processed
            total_new_listings += new_listings

        self.logger.info(f"Finished processing all Remax URLs", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total houses processed: {total_processed}", extra={'action': 'PROCESSING'})
        self.logger.info(f"Total new listings found: {total_new_listings}", extra={'action': 'PROCESSING'})

    def _process_url(self, url):
        """Process a single Remax URL"""
        self.logger.info(f"Starting scrape for Remax URL: {url}", extra={'action': 'SCRAPING'})
        
        try:
            # Configure Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Accessing website...", extra={'action': 'SCRAPING'})
            driver.get(url)
            time.sleep(4)  # Wait for page load

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self.logger.info("Successfully retrieved page content", extra={'action': 'PROCESSING'})

            driver.quit()

            house_div = soup.find_all('div', class_="col-12 col-sm-6 col-md-6 col-lg-4 col-xl-3 result")
            if not house_div:
                self.logger.warning("No houses found. The website structure might have changed.")
                return 0, 0

            self.logger.info(f"Found {len(house_div)} houses to process", extra={'action': 'PROCESSING'})
            processed = 0
            new_listings = 0

            for house in house_div:
                try:
                    processed += 1
                    
                    # Extract house information
                    name = f'{house.find("li", class_="listing-type").text.strip()} Remax'
                    zone = house.find('h2', class_='listing-address').find('span').text.strip()
                    price = house.find('p', class_='listing-price').text.strip()
                    url = f"https://www.remax.pt{house.find('a')['href']}"
                    bedrooms = str("T" + house.find('li', class_='listing-bedroom').text.strip())
                    area = house.find('li', class_='listing-area').text.strip()
                    description = house.find('span', id='listing-description-tags').text.replace("-", " ")
                    
                    info_list = [name, zone, price, url, bedrooms, area, description]
                    
                    if self.save_to_excel(info_list):
                        new_listings += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing house: {str(e)}", exc_info=True)
                    continue

            return processed, new_listings

        except Exception as e:
            self.logger.error(f"Error accessing website: {str(e)}", exc_info=True)
            return 0, 0
