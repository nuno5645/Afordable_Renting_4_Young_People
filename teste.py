from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os
from datetime import datetime
import json

class HouseListing:
    def __init__(self, title, price, location, images):
        self.title = title
        self.price = price
        self.location = location
        self.images = images
        self.timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.extracted_by = "nuno5645"  # Current user

def extract_house_listings(html_content, base_url=None):
    """
    Extract house listings with their respective images and details.
    Args:
        html_content (str): HTML content to parse
        base_url (str): Base URL to resolve relative URLs (optional)
    Returns:
        list: List of HouseListing objects
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    listings = []

    # Find all <article> elements that represent house listings
    articles = soup.find_all('article', class_='item')
    
    for article in articles:
        # Extract house details
        title_elem = article.find('a', class_='item-link')
        title = title_elem.get_text().strip() if title_elem else "No title"
        
        price_elem = article.find(class_='item-price')
        price = price_elem.get_text().strip() if price_elem else "No price"
        
        location_elem = article.find(class_='item-detail-location')
        location = location_elem.get_text().strip() if location_elem else "No location"

        # Collect multiple images inside the current article
        images = []
        picture_elems = article.find_all('picture')
        for picture in picture_elems:
            # Extract webp sources
            webp_sources = picture.find_all('source', type='image/webp')
            for source in webp_sources:
                srcset = source.get('srcset')
                if srcset:
                    if base_url:
                        srcset = urljoin(base_url, srcset)
                    if not any(img['url'] == srcset for img in images):
                        images.append({'url': srcset, 'type': 'webp'})

            # Extract jpg sources
            jpg_sources = picture.find_all('source', type='image/jpeg')
            for source in jpg_sources:
                srcset = source.get('srcset')
                if srcset:
                    if base_url:
                        srcset = urljoin(base_url, srcset)
                    if not any(img['url'] == srcset for img in images):
                        images.append({'url': srcset, 'type': 'jpg'})

            # Extract <img> element
            img = picture.find('img')
            if img and img.get('src'):
                src = img.get('src')
                if base_url:
                    src = urljoin(base_url, src)
                if not any(img_data['url'] == src for img_data in images):
                    images.append({
                        'url': src,
                        'type': 'jpg',
                        'alt': img.get('alt', '')
                    })

        # Create a HouseListing object
        listing = HouseListing(title, price, location, images)
        listings.append(listing)

    return listings

def save_listings_to_json(listings, output_file='house_listings.json'):
    """
    Save listings to a JSON file.
    """
    listings_data = []
    for listing in listings:
        listings_data.append({
            'title': listing.title,
            'price': listing.price,
            'location': listing.location,
            'images': listing.images,
            'timestamp': listing.timestamp,
            'extracted_by': listing.extracted_by
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(listings_data, f, ensure_ascii=False, indent=2)

def download_images(listings, output_dir='downloaded_images'):
    """
    Download images for each house listing.
    """
    for i, listing in enumerate(listings):
        # Create a directory for each house
        house_dir = os.path.join(output_dir, f'house_{i+1}_{listing.title[:30]}')
        os.makedirs(house_dir, exist_ok=True)
        
        # Save house details
        with open(os.path.join(house_dir, 'details.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Title: {listing.title}\n")
            f.write(f"Price: {listing.price}\n")
            f.write(f"Location: {listing.location}\n")
            f.write(f"Extracted on: {listing.timestamp}\n")
            f.write(f"Extracted by: {listing.extracted_by}\n")

        # Download images
        for j, image in enumerate(listing.images):
            try:
                url = image['url']
                img_type = image['type']
                # Handle unknown image types if needed
                if img_type not in ['jpg', 'webp']:
                    img_type = 'jpg'
                filename = f'image_{j+1}.{img_type}'
                filepath = os.path.join(house_dir, filename)
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Downloaded: {filename} for house {i+1}")
                
            except Exception as e:
                print(f"Failed to download image for house {i+1}: {str(e)}")

if __name__ == "__main__":
    # Make the API request to ScraperAPI
    payload = {
        'api_key': '59592949eae6a709781746fc0aaec447',
        'url': 'https://www.idealista.pt/arrendar-casas/lisboa/'
    }
    r = requests.get(
        'https://api.scraperapi.com/',
        params=payload
    )

    # Extract listings from the response
    listings = extract_house_listings(r.text)

    # Save listings to JSON (for review/debug)
    save_listings_to_json(listings)

    # Print extraction summary
    print(f"\nExtracted {len(listings)} house listings")
    for i, listing in enumerate(listings):
        print(f"\nHouse {i+1}:")
        print(f"Title: {listing.title}")
        print(f"Price: {listing.price}")
        print(f"Location: {listing.location}")
        print(f"Number of images: {len(listing.images)}")

    # Optionally, download images if needed:
    # download_images(listings)