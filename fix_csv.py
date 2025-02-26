import pandas as pd
import csv
from pathlib import Path
import os
import shutil
import time
from datetime import datetime

def fix_csv_file():
    """Fix the CSV file by rewriting it with proper quoting and escaping"""
    csv_file = Path("data/houses.csv")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # If CSV doesn't exist, nothing to fix
    if not csv_file.exists():
        print("CSV file doesn't exist yet. Nothing to fix.")
        return
    
    try:
        # Create a timestamped backup of the original file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = csv_file.with_suffix(f'.csv.bak_{timestamp}')
        shutil.copy2(csv_file, backup_file)
        print(f"Created backup at {backup_file}")
        
        # Try to read the CSV file with different options if standard reading fails
        try:
            # First attempt with standard settings
            df = pd.read_csv(csv_file, dtype=str, on_bad_lines='warn')
        except Exception as e:
            print(f"Standard CSV reading failed: {str(e)}")
            try:
                # Second attempt with error handling
                df = pd.read_csv(csv_file, dtype=str, on_bad_lines='skip', error_bad_lines=False)
                print("Used fallback CSV reading with skipping bad lines")
            except Exception as e2:
                print(f"Fallback CSV reading failed: {str(e2)}")
                # Last resort: manual parsing
                try:
                    print("Attempting manual CSV parsing...")
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Get headers from first line
                    headers = lines[0].strip().split(',')
                    headers = [h.strip('"') for h in headers]
                    
                    # Create empty dataframe with these headers
                    df = pd.DataFrame(columns=headers)
                    
                    # Process remaining lines, skipping problematic ones
                    for i, line in enumerate(lines[1:], 1):
                        try:
                            # Use csv module to properly parse the line
                            values = next(csv.reader([line]))
                            if len(values) == len(headers):
                                df.loc[len(df)] = values
                        except Exception as line_error:
                            print(f"Skipping problematic line {i+1}: {str(line_error)}")
                    
                    print(f"Manual parsing completed. Recovered {len(df)} rows.")
                except Exception as e3:
                    print(f"Manual parsing failed: {str(e3)}")
                    # If all attempts fail, restore the backup and exit
                    print("All CSV parsing attempts failed. Restoring original file.")
                    shutil.copy2(backup_file, csv_file)
                    return
        
        # Clean the data - remove any control characters that might cause issues
        for col in df.columns:
            if df[col].dtype == 'object':  # Only process string columns
                # Replace control characters and ensure strings
                df[col] = df[col].apply(lambda x: ''.join(ch for ch in str(x) if ord(ch) >= 32 or ch in '\n\r\t') if pd.notna(x) else '')
        
        # Temporarily rename the original file
        temp_file = csv_file.with_suffix('.csv.temp')
        if csv_file.exists():
            csv_file.rename(temp_file)
        
        # Write the DataFrame back to CSV with proper quoting and escaping
        df.to_csv(csv_file, index=False, encoding='utf-8', quoting=csv.QUOTE_ALL, escapechar='\\')
        print(f"Successfully fixed the CSV file with {len(df)} rows")
        
        # Remove the temporary file if everything went well
        if temp_file.exists():
            temp_file.unlink()
        
        # Keep only the 5 most recent backups to save space
        backup_files = sorted(list(data_dir.glob('houses.csv.bak_*')))
        if len(backup_files) > 5:
            for old_backup in backup_files[:-5]:
                old_backup.unlink()
                print(f"Removed old backup: {old_backup}")
        
    except Exception as e:
        print(f"Error fixing CSV file: {str(e)}")
        # Restore from backup if something went wrong
        if 'backup_file' in locals() and backup_file.exists() and not csv_file.exists():
            shutil.copy2(backup_file, csv_file)
            print("Restored original file from backup")

if __name__ == "__main__":
    fix_csv_file() 