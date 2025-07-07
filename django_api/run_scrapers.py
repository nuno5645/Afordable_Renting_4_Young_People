#!/usr/bin/env python
# coding: utf-8

import os
import sys
import django
from pathlib import Path

# Add the current directory and parent directories to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))
sys.path.insert(0, str(current_dir / 'api'))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Initialize Django
django.setup()

# Now import and run the scraper main
if __name__ == "__main__":
    from src.main import main
    main() 