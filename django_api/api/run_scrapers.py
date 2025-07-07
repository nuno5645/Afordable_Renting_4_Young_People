#!/usr/bin/env python
# coding: utf-8

import os
import sys
from pathlib import Path

# Add the virtual environment's site-packages to Python path
current_dir = Path(__file__).parent.absolute()
venv_site_packages = current_dir / 'venv' / 'lib' / 'python3.12' / 'site-packages'
if venv_site_packages.exists():
    sys.path.insert(0, str(venv_site_packages))

# Add the parent directories to Python path
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / 'src'))
sys.path.insert(0, str(current_dir))

# Now try to import Django
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

# Initialize Django
django.setup()

# Now import and run the scraper main
if __name__ == "__main__":
    from src.main import main
    main() 