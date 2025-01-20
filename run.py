#!/usr/bin/env python
# coding: utf-8

import sys
import argparse
from src.main import main

def parse_args():
    parser = argparse.ArgumentParser(description='House Scraper')
    parser.add_argument('--less', action='store_true', help='Run all scrapers without menu')
    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = parse_args()
        main(use_menu=not args.less)
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
