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
    'https://www.remax.pt/pt/arrendar/imoveis/habitacao/lisboa/lisboa/r/t,preco__1200?s=%7B%22rg%22%3A%22Lisboa%22%7D&p=1&o=-PublishDate'
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

CASA_SAPO_URLS = [
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/lisboa/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/amadora/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/cascais/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/oeiras/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/sintra/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/loures/?gp=1200',
    'https://casa.sapo.pt/alugar-apartamentos/t2,t3,t4,t5,t6-ou-superior/mais-recentes/odivelas/?gp=1200',
]

# API Keys
SCRAPER_API_KEY = '59592949eae6a709781746fc0aaec447'  # For Idealista scraping

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

# Idealista Settings
IDEALISTA_MAX_REQUESTS_PER_HOUR = 15  # Maximum number of requests per hour for Idealista scraper
