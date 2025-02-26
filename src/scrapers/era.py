from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from src.utils.base_scraper import BaseScraper
from src.utils.location_manager import LocationManager

class EraScraper(BaseScraper):
    def __init__(self, logger, url):
        super().__init__(logger)
        self.url = url
        self.source = "ERA"
        self.location_manager = LocationManager()
        self._initialize_status()

    def scrape(self):
        """Scrape houses from ERA website"""
        self._log('info', f"Starting scrape for URL: {self.url}")
        
        try:
            # Configure Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)
            self._log('info', "Accessing website...")
            driver.get(self.url)
            time.sleep(5)  # Wait for page load

            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self._log('info', "Successfully retrieved page content")

            driver.quit()

            house_div = soup.find_all(class_="content p-3")
            if not house_div:
                self._log('warning', "No houses found. The website structure might have changed.")
                return

            self._log('info', f"Found {len(house_div)} houses to process")
            processed = 0
            new_listings = 0

            for house in house_div:
                try:
                    processed += 1
                    
                    # Extract house information
                    name = f'{house.find("p", class_="property-type d-block mb-1").text} ERA'
                    zone = house.find('div', class_="col-12 location").text.strip()
                    
                    # Extract freguesia and concelho
                    freguesia, concelho = self.location_manager.extract_location(zone)
                    
                    self._log('info', f"Freguesia: {freguesia}, Concelho: {concelho}")
                    
                    price = house.find('p', class_="price-value").text
                    url = house.find('a')['href']
                    bedrooms = f'T{house.find_all("span", class_="d-inline-flex")[0].text}'
                    area = house.find_all("span", class_="d-inline-flex")[3].text
                    description = "No description"  # ERA website doesn't provide description in listing
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt
                    info_list = [
                        name,
                        zone,
                        price,
                        url,
                        bedrooms,
                        area,
                        "N/A",  # Floor not available
                        description,
                        freguesia if freguesia else "N/A",
                        concelho if concelho else "N/A",
                        "ERA",
                        None  # ScrapedAt will be filled by save_to_excel
                    ]
                    
                    if self.save_to_excel(info_list):
                        new_listings += 1
                    
                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                    continue

            self._log('info', f"Finished processing URL: {self.url}")
            self._log('info', f"Total houses processed: {processed}")
            self._log('info', f"New listings found: {new_listings}")

        except Exception as e:
            self._log('error', f"Error accessing website: {str(e)}", exc_info=True)
