import csv
import json
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from houses.models import House, Photo
from decimal import Decimal, InvalidOperation

class Command(BaseCommand):
    help = 'Import houses from CSV file'

    # CSV field mappings (CSV column name -> model field name)
    field_mappings = {
        'Name': 'name',
        'Zone': 'zone',
        'Price': 'price',
        'URL': 'url',
        'Bedrooms': 'bedrooms',
        'Area': 'area',
        'Floor': 'floor',
        'Description': 'description',
        'Freguesia': 'freguesia',
        'Concelho': 'concelho',
        'Source': 'source',
        'Scraped At': 'scraped_at',
        'house_id': 'house_id'
    }

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def clean_decimal(self, value):
        """Clean and convert decimal values"""
        if not value:
            return Decimal('0')
        try:
            # Remove currency symbols, spaces, and commas
            cleaned = str(value).replace('€', '').replace(' ', '').replace(',', '')
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal('0')

    def clean_date(self, value):
        """Clean and convert date values"""
        if not value:
            return datetime.now()
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return datetime.now()

    def clean_image_urls(self, value):
        """Clean and convert image URLs"""
        if not value:
            return []
        if isinstance(value, list):
            return value
        try:
            # Try parsing as JSON
            return json.loads(value)
        except json.JSONDecodeError:
            # Try parsing as comma-separated string
            if isinstance(value, str):
                return [url.strip(' "[]\'') for url in value.split(',') if url.strip()]
            return []

    def generate_house_id(self, row):
        """Generate a unique house ID from row data"""
        unique_string = f"{row.get('URL', '')}-{row.get('Name', '')}-{row.get('Price', '')}-{row.get('Source', '')}"
        return str(abs(hash(unique_string)))

    def handle(self, *args, **options):
        csv_path = Path(options['csv_file'])
        if not csv_path.exists():
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        try:
            # Try different encodings if utf-8 fails
            encodings = ['utf-8', 'latin1', 'cp1252']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding) as f:
                        file_content = f.read()
                        break
                except UnicodeDecodeError:
                    continue

            if file_content is None:
                self.stdout.write(self.style.ERROR('Could not read file with any supported encoding'))
                return

            # Process the CSV content
            houses_created = 0
            houses_updated = 0
            errors = 0

            reader = csv.DictReader(file_content.splitlines())
            total_rows = sum(1 for row in csv.DictReader(file_content.splitlines()))
            
            self.stdout.write(self.style.SUCCESS(f'Found {total_rows} rows in CSV'))
            self.stdout.write(self.style.SUCCESS(f'CSV headers: {reader.fieldnames}'))

            for row in reader:
                try:
                    # Generate or get house_id
                    house_id = row.get('house_id') or self.generate_house_id(row)

                    # Prepare house data with cleaned values
                    house_data = {
                        'name': row.get('Name', '').strip(),
                        'zone': row.get('Zone', '').strip(),
                        'price': self.clean_decimal(row.get('Price')),
                        'url': row.get('URL', '').strip(),
                        'bedrooms': row.get('Bedrooms', '').strip(),
                        'area': self.clean_decimal(row.get('Area')),
                        'floor': row.get('Floor', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'freguesia': row.get('Freguesia', '').strip(),
                        'concelho': row.get('Concelho', '').strip(),
                        'source': row.get('Source', '').strip(),
                        'scraped_at': self.clean_date(row.get('Scraped At')),
                        'house_id': house_id
                    }

                    # Skip if essential fields are missing
                    if not house_data['url'] or not house_data['name']:
                        self.stdout.write(self.style.WARNING(f'Skipping row with missing essential data: {row}'))
                        errors += 1
                        continue

                    # Create or update house
                    house, created = House.objects.update_or_create(
                        house_id=house_id,
                        defaults=house_data
                    )

                    if created:
                        houses_created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Created house: {house.name[:30]}... (ID: {house.house_id})'
                        ))
                    else:
                        houses_updated += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Updated house: {house.name[:30]}... (ID: {house.house_id})'
                        ))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row: {str(e)}'))
                    self.stdout.write(self.style.ERROR(f'Problematic row: {row}'))
                    errors += 1
                    continue

            # Final summary
            self.stdout.write(self.style.SUCCESS(
                f'\nImport Summary:\n'
                f'Total rows in CSV: {total_rows}\n'
                f'Successfully created: {houses_created}\n'
                f'Successfully updated: {houses_updated}\n'
                f'Errors: {errors}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Fatal error during import: {str(e)}')) 