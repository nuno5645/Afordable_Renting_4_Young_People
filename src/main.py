#!/usr/bin/env python
# coding: utf-8

import os
import sys
from openpyxl import Workbook
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.utils.logger import setup_logger
from src.scrapers.imovirtual import ImoVirtualScraper
from src.scrapers.idealista import IdealistaScraper
from src.scrapers.remax import RemaxScraper
from src.scrapers.era import EraScraper
from src.scrapers.casa_sapo import CasaSapoScraper
from config.settings import (
    IMOVIRTUAL_URLS,
    REMAX_URLS,
    IDEALISTA_URLS,
    ERA_URL,
    CASA_SAPO_URLS,
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

def get_scraper_selection():
    """Display menu and get user selection of scrapers to run"""
    available_scrapers = {
        1: ('ImoVirtual', ImoVirtualScraper, IMOVIRTUAL_URLS, None),
        2: ('Idealista', IdealistaScraper, IDEALISTA_URLS, SCRAPER_API_KEY),
        3: ('Remax', RemaxScraper, REMAX_URLS, None),
        4: ('ERA', EraScraper, ERA_URL, None),
        5: ('Casa SAPO', CasaSapoScraper, CASA_SAPO_URLS, None)
    }
    
    print("\nAvailable scrapers:")
    for num, (name, _, _, _) in available_scrapers.items():
        print(f"{num}. {name}")
    print("Enter numbers separated by spaces (e.g., '1 2 3 4 5') or 'all' for all scrapers:")
    
    while True:
        choice = input("> ").strip().lower()
        if choice == 'all':
            return available_scrapers
        
        try:
            selected_nums = [int(x) for x in choice.split()]
            selected_scrapers = {num: data for num, data in available_scrapers.items() if num in selected_nums}
            if not selected_scrapers:
                print("Please select at least one scraper")
                continue
            if any(num not in available_scrapers for num in selected_nums):
                print("Invalid selection. Please try again")
                continue
            return selected_scrapers
        except ValueError:
            print("Invalid input. Please enter numbers or 'all'")

def main(use_menu=True):
    try:
        logger.info("Starting house scraping process", extra={'action': 'PROCESSING'})
        
        # Initialize scrapers based on menu selection or all scrapers
        if len(sys.argv) > 1 and sys.argv[1] == '--all':
            use_menu = False
            
        if use_menu:
            selected_scrapers = get_scraper_selection()
        else:
            selected_scrapers = {
                1: ('ImoVirtual', ImoVirtualScraper, IMOVIRTUAL_URLS, None),
                2: ('Idealista', IdealistaScraper, IDEALISTA_URLS, SCRAPER_API_KEY),
                3: ('Remax', RemaxScraper, REMAX_URLS, None),
                4: ('ERA', EraScraper, ERA_URL, None),
                5: ('Casa SAPO', CasaSapoScraper, CASA_SAPO_URLS, None)
            }
        
        # Create scraper instances
        scrapers = {}
        for _, (name, scraper_class, urls, api_key) in selected_scrapers.items():
            if api_key:
                scrapers[name] = scraper_class(logger, urls, api_key)
            else:
                scrapers[name] = scraper_class(logger, urls)

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
