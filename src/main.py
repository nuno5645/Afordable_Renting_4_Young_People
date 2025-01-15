#!/usr/bin/env python
# coding: utf-8

import os
from openpyxl import Workbook
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.logger import setup_logger
from src.scrapers.imovirtual import ImoVirtualScraper
from src.scrapers.idealista import IdealistaScraper
from src.scrapers.remax import RemaxScraper
from src.scrapers.era import EraScraper
from config.settings import (
    IMOVIRTUAL_URLS,
    REMAX_URLS,
    IDEALISTA_URLS,
    ERA_URL,
    SCRAPER_API_KEY,
    EXCEL_FILENAME,
    EXCEL_HEADERS
)

# Setup logger
logger = setup_logger(__name__)

def run_scraper(scraper_name, scraper_instance):
    """Run a scraper and handle any exceptions"""
    try:
        logger.info(f"Starting {scraper_name} scraper...", extra={'action': 'SCRAPING'})
        scraper_instance.scrape()
        logger.info(f"Finished {scraper_name} scraper - Processed: {scraper_instance.houses_processed}, Found: {scraper_instance.houses_found}", extra={'action': 'PROCESSING'})
        return scraper_instance.houses_processed, scraper_instance.houses_found
    except Exception as e:
        logger.error(f"Error in {scraper_name} scraper: {str(e)}", exc_info=True)
        return 0, 0

def main():
    try:

        # Initialize scrapers
        logger.info("Starting house scraping process", extra={'action': 'PROCESSING'})
        
        # Create scraper instances
        scrapers = {
            'ImoVirtual': ImoVirtualScraper(logger, IMOVIRTUAL_URLS),
            # 'Remax': RemaxScraper(logger, REMAX_URLS),
            'Idealista': IdealistaScraper(logger, IDEALISTA_URLS, SCRAPER_API_KEY),
            # 'ERA': EraScraper(logger, ERA_URL)
        }

        # Store statistics
        stats = {}

        # Run scrapers concurrently using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(run_scraper, name, scraper): name 
                for name, scraper in scrapers.items()
            }

            # Wait for all tasks to complete
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    processed, found = future.result()
                    stats[scraper_name] = {'processed': processed, 'found': found}
                except Exception as e:
                    logger.error(f"Scraper {scraper_name} generated an exception: {str(e)}", exc_info=True)
                    stats[scraper_name] = {'processed': 0, 'found': 0}

        # Display final statistics
        total_processed = sum(s['processed'] for s in stats.values())
        total_found = sum(s['found'] for s in stats.values())
        logger.info("=== Scraping Statistics ===", extra={'action': 'SUMMARY'})
        for scraper_name, stat in stats.items():
            logger.info(f"{scraper_name}: Processed {stat['processed']} houses, Found {stat['found']} new listings", extra={'action': 'SUMMARY'})
        logger.info(f"Total: Processed {total_processed} houses, Found {total_found} new listings", extra={'action': 'SUMMARY'})
        logger.info("House scraping process completed", extra={'action': 'PROCESSING'})
    except Exception as e:
        logger.error(f"An error occurred in the main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
