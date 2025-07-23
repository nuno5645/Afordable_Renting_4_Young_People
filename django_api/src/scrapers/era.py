from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager

class EraScraper(BaseScraper):
    def __init__(self, logger, url):
        super().__init__(logger)
        self.url = url
        self.source = "ERA"
        self.location_manager = LocationManager()

    def scrape(self):
        """Scrape houses from ERA website"""
        self._log('info', f"Starting scrape for URL: {self.url}")
        
        try:
            # Configure Chrome for dynamic content - disable headless to allow JS execution
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Remove headless for now
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Enable JavaScript and disable blocking
            chrome_options.add_argument("--enable-javascript")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(options=chrome_options)
            
            # Set page load timeout
            driver.set_page_load_timeout(30)
            
            self._log('info', "Accessing website...")
            driver.get(self.url)
            
            # Wait much longer and trigger multiple interactions
            self._log('info', "Waiting extended time for AJAX content to load...")
            time.sleep(5)
            
            # Scroll down to trigger lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Click the Prédios button to load property content
            try:
                predios_button = driver.find_element(By.CSS_SELECTOR, "button.btn-multi-selection")
                if predios_button.is_displayed():
                    driver.execute_script("arguments[0].click();", predios_button)
                    self._log('info', "Clicked Prédios button")
                    time.sleep(2)
                    
                    # Click again
                    driver.execute_script("arguments[0].click();", predios_button)
                    self._log('info', "Clicked Prédios button again")
                    time.sleep(5)
                else:
                    self._log('warning', "Prédios button not visible")
                    
            except Exception as e:
                self._log('error', f"Error clicking Prédios button: {str(e)}")
                
            # Final long wait for content
            time.sleep(10)
            
            # Check current URL to see if we were redirected
            current_url = driver.current_url
            self._log('info', f"Current URL after navigation: {current_url}")
            
            # Check page title to verify we're on the right site
            page_title = driver.title
            self._log('info', f"Page title: {page_title}")
            
            # If we're on Idealista instead of ERA, this is the problem
            if "idealista" in current_url.lower() or "idealista" in page_title.lower():
                self._log('error', f"REDIRECT DETECTED: We were redirected from ERA to Idealista!")
                self._log('error', f"Original URL: {self.url}")
                self._log('error', f"Current URL: {current_url}")
                driver.quit()
                return
                
            # Look for ERA-specific elements to confirm we're on the right site
            era_indicators = driver.find_elements(By.CSS_SELECTOR, "[class*='era'], [id*='era'], [href*='era.pt']")
            if not era_indicators:
                self._log('warning', "No ERA-specific elements found. We might not be on ERA website.")
            
            # Save initial page content for debugging
            initial_content = driver.page_source
            debug_file = '/home/hugoa/repos/Afordable_Renting_4_Young_People/debug_output.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(initial_content)
                self._log('info', f"Saved initial page content to {debug_file}")
            
            # Wait for dynamic content to load by checking for actual property listings
            self._log('info', "Waiting for property listings to load...")
            
            # Wait up to 30 seconds for properties to appear
            property_loaded = False
            for attempt in range(30):
                try:
                    # Check for actual ERA property cards based on the real HTML structure
                    property_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "div.card.col-12, .content.p-3, div.property_details--container")
                    
                    if property_elements:
                        self._log('info', f"Found {len(property_elements)} property elements after {attempt + 1} seconds")
                        property_loaded = True
                        break
                    
                    # Also check for the main results container
                    results_container = driver.find_elements(By.CSS_SELECTOR, 
                        ".cards-container, .list-all-properties, .list-results")
                    if results_container:
                        self._log('info', f"Found results container after {attempt + 1} seconds, checking for properties...")
                        # Wait a bit more for properties to populate
                        time.sleep(2)
                        property_elements = driver.find_elements(By.CSS_SELECTOR, 
                            "div.card.col-12, .content.p-3, div.property_details--container")
                        if property_elements:
                            self._log('info', f"Found {len(property_elements)} property elements in results container")
                            property_loaded = True
                            break
                    
                    # Log progress every 5 seconds instead of 10
                    if (attempt + 1) % 5 == 0:
                        self._log('info', f"Still waiting for properties... ({attempt + 1}/30 seconds)")
                    
                    time.sleep(1)
                    
                except Exception as e:
                    self._log('warning', f"Error checking for property elements: {str(e)}")
                    time.sleep(1)
            
            if not property_loaded:
                self._log('warning', "Timeout: No property listings found after 30 seconds")
            
            # Alternative: try direct API endpoint approach
            if not property_loaded:
                self._log('info', "Attempting to find AJAX endpoints...")
                
                # Check network logs for AJAX calls (basic approach)
                try:
                    # Look for common ERA API patterns in page source
                    page_source = driver.page_source
                    import re
                    
                    # Look for API endpoints in JavaScript
                    api_patterns = [
                        r'/api/[^"\']*',
                        r'/services/[^"\']*', 
                        r'\.ashx[^"\']*',
                        r'ServicesModule[^"\']*'
                    ]
                    
                    found_endpoints = []
                    for pattern in api_patterns:
                        matches = re.findall(pattern, page_source, re.IGNORECASE)
                        found_endpoints.extend(matches)
                    
                    if found_endpoints:
                        self._log('info', f"Found potential API endpoints: {found_endpoints[:3]}")
                        
                except Exception as e:
                    self._log('warning', f"Error searching for API endpoints: {str(e)}")
                    
                # Try refreshing and waiting again
                self._log('info', "Refreshing page and waiting longer...")
                driver.refresh()
                time.sleep(20)
                
            # Try clicking any filter/search buttons to trigger content load
            try:
                # Look for buttons that might trigger property loading
                trigger_buttons = [
                    "button.btn-multi-selection",
                    "button[class*='search']",
                    "button[class*='filter']",
                    ".search-btn",
                    ".filter-btn"
                ]
                
                for btn_selector in trigger_buttons:
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, btn_selector)
                        if button.is_displayed() and button.is_enabled():
                            driver.execute_script("arguments[0].click();", button)
                            self._log('info', f"Clicked trigger button: {btn_selector}")
                            time.sleep(5)  # Wait for potential AJAX response
                            break
                    except:
                        continue
                        
            except Exception as e:
                self._log('warning', f"Error clicking trigger buttons: {str(e)}")
                        
            # Alternative approach: use WebDriverWait to wait for content
            try:
                self._log('info', "Using WebDriverWait to wait for property content...")
                wait = WebDriverWait(driver, 30)
                
                # Wait for any property-related content to appear
                property_indicators = [
                    (By.CSS_SELECTOR, "div.property-card"),
                    (By.CSS_SELECTOR, "article.property-card"), 
                    (By.CSS_SELECTOR, ".listing-card"),
                    (By.CSS_SELECTOR, "[data-property-id]"),
                    (By.CSS_SELECTOR, ".search-result-item"),
                    (By.CSS_SELECTOR, ".property-listing"),
                    (By.PARTIAL_LINK_TEXT, "€"),  # Look for price elements
                    (By.CSS_SELECTOR, "[class*='property']:not(.modal)"),
                ]
                
                element_found = False
                for by, selector in property_indicators:
                    try:
                        element = wait.until(EC.presence_of_element_located((by, selector)))
                        if element:
                            self._log('info', f"Found property content using selector: {selector}")
                            element_found = True
                            break
                    except:
                        continue
                        
                if not element_found:
                    self._log('warning', "WebDriverWait did not find any property content")
                    
            except Exception as e:
                self._log('warning', f"Error with WebDriverWait: {str(e)}")
            
            # Get final page content
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            self._log('info', "Successfully retrieved page content")

            driver.quit()

            # Check if we're actually on ERA by looking for ERA-specific elements
            era_specific_elements = soup.find_all(string=lambda text: text and 'era' in text.lower())
            idealista_elements = soup.find_all(string=lambda text: text and 'idealista' in text.lower())
            
            if idealista_elements and not era_specific_elements:
                self._log('error', "Page content indicates we are on Idealista, not ERA!")
                self._log('error', f"Found {len(idealista_elements)} Idealista references")
                return

            # Extract search results metadata
            self._extract_search_metadata(soup)

            # Debug: Check what elements we can find
            self._log('info', "Debugging page structure...")
            
            # Try different selectors to find houses - updated for current ERA structure
            possible_selectors = [
                # Current ERA structure based on actual HTML
                "div.content.p-3",  # This is the main property content container
                "div.card.col-12",  # The card wrapper
                
                # Backup selectors
                "div.property-card",
                "article.property-card", 
                ".listing-card",
                ".search-result-item",
                "[data-property-id]",
                ".property-listing",
                ".result-item",
                
                # Legacy selectors as fallback
                ".property-item",
                ".listing-item", 
                ".card",
                ".search-result",
            ]
            
            house_div = []
            selected_selector = None
            
            for selector in possible_selectors:
                elements = soup.select(selector)
                self._log('info', f"Selector '{selector}': found {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    # Log first element's classes for debugging
                    first_elem = elements[0]
                    classes = first_elem.get('class', [])
                    self._log('info', f"First element classes: {classes}")
                    
                    # Exclude modal elements and other non-property elements
                    if any(cls in ' '.join(classes).lower() for cls in ['modal', 'popup', 'dialog', 'overlay']):
                        self._log('info', f"Skipping selector '{selector}' - contains modal/popup elements")
                        continue
                    
                    # Check if this looks like property listings
                    # Look for typical property indicators in ERA structure
                    has_price = first_elem.find(string=lambda text: text and ('€' in text or 'Sob Consulta' in text))
                    has_location = first_elem.find(string=lambda text: text and any(word in text.lower() for word in ['lisboa', 'porto', 'sintra', 'cascais', 'torres vedras', 'odivelas', 'loures']))
                    has_property_info = first_elem.find(string=lambda text: text and any(word in text.lower() for word in ['t0', 't1', 't2', 't3', 't4', 't5', 'm²', 'quartos', 'apartamento', 'moradia']))
                    has_property_type = first_elem.find('div', class_="property_details--type")
                    
                    # Give higher priority to elements with actual property data
                    if has_price or has_location or has_property_info or has_property_type:
                        house_div = elements
                        selected_selector = selector
                        self._log('info', f"Selected selector '{selector}' with {len(house_div)} property elements (has property data)")
                        break
                    elif 'content' in ' '.join(classes).lower() and len(elements) >= 3:
                        # Accept content elements if there are several (ERA uses div.content.p-3)
                        house_div = elements
                        selected_selector = selector
                        self._log('info', f"Selected selector '{selector}' with {len(house_div)} potential property elements")
                        # Don't break yet, continue looking for better matches
                        
            # Additional check: if we still haven't found good property listings, 
            # try to find them in a results container
            if not house_div or len(house_div) < 3:
                self._log('info', "Searching in results containers...")
                container_selectors = [
                    ".search-results",
                    ".property-results", 
                    ".results-container",
                    "#search-results",
                    ".results-list",
                    ".property-list"
                ]
                
                for container_sel in container_selectors:
                    container = soup.select(container_sel)
                    if container:
                        self._log('info', f"Found results container: {container_sel}")
                        # Look for properties within the container
                        for prop_sel in possible_selectors[:10]:  # Try top selectors
                            container_props = container[0].select(prop_sel)
                            if container_props and len(container_props) > len(house_div):
                                house_div = container_props
                                selected_selector = f"{container_sel} {prop_sel}"
                                self._log('info', f"Found {len(house_div)} properties in container with {prop_sel}")
                                break
                        if house_div:
                            break
                        
            # Fallback to the problematic selector if nothing else worked
            if not house_div:
                house_div = soup.find_all(class_="content p-3")
                if house_div:
                    selected_selector = "class='content p-3'"
                    
            if not house_div:
                # Try alternative selectors
                house_div = soup.find_all("div", class_="content")
                if house_div:
                    selected_selector = "div.content"
                    
            if not house_div:
                house_div = soup.select(".property-card, .card, [class*='property']")
                if house_div:
                    selected_selector = "general property selectors"
                    
            if not house_div:
                self._log('warning', "No houses found. The website structure might have changed.")
                # Save page content for debugging
                debug_file = '/home/hugoa/repos/Afordable_Renting_4_Young_People/era_debug_no_properties.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                    self._log('info', f"Saved page content to {debug_file} for debugging")
                return

            self._log('info', f"Found {len(house_div)} houses to process using selector: {selected_selector}")

            for house in house_div:
                try:
                    # Check if this is a development property
                    is_development = 'is-development' in house.parent.get('class', []) if house.parent else False
                    
                    if is_development:
                        self._process_development_property(house)
                    else:
                        self._process_regular_property(house)
                        
                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                    continue

            self._log('info', f"Finished processing URL: {self.url}")

        except Exception as e:
            self._log('error', f"Error accessing website: {str(e)}", exc_info=True)
    
    def _process_regular_property(self, house):
        """Process regular property listing"""
        # Extract basic property information
        property_type_elem = house.find("div", class_="property_details--type")
        if not property_type_elem:
            # Fallback to old structure
            property_type_elem = house.find("p", class_="property-type d-block mb-1")
        
        name = f'{property_type_elem.text.strip()} ERA' if property_type_elem else 'Propriedade ERA'
        
        # Extract location
        location_elem = house.find('div', class_="property_details--location")
        if not location_elem:
            # Fallback to old structure
            location_elem = house.find('div', class_="col-12 location")
        
        zone = location_elem.text.strip() if location_elem else "N/A"
        
        # Extract freguesia and concelho
        freguesia, concelho = self.location_manager.extract_location(zone)
        
        self._log('info', f"Processing: {name} in {zone}")
        self._log('info', f"Freguesia: {freguesia}, Concelho: {concelho}")
        
        # Extract price
        price_elem = house.find('p', class_="price-value")
        price = price_elem.text.strip() if price_elem else "N/A"
        
        # Extract URL
        url_elem = house.find('a', class_="card-anchor") or house.find('a')
        url = url_elem['href'] if url_elem and url_elem.get('href') else "N/A"
        if url != "N/A" and not url.startswith('http'):
            url = f"https://www.era.pt{url}"
        
        # Extract property details
        details = self._extract_property_details(house)
        
        # Extract images
        images = self._extract_images(house)
        
        # Extract energy certificate
        energy_cert = self._extract_energy_certificate(house)
        
        # Extract amenities/features
        amenities = self._extract_amenities(house)
        
        # Extract status (new, reserved, sold)
        status = self._extract_property_status(house)
        
        description = "No description"  # ERA website doesn't provide description in listing
        
        # Enhanced info list with all possible values
        info_list = [
            name,
            zone,
            price,
            url,
            details.get('bedrooms', 'N/A'),
            details.get('area', 'N/A'),
            details.get('floor', 'N/A'),
            description,
            freguesia if freguesia else "N/A",
            concelho if concelho else "N/A",
            "ERA",
            None,  # ScrapedAt will be filled by save_to_excel
            details.get('bathrooms', 'N/A'),
            details.get('gross_area', 'N/A'),
            details.get('land_area', 'N/A'),
            details.get('parking', 'N/A'),
            energy_cert,
            status,
            amenities,
            images
        ]
        
        self.save_to_database(info_list)
    
    def _process_development_property(self, house):
        """Process development property listing"""
        try:
            # Extract development name
            name_elem = house.find('div', class_="property_details--name")
            name = name_elem.text.strip() if name_elem else "Empreendimento ERA"
            
            # Extract location
            location_elem = house.find('div', class_="property_details--location")
            zone = location_elem.text.strip() if location_elem else "N/A"
            
            # Extract freguesia and concelho
            freguesia, concelho = self.location_manager.extract_location(zone)
            
            # Extract prices (buy and rent)
            buy_price = "N/A"
            rent_price = "N/A"
            
            buy_price_elem = house.find('div', class_="comprar price")
            if buy_price_elem:
                price_value = buy_price_elem.find('p', class_="price-value")
                if price_value:
                    buy_price = price_value.text.strip()
            
            rent_price_elem = house.find('div', class_="arrendar price")
            if rent_price_elem:
                price_value = rent_price_elem.find('p', class_="price-value")
                if price_value:
                    rent_price = price_value.text.strip()
            
            # Extract URL
            url_elem = house.find('a')
            url = url_elem['href'] if url_elem and url_elem.get('href') else "N/A"
            if url != "N/A" and not url.startswith('http'):
                url = f"https://www.era.pt{url}"
            
            # Extract available fractions
            available_elem = house.find('div', class_="property_details--available")
            available = available_elem.text.strip() if available_elem else "N/A"
            
            # Extract fraction details
            fractions = self._extract_development_fractions(house)
            
            # Extract images
            images = self._extract_images(house)
            
            self._log('info', f"Processing development: {name} in {zone}")
            
            # Save development info
            info_list = [
                name,
                zone,
                f"Comprar: {buy_price}, Arrendar: {rent_price}",
                url,
                fractions.get('types', 'N/A'),
                fractions.get('details', 'N/A'),
                "N/A",  # Floor
                f"Empreendimento com {available}",
                freguesia if freguesia else "N/A",
                concelho if concelho else "N/A",
                "ERA",
                None,  # ScrapedAt
                "N/A",  # Bathrooms
                "N/A",  # Gross area
                "N/A",  # Land area
                "N/A",  # Parking
                "N/A",  # Energy cert
                "Empreendimento",
                [],  # Amenities
                images
            ]
            
            self.save_to_database(info_list)
            
        except Exception as e:
            self._log('error', f"Error processing development: {str(e)}", exc_info=True)
    
    def _extract_development_fractions(self, house):
        """Extract fraction details from development"""
        fractions = {'types': [], 'details': []}
        
        try:
            fraction_cards = house.find_all('a', class_="fraction-card")
            
            for card in fraction_cards:
                # Extract fraction type (T1, T2, etc.)
                type_elem = card.find('span', class_="fraction-type")
                count_elem = card.find('span', class_="fraction-count")
                
                if type_elem and count_elem:
                    fraction_type = type_elem.text.strip()
                    fraction_count = count_elem.text.strip()
                    fractions['types'].append(f"{fraction_type} {fraction_count}")
                
                # Extract features (bedrooms, bathrooms)
                features = card.find_all('span', class_="feature")
                feature_details = []
                
                for feature in features:
                    feature_text = feature.get_text(strip=True)
                    feature_details.append(feature_text)
                
                if feature_details:
                    fractions['details'].append(' - '.join(feature_details))
                    
        except Exception as e:
            self._log('warning', f"Error extracting development fractions: {str(e)}")
            
        return {
            'types': ', '.join(fractions['types']) if fractions['types'] else 'N/A',
            'details': ' | '.join(fractions['details']) if fractions['details'] else 'N/A'
        }
    
    def _extract_property_details(self, house):
        """Extract detailed property information"""
        details = {}
        
        try:
            # Find property details section
            details_section = house.find('div', class_="property-details")
            if details_section:
                detail_items = details_section.find_all('div', class_="detail")
                
                for i, detail in enumerate(detail_items):
                    span = detail.find('span', class_="d-inline-flex")
                    if span:
                        value = span.text.strip()
                        
                        # Determine detail type based on SVG title or position
                        svg = detail.find('svg')
                        if svg:
                            title_attr = svg.get('data-original-title', '')
                            
                            if 'Quartos' in title_attr or i == 0:
                                details['bedrooms'] = f'T{value}' if value.isdigit() else value
                            elif 'Casas de Banho' in title_attr or i == 1:
                                details['bathrooms'] = value
                            elif 'Área Útil' in title_attr or (i == 2 and 'Piso' not in title_attr):
                                details['area'] = f'{value} m²' if value.isdigit() else value
                            elif 'Área Bruta Privativa' in title_attr or i == 3:
                                details['gross_area'] = f'{value} m²' if value.isdigit() else value
                            elif 'Área Terreno' in title_attr:
                                details['land_area'] = f'{value} m²' if value.isdigit() else value
                            elif 'Piso' in title_attr:
                                details['floor'] = value
                            elif 'Estacionamento' in title_attr:
                                details['parking'] = value
                                
            # Fallback to old structure if new structure not found
            if not details:
                spans = house.find_all("span", class_="d-inline-flex")
                if len(spans) >= 4:
                    details['bedrooms'] = f'T{spans[0].text.strip()}'
                    details['bathrooms'] = spans[1].text.strip() if len(spans) > 1 else 'N/A'
                    details['area'] = f'{spans[3].text.strip()} m²' if len(spans) > 3 else 'N/A'
                    
        except Exception as e:
            self._log('warning', f"Error extracting property details: {str(e)}")
            
        return details
    
    def _extract_images(self, house):
        """Extract property images"""
        images = []
        
        try:
            # Find carousel slides
            carousel = house.find('div', class_="carousel")
            if carousel:
                slides = carousel.find_all('div', class_="slide")
                
                for slide in slides:
                    style = slide.get('style', '')
                    if 'background-image: url(' in style:
                        # Extract URL from style attribute
                        start = style.find('url("') + 5
                        end = style.find('")', start)
                        if start > 4 and end > start:
                            image_url = style[start:end]
                            cleaned_url = self._clean_image_url(image_url)
                            if cleaned_url and cleaned_url not in images:
                                images.append(cleaned_url)
                                
        except Exception as e:
            self._log('warning', f"Error extracting images: {str(e)}")
            
        return images
    
    def _extract_energy_certificate(self, house):
        """Extract energy certificate information"""
        try:
            # Look for energy certificate icon/indicator
            energy_elem = house.find('svg', {'data-original-title': 'Certificado Energético'})
            if energy_elem:
                return "Available"
            
            # Check if there's any energy-related information
            if house.find(string=lambda text: text and 'energético' in text.lower()):
                return "Available"
                
        except Exception as e:
            self._log('warning', f"Error extracting energy certificate: {str(e)}")
            
        return "N/A"
    
    def _extract_amenities(self, house):
        """Extract property amenities and features"""
        amenities = []
        
        try:
            # Look for elevator
            if house.find('svg', {'data-original-title': 'Elevador'}):
                amenities.append('Elevador')
                
            # Look for parking
            if house.find('svg', {'data-original-title': 'Estacionamento'}):
                amenities.append('Estacionamento')
                
            # Look for energy certificate
            if house.find('svg', {'data-original-title': 'Certificado Energético'}):
                amenities.append('Certificado Energético')
                
            # Look for other amenities in icons-badge
            icons_badge = house.find('div', class_="icons-badge")
            if icons_badge:
                # Could contain additional amenity icons
                pass
                
        except Exception as e:
            self._log('warning', f"Error extracting amenities: {str(e)}")
            
        return amenities
    
    def _extract_property_status(self, house):
        """Extract property status (new, reserved, sold, etc.)"""
        try:
            # Check for status labels
            if house.find('div', class_="card-label"):
                label = house.find('span', class_="group-2")
                if label:
                    return label.text.strip()
                    
            # Check for highlights (reserved, sold)
            if house.find('div', class_="card-highlight"):
                if house.find('div', class_="card-highlight sold"):
                    return "Vendido"
                elif house.find('div', class_="card-highlight"):
                    highlight = house.find('div', class_="card-highlight")
                    if highlight and 'reserved' in highlight.get('class', []):
                        return "Reservado"
                        
            # Check for development properties
            if 'is-development' in house.get('class', []):
                return "Empreendimento"
                
        except Exception as e:
            self._log('warning', f"Error extracting property status: {str(e)}")
            
        return "Disponível"
    
    def _extract_search_metadata(self, soup):
        """Extract search results metadata"""
        try:
            # Extract total results count
            results_elem = soup.find('span', class_="mobile-results__label")
            if results_elem:
                results_text = results_elem.text.strip()
                self._log('info', f"Search results: {results_text}")
            
            # Extract current sorting option
            sorting_elem = soup.find('span', class_="selected-value")
            if sorting_elem:
                sorting = sorting_elem.text.strip()
                self._log('info', f"Current sorting: {sorting}")
                
            # Extract available sorting options
            sort_options = soup.find_all('span', class_="position-relative d-block mx-2 p-2 pt-3 border-bottom")
            if sort_options:
                options = [opt.text.strip() for opt in sort_options]
                self._log('info', f"Available sorting options: {', '.join(options)}")
                
        except Exception as e:
            self._log('warning', f"Error extracting search metadata: {str(e)}")
    
    def _clean_image_url(self, url):
        """Clean and validate image URLs"""
        if not url:
            return None
            
        # Remove URL encoding artifacts
        url = url.replace('%2b', '+').replace('%3d', '=').replace('%2f', '/')
        
        # Ensure proper HTTPS
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith('http'):
            url = 'https://' + url
            
        return url
