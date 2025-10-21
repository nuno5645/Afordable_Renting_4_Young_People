import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime, timedelta
try:
    from src.utils.base_scraper import BaseScraper
    from src.utils.location_manager import LocationManager
except Exception as e:
    from utils.base_scraper import BaseScraper
    from utils.location_manager import LocationManager
from config.settings import IDEALISTA_MAX_REQUESTS_PER_HOUR
from houses.models import House


class IdealistaScraper(BaseScraper):
    def __init__(self, logger, url, api_key, listing_type='rent'):
        super().__init__(logger, listing_type)
        # Convert single URL to list if needed
        self.url = [url] if isinstance(url, str) else url
        self.api_key = api_key
        self.source = "Idealista"
        self.last_run_file = "data/last_run_times.json"
        self.location_manager = LocationManager()
        self._load_request_history()
        self._load_existing_urls()

    def _load_existing_urls(self):
        """Load existing property URLs from the database to avoid duplicates"""
        self.existing_urls = set()
        try:
            # Get all URLs from the House model where source is Idealista
            urls = House.objects.filter(source="Idealista").values_list('url', flat=True)
            self.existing_urls = set(urls)
            self._log('info', f"Loaded {len(self.existing_urls)} existing property URLs from database")
        except Exception as e:
            self._log('warning', f"Error loading existing URLs: {str(e)}")
            # Continue with an empty set if there was an error
            self.existing_urls = set()

    def _load_request_history(self):
        """Load the request history from JSON file"""
        try:
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    data = json.load(f)
                    history = data.get('idealista_requests', [])
                    # Convert string timestamps to datetime objects and filter last hour
                    one_hour_ago = datetime.now() - timedelta(hours=1)
                    self.request_history = [
                        datetime.fromisoformat(ts) for ts in history
                        if datetime.fromisoformat(ts) > one_hour_ago
                    ]
            else:
                self.request_history = []
        except Exception as e:
            self._log('error', f"Error loading request history: {str(e)}")
            self.request_history = []

    def _save_request_history(self):
        """Save the request history to JSON file"""
        try:
            data = {}
            if os.path.exists(self.last_run_file):
                with open(self.last_run_file, 'r') as f:
                    data = json.load(f)
            
            # Only keep timestamps from the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            self.request_history = [ts for ts in self.request_history if ts > one_hour_ago]
            
            # Convert datetime objects to ISO format strings
            data['idealista_requests'] = [ts.isoformat() for ts in self.request_history]
            
            with open(self.last_run_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self._log('error', f"Error saving request history: {str(e)}")

    def can_make_request(self):
        """Check if we can make another request within the hourly limit"""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        # Filter requests from the last hour
        self.request_history = [ts for ts in self.request_history if ts > one_hour_ago]
        return len(self.request_history) < IDEALISTA_MAX_REQUESTS_PER_HOUR

    def track_request(self):
        """Track a new request"""
        self.request_history.append(datetime.now())
        self._save_request_history()

    def scrape(self):
        """Scrape houses from Idealista website"""
        for url_index, base_url in enumerate(self.url, 1):
            if not self.can_make_request():
                self._log('info', f"Reached maximum requests per hour ({IDEALISTA_MAX_REQUESTS_PER_HOUR}), waiting for next hour")
                break

            self._log('info', f"Processing URL {url_index}: {base_url}")
            
            # Process first page
            new_houses_on_page1 = self._process_page(1, base_url)

            # Only continue to page 2 if we found new houses on page 1 and haven't hit the request limit
            if new_houses_on_page1 and self.can_make_request():
                self._log('info', "Processing page 2")
                self._process_page(2, base_url)
            elif not new_houses_on_page1:
                self._log('info', "No new houses found on page 1, skipping page 2")
            else:
                self._log('info', "Request limit reached, skipping page 2")

        self._log('info', "Finished processing all URLs")

    def _clean_image_url(self, img_url):
        """Clean up image URL by removing query parameters and normalizing"""
        if not img_url:
            return None
        
        # Remove query parameters
        if '?' in img_url:
            img_url = img_url.split('?')[0]
        
        # Handle srcset with multiple resolutions - take the highest resolution
        if ',' in img_url:
            # Split by comma and take the last (usually highest resolution) URL
            parts = img_url.split(',')
            for part in reversed(parts):
                part = part.strip()
                if part and ('http' in part):
                    img_url = part.split()[0]  # Take URL part, ignore resolution descriptor
                    break
        
        return img_url.strip()

    def _extract_gallery_images(self, house_element):
        """Extract all images from the property gallery on the listing page"""
        image_urls = []
        
        # Find the picture element with the gallery
        picture_elem = house_element.find('picture', class_='item-multimedia')
        if not picture_elem:
            self._log('warning', "No picture element with item-multimedia class found")
            # Try alternative selectors
            picture_elem = house_element.find('picture')
            if picture_elem:
                self._log('debug', f"Found picture element with class: {picture_elem.get('class')}")
            else:
                self._log('warning', "No picture element found at all")
                return image_urls
        
        # Check if there's a gallery with multiple images
        gallery_container = picture_elem.find('div', class_='item-gallery')

        if not gallery_container:
            self._log('warning', "No item-gallery container found, trying to extract images directly from picture element")
            return image_urls
        
        self._log('debug', "Found item-gallery container")
        # Get total number of images from the counter
        counter_spans = picture_elem.find_all('span')
        self._log('debug', f"Found {len(counter_spans)} span elements in picture")
        total_images = 1  # Default to 1 if we can't find the counter
        
        # Look for the image counter (e.g., "1/13")
        for span in counter_spans:
            span_text = span.get_text().strip()
            if '/' in span_text:
                try:
                    total_images = int(span_text.split('/')[-1])
                    self._log('debug', f"Found {total_images} total images in gallery counter")
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract all images from gallery slides
        gallery_slides = gallery_container.find_all('div', class_='image-gallery-slide')
        self._log('debug', f"Found {len(gallery_slides)} gallery slides")
        
        for slide in gallery_slides:
            # Skip map slides
            if slide.find('div', class_='map-content'):
                self._log('debug', "Skipping map slide")
                continue
                
            # Find picture element in slide
            slide_picture = slide.find('picture')
            if slide_picture:
                # Prefer WebP source
                webp_source = slide_picture.find('source', type='image/webp')
                if webp_source and webp_source.get('srcset'):
                    img_url = self._clean_image_url(webp_source.get('srcset'))
                    if img_url and img_url not in image_urls:
                        image_urls.append(img_url)
                        self._log('debug', f"Added WebP image: {img_url}")
                        continue
                
                # Fallback to JPEG source
                jpg_source = slide_picture.find('source', type='image/jpeg')
                if jpg_source and jpg_source.get('srcset'):
                    img_url = self._clean_image_url(jpg_source.get('srcset'))
                    if img_url and img_url not in image_urls:
                        image_urls.append(img_url)
                        self._log('debug', f"Added JPEG image: {img_url}")
                        continue
                
                # Final fallback to img tag
                img = slide_picture.find('img')
                if img and img.get('src') and not img.get('src').endswith('.gif'):
                    img_url = self._clean_image_url(img.get('src'))
                    if img_url and img_url not in image_urls:
                        image_urls.append(img_url)
                        self._log('debug', f"Added IMG tag image: {img_url}")
        return image_urls

    def _get_gallery_images(self, element_id):
        """Fetch all gallery images for a specific property"""
        gallery_images = []
        
        # Common Idealista gallery endpoint patterns
        gallery_urls = [
            f"https://www.idealista.pt/gallery/{element_id}",
            f"https://www.idealista.pt/imovel/{element_id}/gallery",
            f"https://www.idealista.pt/ajax/gallery/{element_id}",
        ]
        
        for gallery_url in gallery_urls:
            try:
                self._log('debug', f"Trying gallery URL: {gallery_url}")
                
                # Use ScraperAPI for gallery requests too
                payload = {
                    "api_key": self.api_key, 
                    "url": gallery_url, 
                    "autoparse": "true",
                    "premium": "true"  # Use premium proxies for protected domains
                }
                
                # Track the request
                self.track_request()
                r = requests.get("https://api.scraperapi.com/", params=payload)
                
                if r.status_code == 200:
                    # Try to parse as JSON first (common for AJAX endpoints)
                    try:
                        data = r.json()
                        if isinstance(data, dict) and 'images' in data:
                            for img_data in data['images']:
                                if isinstance(img_data, dict) and 'url' in img_data:
                                    gallery_images.append(img_data['url'])
                                elif isinstance(img_data, str):
                                    gallery_images.append(img_data)
                        elif isinstance(data, list):
                            for img_url in data:
                                if isinstance(img_url, str) and 'idealista.pt' in img_url:
                                    gallery_images.append(img_url)
                    except ValueError:
                        # Not JSON, try parsing as HTML
                        soup = BeautifulSoup(r.text, "html.parser")
                        
                        # Look for image elements
                        img_elements = soup.find_all(['img', 'source'])
                        for img_elem in img_elements:
                            img_url = img_elem.get('src') or img_elem.get('srcset')
                            if img_url and 'idealista.pt' in img_url and not img_url.endswith('.gif'):
                                gallery_images.append(img_url)
                    
                    if gallery_images:
                        self._log('info', f"Successfully fetched {len(gallery_images)} images from gallery endpoint")
                        break  # Found images, no need to try other URLs
                        
            except Exception as e:
                self._log('debug', f"Gallery request failed for URL {gallery_url}: {str(e)}")
                continue
        
        return gallery_images

    def _get_property_page_images(self, property_url):
        """Fetch all images by visiting the property detail page"""
        property_images = []
        
        try:
            self._log('debug', f"Fetching images from property page: {property_url}")
            
            # Use ScraperAPI to get the property page
            payload = {
                "api_key": self.api_key, 
                "url": property_url, 
                "autoparse": "true",
                "premium": "true"  # Use premium proxies for protected domains
            }
            
            # Track the request
            self.track_request()
            r = requests.get("https://api.scraperapi.com/", params=payload)
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                
                # Look for gallery containers and image elements
                gallery_selectors = [
                    '.gallery-image img',
                    '.image-gallery img', 
                    '.property-gallery img',
                    '.media-gallery img',
                    '[data-src*="idealista"]',
                    'img[src*="idealista"]',
                    'source[srcset*="idealista"]'
                ]
                
                for selector in gallery_selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        img_url = elem.get('src') or elem.get('srcset') or elem.get('data-src')
                        if img_url and 'idealista.pt' in img_url and not img_url.endswith('.gif'):
                            # Clean up the URL if it has multiple resolutions
                            if ',' in img_url:
                                img_url = img_url.split(',')[0].strip()
                            if img_url not in property_images:
                                property_images.append(img_url)
                
                self._log('info', f"Found {len(property_images)} images on property page")
                
        except Exception as e:
            self._log('warning', f"Could not fetch property page images: {str(e)}")
        
        return property_images

    def _process_page(self, page_num, base_url):
        """Process a single page of listings"""
        if not self.can_make_request():
            return

        if page_num == 1:
            current_url = base_url
        else:
            if "pagina-" not in base_url:
                # Add a trailing slash if it doesn't exist
                if not base_url.endswith('/'):
                    base_url += '/'
                current_url = base_url + f"pagina-{page_num}/"
            else:
                current_url = base_url.replace(
                    f"pagina-{page_num-1}", f"pagina-{page_num}"
                )

        self._log('info', f"Constructed URL for page {page_num}: {current_url}")

        try:
            self._log('info', f"Processing page {page_num}...")
           
            payload = {
                "api_key": self.api_key, 
                "url": current_url, 
                "autoparse": "true",
                "premium": "true"  # Use premium proxies for protected domains like Idealista
            }
            self._log('info', "Making request to ScraperAPI with premium proxies...")
            
            # Track the request before making it
            self.track_request()
            r = requests.get("https://api.scraperapi.com/", params=payload)
            
            self._log('info', f"ScraperAPI response status code: {r.status_code}")

            if r.status_code != 200:
                self._log('error', f"Failed to get page. Status code: {r.status_code}")
                self._log('error', f"Response content: {r.text[:500]}...")
                return

            soup = BeautifulSoup(r.text, "html.parser")
            self._log('info', "Successfully parsed page content with BeautifulSoup")

            houses = soup.find_all("article", class_="item")
            self._log('info', f"Found {len(houses)} house listings on page {page_num}")

            if not houses:
                self._log('warning', f"No houses found on page {page_num}")
                return

            # Track if any new houses were processed
            new_houses_found = False
            
            for house in houses:
                try:
                    title_link = house.find("a", class_="item-link")
                    if not title_link:
                        continue
                    
                    if self.current_run:
                        self.current_run.total_houses += 1
                        self.current_run.save()

                    name = title_link.get("title", "N/A")
                    url = f"https://www.idealista.pt{title_link.get('href', '')}"
                    
                    # Skip if URL already exists in the database
                    if self.url_exists(url):
                        self._log('info', f"Skipping already processed property: {url}")
                        continue

                    # If we get here, we found at least one new house
                    new_houses_found = True
                    
                    price_elem = house.find("span", class_="item-price")
                    price = price_elem.text.strip() if price_elem else "N/A"

                    details = house.find_all("span", class_="item-detail")
                    bedrooms = details[0].text.strip() if len(details) > 0 else "N/A"
                    area = (
                        details[1].text.strip().replace(" área bruta", "")
                        if len(details) > 1
                        else "N/A"
                    )
                    
                    # Extract floor directly from item-detail
                    floor = "N/A"
                    for detail in details:
                        if "andar" in detail.text.lower():
                            floor = detail.text.strip()
                            break

                    # Extract image URLs from the gallery
                    image_urls = self._extract_gallery_images(house)
                    
                    # Log image extraction results
                    if image_urls:
                        self._log('info', f"Successfully extracted {len(image_urls)} image(s) for property: {name}")
                    else:
                        self._log('warning', f"No images found for property: {name}")

                    zone_elem = house.find("a", class_="item-link")
                    if zone_elem and zone_elem.get("title"):
                        zone_words = zone_elem["title"].split()
                        try:
                            location_start = (
                                zone_words.index("em")
                                if "em" in zone_words
                                else zone_words.index("na")
                            )
                            zone = " ".join(zone_words[location_start + 1 :])
                        except ValueError:
                            zone = "N/A"
                    else:
                        zone = "N/A"

                    # Get description from item-description div
                    description_elem = house.find("div", class_="item-description")
                    description = description_elem.text.strip() if description_elem else "N/A"

                    # Extract freguesia and concelho
                    freguesia, concelho = self.location_manager.extract_location(zone)
                    
                    # Order: Name, Zone, Price, URL, Bedrooms, Area, Floor, Description, Freguesia, Concelho, Source, ScrapedAt, Image URLs
                    info_list = [
                        name,
                        zone,
                        price,
                        url,
                        bedrooms,
                        area,
                        floor,
                        description,
                        freguesia if freguesia else "N/A",
                        concelho if concelho else "N/A",
                        "Idealista",
                        None,  # ScrapedAt will be filled by save_to_excel
                        image_urls  # Add image URLs as the last column
                    ]

                    self.save_to_database(info_list)

                except Exception as e:
                    self._log('error', f"Error processing house: {str(e)}", exc_info=True)
                    continue

            # Return whether new houses were found
            return new_houses_found

        except Exception as e:
            self._log('error', f"Error processing page {page_num}: {str(e)}", exc_info=True)
            return False
