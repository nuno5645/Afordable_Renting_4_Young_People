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
- Docker support for easy deployment
- Detailed logging system

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

### Running with Python

```bash
python run.py
```

### Running with Docker

```bash
docker-compose up --build
```

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