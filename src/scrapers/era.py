from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from src.utils.base_scraper import BaseScraper

class EraScraper(BaseScraper):
    def __init__(self, logger, url):
        super().__init__(logger)
        self.url = url
        self.source = "ERA"

    def scrape(self):
        """Scrape houses from ERA website"""
        self.logger.info(f"Starting scrape for ERA URL: {self.url}", extra={'action': 'SCRAPING'})
        
        try:
            # Configure Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Accessing website...", extra={'action': 'SCRAPING'})
            driver.get(self.url)
            time.sleep(5)  # Wait for page load

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self.logger.info("Successfully retrieved page content", extra={'action': 'PROCESSING'})

            driver.quit()

            house_div = soup.find_all(class_="content p-3")
            if not house_div:
                self.logger.warning("No houses found. The website structure might have changed.")
                return

            self.logger.info(f"Found {len(house_div)} houses to process", extra={'action': 'PROCESSING'})
            processed = 0
            new_listings = 0

            for house in house_div:
                try:
                    processed += 1
                    
                    # Extract house information
                    name = f'{house.find("p", class_="property-type d-block mb-1").text} ERA'
                    zone = house.find('div', class_="col-12 location").text
                    price = house.find('p', class_="price-value").text
                    url = house.find('a')['href']
                    bedrooms = f'T{house.find_all("span", class_="d-inline-flex")[0].text}'
                    area = house.find_all("span", class_="d-inline-flex")[3].text
                    description = "No description"  # ERA website doesn't provide description in listing
                    
                    info_list = [name, zone, price, url, bedrooms, area, description]
                    
                    if self.save_to_excel(info_list):
                        new_listings += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing house: {str(e)}", exc_info=True)
                    continue

            self.logger.info(f"Finished processing URL: {self.url}", extra={'action': 'PROCESSING'})
            self.logger.info(f"Total houses processed: {processed}", extra={'action': 'PROCESSING'})
            self.logger.info(f"New listings found: {new_listings}", extra={'action': 'PROCESSING'})

        except Exception as e:
            self.logger.error(f"Error accessing website: {str(e)}", exc_info=True)
