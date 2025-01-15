import logging
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log messages"""
    
    def format(self, record):
        # Add colors based on log level
        if record.levelno >= logging.ERROR:
            color = Colors.ERROR
            record.levelname = f"[ERROR]"
        elif record.levelno >= logging.WARNING:
            color = Colors.WARNING
            record.levelname = f"[WARNING]"
        elif record.levelno >= logging.INFO:
            color = Colors.INFO
            record.levelname = f"[INFO]"
        else:
            color = Colors.INFO
            record.levelname = f"[DEBUG]"
            
        # Add action name if present
        if hasattr(record, 'action'):
            action_color = {
                'SCRAPING': Colors.HEADER,
                'PROCESSING': Colors.SUCCESS,
                'SAVING': Colors.WARNING,
            }.get(record.action, Colors.INFO)
            record.msg = f"{action_color}[{record.action}]{Colors.ENDC} {record.msg}"
            
        record.msg = f"{color}{record.msg}{Colors.ENDC}"
        return super().format(record)

def setup_logger(name):
    """Setup and return a logger instance with both file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    logger.handlers = []

    # File handler (without colors)
    file_handler = logging.FileHandler(f'logs/house_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler (with colors)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger
