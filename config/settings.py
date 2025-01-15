# Website URLs
IMOVIRTUAL_URLS = [
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/lisboa?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/amadora?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/cascais?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/oeiras?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/sintra?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/loures?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
    'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/odivelas?limit=36&priceMax=1200&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=DEFAULT&direction=DESC&viewType=listing',
]

REMAX_URLS = [
    'https://www.remax.pt/comprar?searchQueryState=%7B%22regionName%22:%22cascais%22,%22businessType%22:1,%22page%22:1,%22regionID%22:%22%22,%22regionType%22:%22%22,%22sort%22:%7B%22fieldToSort%22:%22PublishDate%22,%22order%22:1%7D,%22mapIsOpen%22:false,%22price%22:%7B%22min%22:null,%22max%22:240000%7D,%22mapScroll%22:false,%22rooms%22:2%7D',
    'https://www.remax.pt/comprar?searchQueryState=%7B%22regionName%22:%22Oeiras%22,%22businessType%22:1,%22page%22:1,%22regionID%22:%22541%22,%22regionType%22:%22Region2ID%22,%22sort%22:%7B%22fieldToSort%22:%22PublishDate%22,%22order%22:1%7D,%22mapIsOpen%22:false,%22listingClass%22:1,%22price%22:%7B%22min%22:null,%22max%22:240000%7D,%22mapScroll%22:false,%22rooms%22:2,%22listingTypes%22:%5B%5D,%22prn%22:%22Oeiras,%20Lisboa%22,%22regionCoordinates%22:%7B%22latitude%22:38.7170951617666,%22longitude%22:-9.269621200241543%7D,%22regionZoom%22:12%7D'
]

IDEALISTA_URLS = [
    'https://www.idealista.pt/arrendar-casas/amadora/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/cascais/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/lisboa/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/loures/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/odivelas/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/oeiras/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    'https://www.idealista.pt/arrendar-casas/sintra/com-preco-max_1000,t1,t2,t3,t4-t5/?ordem=atualizado-desc'
]

ERA_URL = 'https://www.era.pt/arrendar?ob=2&tp=1,2&sp=mwbkFn}hx@gm[_mEujLinc@cjG}re@xk[~lEjkL|zKbvJh`]gjB~d_@&page=1&ord=3'

# API Keys
SCRAPER_API_KEY = 'e0c9203edd30d2e5c624f841b9c4e0b4'  # For Idealista scraping

# Excel Settings
EXCEL_FILENAME = 'houses.xlsx'
EXCEL_HEADERS = ['Name', 'Zone', 'Price', 'URL', 'Bedrooms', 'Area', 'Floor', 'Description', 'Source', 'Scraped At']

# Scraping Settings
MAX_PAGES = 2  # Maximum number of pages to scrape for paginated sites
PAGE_LOAD_WAIT = 5  # Seconds to wait for page load
BETWEEN_REQUESTS_WAIT = 10  # Seconds to wait between requests

# WhatsApp Settings
WHATSAPP_GROUP_ID = "ByBvbZbZImiIGrL8nlpvQX"  # Group ID for house notifications
WHATSAPP_NOTIFICATION_ENABLED = False
