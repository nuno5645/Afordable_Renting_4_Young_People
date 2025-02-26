#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import pandas as pd
import csv
from pathlib import Path
from datetime import datetime
from fix_csv import fix_csv_file
import argparse
import schedule

def check_csv_integrity():
    """Check if the CSV file is valid and fix it if needed"""
    csv_file = Path("data/houses.csv")
    
    # If CSV doesn't exist, nothing to check
    if not csv_file.exists():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV file doesn't exist yet. Nothing to check.")
        return False
    
    try:
        # Try to read the CSV file to check if it's valid
        df = pd.read_csv(csv_file, dtype=str, nrows=5)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV file is valid. No fix needed.")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV file is invalid: {str(e)}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running fix_csv_file...")
        fix_csv_file()
        return False

def run_scheduled_check():
    """Run the check and print a timestamp"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled CSV integrity check...")
    check_csv_integrity()

def parse_args():
    parser = argparse.ArgumentParser(description='CSV Integrity Checker')
    parser.add_argument('--check-only', action='store_true', help='Only check CSV integrity without scheduling')
    parser.add_argument('--interval', type=int, default=60, help='Check interval in minutes (default: 60)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Run an initial check
    check_result = check_csv_integrity()
    
    # If check-only flag is provided, exit after the check
    if args.check_only:
        sys.exit(0 if check_result else 1)
    
    # Schedule regular checks
    interval_minutes = max(1, args.interval)  # Ensure at least 1 minute
    print(f"Scheduling CSV integrity checks every {interval_minutes} minutes...")
    schedule.every(interval_minutes).minutes.do(run_scheduled_check)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCSV integrity checking interrupted by user")
        sys.exit(0) 