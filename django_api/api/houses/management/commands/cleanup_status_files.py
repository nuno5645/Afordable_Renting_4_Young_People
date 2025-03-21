from django.core.management.base import BaseCommand
from pathlib import Path
import shutil

class Command(BaseCommand):
    help = 'Clean up old scraper status files that are no longer needed'

    def handle(self, *args, **options):
        # Path to the scraper status directory
        status_dir = Path("data/scraper_status")
        
        if status_dir.exists() and status_dir.is_dir():
            try:
                # Remove the entire directory and its contents
                shutil.rmtree(status_dir)
                self.stdout.write(self.style.SUCCESS(f"Successfully removed status directory: {status_dir}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error removing status directory: {str(e)}"))
        else:
            self.stdout.write(self.style.WARNING("Status directory not found, nothing to clean up")) 