# Lisbon Housing Scraper 🏠

## The Housing Crisis in Lisbon 🏘️

Lisbon is currently facing one of the most challenging housing crises in Europe. Young professionals and couples are particularly affected by:

- Rapidly increasing rental prices (up to 37% year-over-year in some areas)
- An extremely competitive rental market with properties being rented within hours
- Average rent consuming 50-80% of an entry-level salary
- Growing number of properties converted to short-term rentals (Airbnb)
- Limited stock of affordable housing in well-connected areas
- Competition from digital nomads and foreign investors with higher purchasing power

The situation is especially difficult for young local couples and professionals who:
- Work full-time jobs and can't constantly monitor rental websites
- Compete against automated systems and quick-response house hunters
- Need to find properties in areas with good public transport connections
- Have to balance affordability with quality of life
- Often lose opportunities because they can't respond immediately to listings

## Project Purpose 🎯

This project aims to level the playing field by providing young house hunters with the same technological advantages that many property companies and professional house hunters use. By automating the search and notification process, it helps you:

1. Get instant notifications about new properties that match your criteria
2. React quickly to new listings before they're gone
3. Find hidden gems in preferred neighborhoods
4. Save time by automating the monitoring of multiple real estate websites
5. Increase your chances of securing a viewing appointment

The tool automatically scrapes multiple Portuguese real estate websites (Idealista, ImoVirtual, Remax, ERA) and aggregates rental listings based on specific filters and price ranges, sending immediate notifications when suitable properties are found.

## Features 🌟

- Multi-platform scraping (Idealista, ImoVirtual, Remax, ERA)
- Configurable filters for location and price ranges
- Automated data collection and processing
- Web interface to view listings
- WhatsApp notifications for new listings
- Ntfy.sh notifications for affordable houses (under €850)
- Docker support for easy deployment
- Detailed logging system
- Robust CSV handling with automatic error detection and fixing

## Notifications 📱

### WhatsApp Notifications

The system can send WhatsApp notifications for new listings through the WhatsApp Business API. This feature is disabled by default and requires additional setup.

### Ntfy.sh Notifications

The system can send instant notifications for affordable houses (under €850 by default) using [ntfy.sh](https://ntfy.sh/), a simple HTTP-based pub-sub notification service.

To receive notifications:
1. Install the ntfy app on your smartphone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) or [iOS](https://apps.apple.com/us/app/ntfy/id1625396347))
2. Subscribe to the topic "Casas" (or your custom topic configured in settings.py)
3. Make sure `NTFY_NOTIFICATION_ENABLED` is set to `True` in `config/settings.py`

You can customize the notification settings in `config/settings.py`:
```python
# Ntfy.sh Settings
NTFY_TOPIC = "Casas"  # Topic for ntfy.sh notifications
NTFY_NOTIFICATION_ENABLED = True
NTFY_PRICE_THRESHOLD = 850  # Maximum price for notifications
NTFY_FILTER_ROOM_RENTALS = True  # Skip notifications for room rentals

# Room rental filter settings
ROOM_RENTAL_TITLE_TERMS = [
    "QUARTO", 
    "ROOM", 
    "ALUGA-SE QUARTO", 
    # ... other terms
]
```

The system automatically filters out room rentals (as opposed to full apartments) by checking for common room rental terms in the listing title and description. You can customize the filter terms or disable this feature by setting `NTFY_FILTER_ROOM_RENTALS = False`.

## Prerequisites 📋

- Python 3.x
- Docker (optional)
- Chrome/Chromium browser (for Selenium-based scraping)
- ScraperAPI key (for proxy rotation)

## Installation 🔧

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scrape_houses.git
cd scrape_houses
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your settings:
   - Copy `config/settings.example.py` to `config/settings.py`
   - Update the configuration with your API keys and preferences

## Usage 🚀

### Running the Scraper

```bash
# Run with interactive menu
python run.py

# Run all scrapers without menu
python run.py --less
```

### CSV Data Management

The scraper saves all housing data to a CSV file in the `data` directory. To ensure data integrity, several tools are provided:

#### Automatic CSV Fixing

The scraper automatically runs the CSV fix script after each scraping session to ensure data integrity. If you need to manually fix the CSV file:

```bash
# Run only the CSV fix script
python run.py --fix-csv-only

# Or run the fix script directly
python fix_csv.py
```

#### Continuous CSV Integrity Checking

For long-running deployments, you can use the CSV checker to periodically validate and fix the CSV file:

```bash
# Start the CSV checker (checks every 30 minutes by default)
./run_csv_checker.sh

# Start with custom interval (in minutes)
./run_csv_checker.sh 15  # Check every 15 minutes

# Stop the CSV checker
./stop_csv_checker.sh
```

The CSV checker logs are stored in the `logs` directory.

## Project Structure 📁

```
scrape_houses/
├── api/                    # FastAPI web interface
│   ├── main.py
│   └── templates/
├── config/                 # Configuration files
│   └── settings.py
├── data/                   # Scraped data storage
│   └── houses.csv
├── logs/                   # Log files
├── src/
│   ├── main.py            # Main execution file
│   ├── whatsapp_sender.py # WhatsApp notification system
│   ├── utils/             # Utility functions
│   └── scrapers/          # Individual website scrapers
│       ├── idealista.py
│       ├── imovirtual.py
│       ├── remax.py
│       └── era.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Configuration ⚙️

The project uses a settings.py file to manage configuration. Key settings include:

### Price Ranges 💰
- Configure minimum and maximum rental prices
- Set different ranges for different areas
- Exclude properties above market average

### Target Neighborhoods 🗺️
Popular areas included in the search:
- Arroios
- Alvalade
- Benfica
- Campo de Ourique
- Estrela
- Marvila
- Parque das Nações
- São Domingos de Benfica

### Transport Requirements 🚇
- Maximum walking distance to metro stations
- Proximity to bus stops
- Access to main transport hubs

### Property Filters 🏡
- Minimum and maximum area (m²)
- Number of bedrooms
- Property type (apartment, studio, etc.)
- Furnished/unfurnished options
- Energy certificate requirements

### Notification Settings 📱
- WhatsApp notification preferences
- Custom message templates
- Alert frequency
- Priority zones for faster notifications

## Roadmap & Tasks 📋

- [ ] Fix filters not working
- [ ] Implement pagination in listings homepage
- [ ] Restructure data and start using postgres(split 'zona' column into concelho/freguesia when possible)
- [ ] Update ngrok configuration to avoid using same domain
- [ ] Complete telegram notification logic
- [ ] Update deleted and viewed properties logic with ID (from database)
- [ ] Add property detail page (`/anuncio/{id}`)
- [ ] Add Casa Sapo scraper integration
- [ ] Display property location in listings
- [ ] Add favorites feature
- [ ] Maintain import history in database
- [ ] Remove duplicate listings
- [ ] Show import timestamp with green bubble notification for recent items
- [ ] Implement analytics/favorites/search pages
- [ ] Sort by most recent by default

## Contributing 🤝

Contributions are welcome! Feel free to:
- Add new real estate platforms
- Improve scraping algorithms
- Enhance the web interface
- Fix bugs
- Add new features

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚠️

This tool is for educational purposes only. Please check and comply with the terms of service of each website before using this scraper. 

## Tips for Success 💡

1. **Setup Priority Notifications:**
   - Configure WhatsApp alerts for high-priority areas
   - Set up different notification sounds for different price ranges

2. **Optimize Your Response:**
   - Prepare a template message for landlords
   - Have your documentation ready (pay slips, contracts, etc.)
   - Set aside a budget for the security deposit

3. **Best Times to Search:**
   - The tool runs 24/7, but most new listings appear between 9-11 AM
   - Many private landlords post on Sunday evenings
   - End of month usually has more listings

4. **Common Pitfalls to Avoid:**
   - Don't skip the viewing even if the price seems perfect
   - Be ready with your documentation
   - Have your deposit ready to secure the property 