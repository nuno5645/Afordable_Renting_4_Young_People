#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
import os
from src.main import main
from fix_csv import fix_csv_file

def parse_args():
    parser = argparse.ArgumentParser(description='House Scraper')
    parser.add_argument('--less', action='store_true', help='Run all scrapers without menu')
    parser.add_argument('--fix-csv-only', action='store_true', help='Only run the CSV fix script without scraping')
    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = parse_args()
        
        # If --fix-csv-only flag is provided, only run the CSV fix script
        if args.fix_csv_only:
            print("Running CSV fix script...")
            fix_csv_file()
            print("CSV fix completed.")
            sys.exit(0)
            
        # Run the main scraping process
        main(use_menu=not args.less)
        
        # After successful scraping, run the CSV fix script to ensure the CSV is valid
        print("Scraping completed. Running CSV fix script...")
        fix_csv_file()
        print("CSV fix completed.")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        # Try to fix CSV even if interrupted
        try:
            print("Running CSV fix script...")
            fix_csv_file()
            print("CSV fix completed.")
        except Exception as csv_error:
            print(f"Error fixing CSV after interruption: {str(csv_error)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        # Try to fix CSV even if there was an error
        try:
            print("Running CSV fix script...")
            fix_csv_file()
            print("CSV fix completed.")
        except Exception as csv_error:
            print(f"Error fixing CSV after error: {str(csv_error)}")
        sys.exit(1)
