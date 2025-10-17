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
import threading
import os

# Define possible locations for the src directory
possible_paths = [
    # Docker paths
    '/app',                # Root of the Docker container
    '/app/src',            # src might be directly in the app directory
    '/src',                # src might be at the root
    # Local development paths
    Path(__file__).resolve().parent.parent.parent.parent.parent,          # Django project root
    Path(__file__).resolve().parent.parent.parent.parent.parent.parent,   # Project root
]

# Add all possible paths to sys.path
for path in possible_paths:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    
    # Also check if there's a src directory in this path
    src_path = Path(path) / 'src'
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Add config directory to path
    config_path = Path(path) / 'config'
    if config_path.exists() and str(config_path) not in sys.path:
        sys.path.insert(0, str(config_path))

# Print current paths for debugging
print(f"Current sys.path: {sys.path}")
print(f"Looking for src directory in: {possible_paths}")

# Now try to import the modules
try:
    from src.scrapers.imovirtual import ImoVirtualScraper
    from src.scrapers.idealista import IdealistaScraper
    from src.scrapers.remax import RemaxScraper
    from src.scrapers.era import EraScraper
    from src.scrapers.casa_sapo import CasaSapoScraper
    from src.scrapers.super_casa import SuperCasaScraper
    from src.messenger.ntfy_sender import NtfySender
    
    # Try different ways to import config settings
    try:
        from config.settings import (
            IMOVIRTUAL_URLS,
            REMAX_URLS,
            IDEALISTA_URLS,
            ERA_URL,
            CASA_SAPO_URLS,
            SUPER_CASA_URLS,
            SCRAPER_API_KEY,
        )
    except ImportError:
        # Try relative import if absolute import fails
        import sys
        sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent.parent))
        from config.settings import (
            IMOVIRTUAL_URLS,
            REMAX_URLS,
            IDEALISTA_URLS,
            ERA_URL,
            CASA_SAPO_URLS,
            SUPER_CASA_URLS,
            SCRAPER_API_KEY,
        )
    
    print("Successfully imported all modules")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current sys.path: {sys.path}")
    
    # Try to find the src directory
    for path in sys.path:
        src_dir = Path(path) / 'src'
        if src_dir.exists():
            print(f"Found src directory at: {src_dir}")
            if src_dir.is_dir():
                print(f"Contents of {src_dir}:")
                for item in src_dir.iterdir():
                    print(f"  - {item}")
    
    # Try to find the config directory
    for path in sys.path:
        config_dir = Path(path) / 'config'
        if config_dir.exists():
            print(f"Found config directory at: {config_dir}")
            if config_dir.is_dir():
                print(f"Contents of {config_dir}:")
                for item in config_dir.iterdir():
                    print(f"  - {item}")
    
    raise

# Create a global lock for database operations
db_lock = threading.Lock()

class Command(BaseCommand):
    help = 'Run house scrapers and save results directly to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scrapers',
            nargs='+',
            type=str,
            help='Specify scrapers to run (ImoVirtual, Idealista, Remax, ERA, CasaSapo, SuperCasa) or "all"'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all available scrapers'
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
            start_time = timezone.now()
            scraper_instance.run()
            end_time = timezone.now()
            
            # Calculate execution time in seconds
            execution_time = (end_time - start_time).total_seconds()
            
            # Update scraper run with execution time
            if hasattr(scraper_instance, 'current_run') and scraper_instance.current_run:
                with db_lock:
                    scraper_instance.current_run.execution_time = execution_time
                    scraper_instance.current_run.save()
            
            self.stdout.write(self.style.SUCCESS(f"[{scraper_name}] Finished scraper in {execution_time:.2f} seconds"))
            return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[{scraper_name}] Error in scraper: {str(e)}")
            )
            return False

    def handle(self, *args, **options):
        logger = self.setup_logger()
        
        # Use lock for database operations
        with db_lock:
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
            main_start_time = timezone.now()
            # Available scrapers - map both display names and lowercase keys
            available_scrapers = {
                'imovirtual': ('ImoVirtual', ImoVirtualScraper, IMOVIRTUAL_URLS, None),
                'idealista': ('Idealista', IdealistaScraper, IDEALISTA_URLS, SCRAPER_API_KEY),
                'remax': ('Remax', RemaxScraper, REMAX_URLS, None),
                'era': ('ERA', EraScraper, ERA_URL, None),
                'casasapo': ('CasaSapo', CasaSapoScraper, CASA_SAPO_URLS, None),
                'supercasa': ('SuperCasa', SuperCasaScraper, SUPER_CASA_URLS, None)
            }
            
            # Create a mapping from display names to keys (case-insensitive)
            name_to_key = {
                'imovirtual': 'imovirtual',
                'idealista': 'idealista',
                'remax': 'remax',
                'era': 'era',
                'casasapo': 'casasapo',
                'supercasa': 'supercasa',
            }

            # Determine which scrapers to run
            selected_scrapers = {}
            if options.get('all') or not options.get('scrapers') or 'all' in (options.get('scrapers') or []):
                selected_scrapers = available_scrapers
                self.stdout.write("Running all scrapers...")
            else:
                for scraper in options['scrapers']:
                    scraper_lower = scraper.lower()
                    if scraper_lower in name_to_key:
                        key = name_to_key[scraper_lower]
                        selected_scrapers[key] = available_scrapers[key]
                        self.stdout.write(f"Selected scraper: {available_scrapers[key][0]}")
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"Unknown scraper: {scraper}. "
                            f"Available: {', '.join([v[0] for v in available_scrapers.values()])}"
                        ))

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
                    
                # Set the main run for each scraper
                scrapers[name].set_main_run(main_run)
                
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
                            f"\n  Execution Time: {run.execution_time:.2f} seconds"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"\n{name}: No statistics available (scraper may have failed)")
                    )
            
            self.stdout.write(f"\nTotal houses processed: {total_houses}")
            self.stdout.write(f"Total new houses found: {new_houses}")
            
            # Calculate main run execution time
            main_end_time = timezone.now()
            main_execution_time = (main_end_time - main_start_time).total_seconds()
            
            # Update main run status
            with db_lock:
                main_run.status = 'completed'
                main_run.end_time = main_end_time
                main_run.execution_time = main_execution_time
                main_run.total_houses = total_houses
                main_run.new_houses = new_houses
                main_run.save()
            
            self.stdout.write(self.style.SUCCESS(f"\nTotal execution time: {main_execution_time:.2f} seconds"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error running scrapers: {str(e)}"))
            
            # Calculate execution time even for failed runs
            main_end_time = timezone.now()
            main_execution_time = (main_end_time - main_start_time).total_seconds()
            
            with db_lock:
                main_run.status = 'failed'
                main_run.error_message = str(e)
                main_run.end_time = main_end_time
                main_run.execution_time = main_execution_time
                main_run.save()