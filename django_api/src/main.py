#!/usr/bin/env python
# coding: utf-8

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Add necessary paths for imports
current_dir = Path(__file__).parent.parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from src.utils.logger import ScraperLogger
    from src.scrapers.imovirtual import ImoVirtualScraper
    from src.scrapers.idealista import IdealistaScraper
    from src.scrapers.remax import RemaxScraper
    from src.scrapers.era import EraScraper
    from src.scrapers.casa_sapo import CasaSapoScraper
    from src.scrapers.super_casa import SuperCasaScraper
except ImportError as e:
    from utils.logger import ScraperLogger
    from scrapers.imovirtual import ImoVirtualScraper
    from scrapers.idealista import IdealistaScraper
    from scrapers.remax import RemaxScraper
    from scrapers.era import EraScraper
    from scrapers.casa_sapo import CasaSapoScraper
    from scrapers.super_casa import SuperCasaScraper

# Django imports
try:
    from houses.models import ScraperRun, MainRun
    from django.utils import timezone
except ImportError:
    # Django is not set up, this should be handled by the caller
    ScraperRun = None
    MainRun = None
    timezone = None

from config.settings import (
    IMOVIRTUAL_URLS,
    REMAX_URLS,
    IDEALISTA_URLS,
    ERA_URL,
    CASA_SAPO_URLS,
    SUPER_CASA_URLS,
    SCRAPER_API_KEY,
)

# Setup colored logger
logger = ScraperLogger(__name__)

def run_scraper(scraper_name, scraper_instance):
    """Run a scraper and handle any exceptions"""
    try:
        logger.initializing(f"[{scraper_name}] Starting scraper...")
        
        # Run the scraper (initialization is handled internally)
        scraper_instance.run()
        
        # Get the statistics from the completed run
        total = scraper_instance.current_run.total_houses if scraper_instance.current_run else 0
        new = scraper_instance.current_run.new_houses if scraper_instance.current_run else 0
        
        logger.analyzing(f"[{scraper_name}] Finished scraper - Total Houses: {total}, New Houses: {new}")
        return total, new
    except Exception as e:
        logger.error(f"[{scraper_name}] Error in scraper: {str(e)}", exc_info=True)
        return 0, 0

def get_scraper_selection():
    """Display menu and get user selection of scrapers to run"""
    available_scrapers = {
        1: ('ImoVirtual', ImoVirtualScraper, IMOVIRTUAL_URLS, None),
        2: ('Idealista', IdealistaScraper, IDEALISTA_URLS, SCRAPER_API_KEY),
        3: ('Remax', RemaxScraper, REMAX_URLS, None),
        4: ('ERA', EraScraper, ERA_URL, None),
        5: ('Casa SAPO', CasaSapoScraper, CASA_SAPO_URLS, None),
        6: ('Super Casa', SuperCasaScraper, SUPER_CASA_URLS, None)
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
        # Check if Django models are available
        if ScraperRun is None or MainRun is None or timezone is None:
            print("Error: Django is not properly set up. Please run this script through run_scrapers.py")
            return
            
        logger.initializing("[MAIN] Starting house scraping process")
        
        # Create a new main run
        main_run = MainRun.objects.create(status='running')
        logger.loading(f"[MAIN] Created new main run: {main_run.id}")
        
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
                5: ('Casa SAPO', CasaSapoScraper, CASA_SAPO_URLS, None),
                6: ('Super Casa', SuperCasaScraper, SUPER_CASA_URLS, None)
            }
        
        # Create scraper instances
        scrapers = {}
        for _, (name, scraper_class, urls, api_key) in selected_scrapers.items():
            if api_key:
                scrapers[name] = scraper_class(logger, urls, api_key)
            else:
                scrapers[name] = scraper_class(logger, urls)
            
            # Set the main run for each scraper
            scrapers[name].set_main_run(main_run)

        # Store statistics for this run
        stats = {}
        total_houses = 0
        total_new = 0

        # Run scrapers concurrently using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(run_scraper, name, scraper): name 
                for name, scraper in scrapers.items()
            }

            # Wait for all tasks to complete and collect statistics
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    total, new = future.result()
                    stats[scraper_name] = {'total': total, 'new': new}
                    total_houses += total
                    total_new += new
                except Exception as e:
                    logger.error(f"[{scraper_name}] Scraper generated an exception: {str(e)}", exc_info=True)
                    stats[scraper_name] = {'total': 0, 'new': 0}

        # Update main run with totals
        main_run.total_houses = total_houses
        main_run.new_houses = total_new
        main_run.status = 'completed'
        main_run.end_time = timezone.now()
        main_run.save()

        # Display final statistics
        logger.analyzing("[SUMMARY] === Scraping Statistics ===")
        for scraper_name, stat in stats.items():
            logger.analyzing(f"[{scraper_name}] Total Houses: {stat['total']}, New Houses: {stat['new']}")
        logger.analyzing(f"[SUMMARY] Total: Total Houses: {total_houses}, New Houses: {total_new}")
        logger.analyzing("[MAIN] House scraping process completed")
        
        # Get today's runs for additional statistics
        today = timezone.now().date()
        today_runs = ScraperRun.objects.filter(
            start_time__date=today,
            status='completed'
        )
        
        if today_runs.exists():
            total_today_houses = sum(run.total_houses for run in today_runs)
            total_today_new = sum(run.new_houses for run in today_runs)
            logger.analyzing(f"[SUMMARY] Today's Total: Total Houses: {total_today_houses}, New Houses: {total_today_new}")
            
    except Exception as e:
        logger.error(f"[MAIN] An error occurred in the main process: {str(e)}", exc_info=True)
        # Mark main run as failed if it exists
        if 'main_run' in locals():
            main_run.status = 'failed'
            main_run.error_message = str(e)
            main_run.end_time = timezone.now()
            main_run.save()
        raise

if __name__ == "__main__":
    main()
