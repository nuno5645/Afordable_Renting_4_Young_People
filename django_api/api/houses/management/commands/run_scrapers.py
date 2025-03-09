import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.utils import timezone
from houses.models import House, MainRun, ScraperRun
from decimal import Decimal, InvalidOperation
import hashlib
import logging
import re
from datetime import datetime, timedelta
import json

# Add the parent directory to sys.path to import scraper modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent))

from src.scrapers.imovirtual import ImoVirtualScraper
from src.scrapers.idealista import IdealistaScraper
from src.scrapers.remax import RemaxScraper
from src.scrapers.era import EraScraper
from src.scrapers.casa_sapo import CasaSapoScraper
from src.scrapers.super_casa import SuperCasaScraper
from src.messenger.ntfy_sender import NtfySender
from config.settings import (
    IMOVIRTUAL_URLS,
    REMAX_URLS,
    IDEALISTA_URLS,
    ERA_URL,
    CASA_SAPO_URLS,
    SUPER_CASA_URLS,
    SCRAPER_API_KEY,
)

class Command(BaseCommand):
    help = 'Run house scrapers and save results directly to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scrapers',
            nargs='+',
            type=str,
            help='Specify scrapers to run (imovirtual, idealista, remax, era, casasapo) or "all"'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force run even if another scraper is already running'
        )

    def setup_logger(self):
        logger = logging.getLogger('house_scrapers')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Remove existing handlers to prevent duplicate logging
        if logger.hasHandlers():
            logger.handlers.clear()
            
        logger.addHandler(console_handler)
        
        return logger

    def run_scraper(self, scraper_name, scraper_instance):
        """Run a scraper and handle any exceptions"""
        try:
            self.stdout.write(f"[{scraper_name}] Starting scraper...")
            scraper_instance.run()
            self.stdout.write(self.style.SUCCESS(f"[{scraper_name}] Finished scraper"))
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[{scraper_name}] Error in scraper: {str(e)}")
            )
            return False

    def handle(self, *args, **options):
        logger = self.setup_logger()
        
        # Check if another scraper is already running
        running_main_run = MainRun.objects.filter(status='running').first()
        if running_main_run and not options.get('force'):
            self.stdout.write(
                self.style.WARNING(f"Another scraper is already running (started at {running_main_run.start_time}). Use --force to run anyway.")
            )
            return
            
        # Create a new main run
        main_run = MainRun.objects.create(status='running')
        
        try:
            # Available scrapers
            available_scrapers = {
                'imovirtual': ('ImoVirtual', ImoVirtualScraper, IMOVIRTUAL_URLS, None),
                'idealista': ('Idealista', IdealistaScraper, IDEALISTA_URLS, SCRAPER_API_KEY),
                'remax': ('Remax', RemaxScraper, REMAX_URLS, None),
                'era': ('ERA', EraScraper, ERA_URL, None),
                'casasapo': ('Casa SAPO', CasaSapoScraper, CASA_SAPO_URLS, None),
                'supercasa': ('SuperCasa', SuperCasaScraper, SUPER_CASA_URLS, None)
            }

            # Determine which scrapers to run
            selected_scrapers = {}
            if not options['scrapers'] or 'all' in options['scrapers']:
                selected_scrapers = available_scrapers
            else:
                for scraper in options['scrapers']:
                    if scraper.lower() in available_scrapers:
                        selected_scrapers[scraper.lower()] = available_scrapers[scraper.lower()]
                    else:
                        self.stdout.write(self.style.WARNING(f"Unknown scraper: {scraper}"))

            if not selected_scrapers:
                self.stdout.write(self.style.ERROR("No valid scrapers selected"))
                main_run.status = 'failed'
                main_run.error_message = "No valid scrapers selected"
                main_run.end_time = timezone.now()
                main_run.save()
                return

            # Create scraper instances with database saver
            scrapers = {}
            for key, (name, scraper_class, urls, api_key) in selected_scrapers.items():
                if api_key:
                    scrapers[name] = scraper_class(logger, urls, api_key)
                else:
                    scrapers[name] = scraper_class(logger, urls)
                    
                # Link the scraper run to the main run
                if hasattr(scrapers[name], 'current_run') and scrapers[name].current_run:
                    scrapers[name].current_run.main_run = main_run
                    scrapers[name].current_run.save()
                
            # Run scrapers concurrently
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_scraper = {
                    executor.submit(self.run_scraper, name, scraper): name 
                    for name, scraper in scrapers.items()
                }

                for future in as_completed(future_to_scraper):
                    scraper_name = future_to_scraper[future]
                    try:
                        future.result()
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"[{scraper_name}] Scraper failed: {str(e)}")
                        )

            # Print statistics for each scraper
            self.stdout.write("\n=== Scraping Statistics ===")
            total_houses = 0
            new_houses = 0
            
            for name, scraper in scrapers.items():
                if hasattr(scraper, 'current_run') and scraper.current_run:
                    run = scraper.current_run
                    success_rate = (run.new_houses/run.total_houses*100) if run.total_houses > 0 else 0
                    duration = (run.end_time - run.start_time).total_seconds() if run.end_time else 0
                    
                    # Update main run statistics
                    total_houses += run.total_houses
                    new_houses += run.new_houses
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"\n{name}:"
                            f"\n  Total Houses Checked: {run.total_houses}"
                            f"\n  New Houses Found: {run.new_houses}"
                            f"\n  Success Rate: {success_rate:.1f}% new houses"
                            f"\n  Status: {run.status}"
                            f"\n  Duration: {duration:.1f} seconds"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"\n{name}: No statistics available (scraper may have failed)")
                    )
            
            # Update main run with final statistics
            main_run.status = 'completed'
            main_run.end_time = timezone.now()
            main_run.total_houses = total_houses
            main_run.new_houses = new_houses
            main_run.save()
            
        except Exception as e:
            # Mark the main run as failed if an exception occurs
            main_run.status = 'failed'
            main_run.end_time = timezone.now()
            main_run.error_message = str(e)
            main_run.save()
            raise