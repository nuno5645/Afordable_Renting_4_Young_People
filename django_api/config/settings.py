# Price limit for searches
MAX_PRICE = 900  # For renting
MAX_PRICE_BUY = 300000  # For buying

# Logging configuration
import os
import logging.config

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/house_scraper.log',
            'formatter': 'verbose',
        },
        'image_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/image_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'house_scrapers': {
            'handlers': ['console', 'file', 'image_debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Website URLs
IMOVIRTUAL_URLS = [
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/lisboa?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/amadora?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/cascais?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/oeiras?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
   f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/sintra?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/loures?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/arrendar/apartamento/lisboa/odivelas?limit=36&priceMax={MAX_PRICE}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
]

REMAX_URLS = [
    f'https://www.remax.pt/pt/arrendar/imoveis/habitacao/lisboa/lisboa/r/t,preco__{MAX_PRICE}?s=%7B%22rg%22%3A%22Lisboa%22%7D&p=1&o=-PublishDate'
]

IDEALISTA_URLS = [
    f'https://www.idealista.pt/arrendar-casas/amadora/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    # f'https://www.idealista.pt/arrendar-casas/cascais/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    # f'https://www.idealista.pt/arrendar-casas/lisboa/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    # f'https://www.idealista.pt/arrendar-casas/loures/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    # f'https://www.idealista.pt/arrendar-casas/odivelas/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
    # f'https://www.idealista.pt/arrendar-casas/oeiras/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
#    f'https://www.idealista.pt/arrendar-casas/sintra/com-preco-max_{MAX_PRICE},t1,t2,t3,t4-t5/?ordem=atualizado-desc'
]

ERA_URL = 'https://www.era.pt/comprar?ob=2&tp=1,2&ord=3&paMax=800&ir=1&nr=0&dt=11&page=1'

CASA_SAPO_URLS = [
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/lisboa/?gp={MAX_PRICE}',
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/amadora/?gp={MAX_PRICE}',
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/cascais/?gp={MAX_PRICE}',
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/oeiras/?gp={MAX_PRICE}',
   f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/sintra/?gp={MAX_PRICE}',
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/loures/?gp={MAX_PRICE}',
    f'https://casa.sapo.pt/alugar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/odivelas/?gp={MAX_PRICE}',
]

SUPER_CASA_URLS = [
    f'https://supercasa.pt/arrendar-casas/lisboa/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
    f'https://supercasa.pt/arrendar-casas/amadora/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
    f'https://supercasa.pt/arrendar-casas/cascais/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
    f'https://supercasa.pt/arrendar-casas/oeiras/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
   f'https://supercasa.pt/arrendar-casas/sintra/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
    f'https://supercasa.pt/arrendar-casas/loures/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
    f'https://supercasa.pt/arrendar-casas/odivelas/com-t1,t2,t3,t4,preco-max-{MAX_PRICE}?ordem=atualizado-desc',
]

# URLs for buying (comprar)
IMOVIRTUAL_URLS_BUY = [
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/lisboa?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/amadora?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/cascais?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/oeiras?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/loures?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
    f'https://www.imovirtual.com/pt/resultados/comprar/apartamento/lisboa/odivelas?limit=36&priceMax={MAX_PRICE_BUY}&roomsNumber=%5BTWO%2CTHREE%2CFOUR%2CFIVE%2CSIX_OR_MORE%5D&by=LATEST&direction=DESC&viewType=listing',
]

REMAX_URLS_BUY = [
    f'https://www.remax.pt/pt/comprar/imoveis/habitacao/lisboa/lisboa/r/t,preco__{MAX_PRICE_BUY}?s=%7B%22rg%22%3A%22Lisboa%22%7D&p=1&o=-PublishDate'
]

IDEALISTA_URLS_BUY = [
    f'https://www.idealista.pt/comprar-casas/amadora/com-preco-max_{MAX_PRICE_BUY},t1,t2,t3,t4-t5/?ordem=atualizado-desc',
]

ERA_URL_BUY = 'https://www.era.pt/comprar?ob=1&tp=1,2&ord=3&paMax=300000&ir=1&nr=0&dt=11&page=1'

CASA_SAPO_URLS_BUY = [
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/lisboa/?gp={MAX_PRICE_BUY}',
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/amadora/?gp={MAX_PRICE_BUY}',
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/cascais/?gp={MAX_PRICE_BUY}',
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/oeiras/?gp={MAX_PRICE_BUY}',
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/loures/?gp={MAX_PRICE_BUY}',
    f'https://casa.sapo.pt/comprar-apartamentos/t1,t2,t3,t4,t5,t6-ou-superior/mais-recentes/odivelas/?gp={MAX_PRICE_BUY}',
]

SUPER_CASA_URLS_BUY = [
    f'https://supercasa.pt/comprar-casas/lisboa/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/amadora/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/cascais/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/sintra/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/oeiras/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/loures/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
    f'https://supercasa.pt/comprar-casas/odivelas/com-t1,t2,t3,t4,preco-max-{MAX_PRICE_BUY}?ordem=atualizado-desc',
]

# API Keys
SCRAPER_API_KEY = 'ebe877384fd8936805b9332cfb7d1613'  # For Idealista scraping

# Excel Settings
EXCEL_FILENAME = 'houses.xlsx'
EXCEL_HEADERS = ['Name', 'Zone', 'Price', 'URL', 'Bedrooms', 'Area', 'Floor', 'Description', 'Freguesia', 'Concelho', 'Source', 'Scraped At', 'Image URLs']

# Scraping Settings
MAX_PAGES = 2  # Maximum number of pages to scrape for paginated sites
PAGE_LOAD_WAIT = 5  # Seconds to wait for page load
BETWEEN_REQUESTS_WAIT = 10  # Seconds to wait between requests


# Ntfy.sh Settings
NTFY_TOPIC = "Casas"  # Topic for ntfy.sh notifications
NTFY_NOTIFICATION_ENABLED = False
NTFY_PRICE_THRESHOLD = 900  # Maximum price for notifications
NTFY_FILTER_ROOM_RENTALS = True  # Skip notifications for room rentals

# Room rental filter settings
ROOM_RENTAL_TITLE_TERMS = [
    "QUARTO", 
    "ROOM", 
    "ALUGA-SE QUARTO", 
    "ALUGO QUARTO", 
    "QUARTO PARA ALUGAR",
    "Dividir apartamento"
]

ROOM_RENTAL_DESCRIPTION_TERMS = [
    "QUARTO EM APARTAMENTO", 
    "QUARTO PARTILHADO", 
    "SHARED ROOM", 
    "ROOM IN APARTMENT",
    "ALUGAM-SE QUARTOS"
]

# Idealista Settings
IDEALISTA_MAX_REQUESTS_PER_HOUR = 50  # Maximum number of requests per hour for Idealista scraper
