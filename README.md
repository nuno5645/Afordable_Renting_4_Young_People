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

The tool automatically scrapes multiple Portuguese real estate websites (Idealista, ImoVirtual, Remax, ERA, Casa Sapo, Super Casa) and aggregates rental listings based on specific filters and price ranges, sending immediate notifications when suitable properties are found.

## Features 🌟

- Multi-platform scraping (Idealista, ImoVirtual, Remax, ERA, Casa Sapo, Super Casa)
- Configurable filters for location and price ranges
- Automated data collection and processing
- Modern React frontend with Tailwind CSS
- Django REST API backend with database storage
- Progressive Web App (PWA) support
- Native iOS app with SwiftUI
- Responsive mobile-friendly design
- Ntfy.sh notifications for affordable houses (under €850)
- Docker support for easy deployment
- Detailed logging system
- Robust CSV handling with automatic error detection and fixing
- Property image storage and display
- Favorite and discard property tracking
- Scraper run statistics and monitoring

## System Architecture 🏗️

The project has been restructured into a modern microservices architecture with the following components:

                     LISBON HOUSING SCRAPER ARCHITECTURE
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│         ┌─────────────────┐                    ┌─────────────────┐                  │
│         │    Frontend     │                    │   iOS Native    │                  │
│         │   React + PWA   │                    │   SwiftUI App   │                  │
│         └────────┬────────┘                    └────────┬────────┘                  │
│                  │                                      │                           │
│                  │ HTTP/REST                            │ HTTP/REST                 │
│                  ▼                                      │                           │
│         ┌────────────────┐                              │                           │
│         │                │                              │                           │
│         │   Django API   │◄─────────────────────────────┘                           │
│         │                │◄───────┐                                                 │
│         └────────┬───────┘        │                                                 │
│                  │                │                                                 │
│                  ▼                │                                                 │
│         ┌────────────────┐        │                                                 │
│         │  PostgreSQL    │        │                                                 │
│         │   Database     │        │                                                 │
│         └────────────────┘        │                                                 │
│                                   │                                                 │
│         ┌────────────────────────────────────────────┐                              │
│         │               Scrapers                     │                              │
│         │ ┌────────────┐ ┌─────────┐ ┌────────────┐  │                              │
│         │ │ Idealista  │ │ Remax   │ │ SuperCasa  │  │                              │
│         │ └────────────┘ └─────────┘ └────────────┘  │                              │
│         │ ┌────────────┐ ┌─────────┐ ┌────────────┐  │                              │
│         │ │ ImoVirtual │ │ ERA     │ │ CasaSapo   │  │-──┐                          │
│         │ └────────────┘ └─────────┘ └────────────┘  │   │                          │
│         └────────────────────────────────────────────┘   │                          │
│                                                          │                          │
│         ┌────────────────────────────────────────┐       │                          │
│         │            Notifications               │       │                          │
│         │                                        │◄────-─┘                          │
│         │  ┌──────────────┐  ┌───────────────┐   │                                  │
│         │  │   ntfy.sh    │  │   WhatsApp    │   │                                  │
│         │  │ Notifications│  │ Notifications │   │                                  │
│         │  └──────────────┘  └───────────────┘   │                                  │
│         └────────────────────────────────────────┘                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

### Backend Services

1. **Django API** - Main backend service with PostgreSQL database
   - RESTful API endpoints for house listings
   - Database models for property data
   - Scraper run statistics and tracking
   - Authentication and data validation

2. **Flask API** (Legacy) - Older API implementation being migrated to Django

3. **Scrapers** - Modular web scrapers for different real estate platforms
   - Idealista, ImoVirtual, Remax, ERA scrapers
   - Rotating proxies and user agents
   - Headless browser automation

### Frontend Application

- Modern React application with TypeScript
- Tailwind CSS for styling
- PWA support for mobile installation
- Responsive design for all device sizes
- Property search and filtering
- Property details view with images
- Favorites management

### iOS Application

- Native SwiftUI app for iOS 15.0+
- Modern card-based property listing interface
- Advanced filtering system with:
  - Price range selection
  - Area range filtering
  - Bedroom count filtering
  - Source filtering
- Dark mode support
- Smooth animations and transitions
- Responsive and adaptive UI design

### Deployment

- Docker containerization for all services
- Docker Compose for orchestration
- HTTPS support with SSL certificates
- Nginx for reverse proxy (optional)

## Notifications 📱

### Ntfy.sh Notifications

The system sends instant notifications for affordable houses (under €850 by default) using [ntfy.sh](https://ntfy.sh/), a simple HTTP-based pub-sub notification service.

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

### WhatsApp Notifications (Planned)

WhatsApp notifications are planned for future implementation. This feature will allow sending notifications through the WhatsApp Business API for new listings that match specific criteria.

## Prerequisites 📋

- Python 3.x
- Docker and Docker Compose
- Node.js (for frontend development)
- Chrome/Chromium browser (for Selenium-based scraping)
- ScraperAPI key (required for Idealista scraping)

## Installation 🔧

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scrape_houses.git
cd scrape_houses
```

2. Configure your environment:
   - Copy `config/settings.example.py` to `config/settings.py` and update settings
   - Add your ScraperAPI key for Idealista scraping
   - Configure other API keys and preferences

3. Start the services with Docker Compose:
```bash
docker-compose up -d
```

This will start the Django API service. You can uncomment other services in the docker-compose.yml file as needed.

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/scrape_houses.git
cd scrape_houses
```

2. Set up the backend:
```bash
cd django_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Configure your settings:
   - Copy `config/settings.example.py` to `config/settings.py`
   - Update the configuration with your API keys and preferences

## Usage 🚀

### Running the Django API

```bash
cd django_api
python api/manage.py runserver
```

The API will be available at http://localhost:8000/api/

### Running the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173/

### Running the Scraper

```bash
# Run with interactive menu
python run.py

# Run all scrapers without menu
python run.py --less
```


## Project Structure 📁

The project now has a more organized structure with several components:

```
scrape_houses/
├── django_api/                # Django REST API
│   ├── api/                   # Django project
│   │   ├── houses/            # Houses app with models and views
│   │   └── manage.py          # Django management script
│   ├── config/                # Configuration files
│   ├── Dockerfile             # Docker config for Django API
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React frontend application
│   ├── src/                   # Source code
│   │   ├── components/        # React components
│   │   ├── services/          # API service connections
│   │   └── context/           # React context providers
│   ├── Dockerfile             # Docker config for frontend
│   └── package.json           # Node.js dependencies
│
├── casas-lisboa/             # iOS native application
│   ├── Views/                # SwiftUI views
│   │   ├── HomeView.swift    # Main listing view
│   │   ├── FilterView.swift  # Property filtering interface
│   │   └── PropertyCardView.swift # Property card component
│   ├── Models/               # Data models
│   └── Assets/               # App resources
│
├── flask_api/                 # Legacy Flask API (being migrated)
│   └── main.py                # Flask API implementation
│
├── data/                      # Scraped data storage
│   └── houses.csv             # CSV data file
│
├── logs/                      # Log files
│
├── src/                       # Scraper source code
│   ├── main.py                # Main execution file
│   ├── whatsapp_sender.py     # WhatsApp notification system
│   ├── utils/                 # Utility functions
│   └── scrapers/              # Individual website scrapers
│       ├── idealista.py
│       ├── imovirtual.py
│       ├── remax.py
│       ├── era.py
│       ├── casa_sapo.py
│       └── super_casa.py
│
├── Dockerfile                 # Docker config for scrapers
├── docker-compose.yml         # Docker Compose configuration
└── requirements.txt           # Python dependencies for scrapers
```

## Database Models 📊

The system now uses a PostgreSQL database with Django models:

### House Model
- Property details (name, price, area, bedrooms, etc.)
- Location data (zone, freguesia, concelho)
- Property images
- Status tracking (contacted, discarded, favorite)
- Source platform and scraping timestamp

### MainRun Model
- Tracks main scraper runs
- Stores run status and execution time
- Counts total and new houses found
- Error reporting

### ScraperRun Model
- Tracks individual scraper runs
- Links to parent MainRun
- Stores status, statistics, and errors for each scraper

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

- [x] Implement Django backend with proper database models
- [x] Create React frontend with Tailwind CSS
- [x] Set up Docker containerization
- [x] Add property image storage and display
- [x] Implement property detail view
- [x] Add favorites and discarded property tracking
- [x] Fix filters not working
- [x] Update deleted and viewed properties logic with ID (from database)
- [x] Add Casa Sapo scraper integration
- [x] Sort by most recent by default
- [ ] Implement pagination in listings homepage
- [ ] Restructure data and start using postgres(split 'zona' column into concelho/freguesia when possible)
- [ ] Add property detail page (`/anuncio/{id}`)
- [ ] Display property location in listings
- [ ] Maintain import history in database
- [ ] Remove duplicate listings
- [ ] Show import timestamp with green bubble notification for recent items
- [ ] Implement analytics/favorites/search pages
- [ ] Complete iOS app features:
  - [ ] Property details screen
  - [ ] Favorites system
  - [ ] Search functionality
  - [ ] User preferences persistence
  - [ ] Map view for property locations
  - [ ] Property alerts and notifications
- [ ] Implement WhatsApp notifications
- [ ] Add support for more real estate platforms

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