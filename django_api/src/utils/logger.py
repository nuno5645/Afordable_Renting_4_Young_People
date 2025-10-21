import logging
import os
from datetime import datetime
from glob import glob

class Colors:
    HEADER = '\033[95m'      # Purple
    INFO = '\033[94m'        # Blue
    SUCCESS = '\033[92m'     # Green
    WARNING = '\033[93m'     # Yellow
    ERROR = '\033[91m'       # Red
    ENDC = '\033[0m'         # Reset
    BOLD = '\033[1m'         # Bold
    CYAN = '\033[96m'        # Cyan
    MAGENTA = '\033[35m'     # Magenta
    WHITE = '\033[97m'       # Bright White

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
            
        # Add action colors for different scraper operations
        action_colors = {
            'SCRAPING': Colors.HEADER,      # Purple for scraping operations
            'PROCESSING': Colors.SUCCESS,   # Green for processing
            'SAVING': Colors.WARNING,       # Yellow for saving operations
            'LOADING': Colors.CYAN,         # Cyan for loading data
            'INITIALIZING': Colors.MAGENTA, # Magenta for initialization
            'FILTERING': Colors.WHITE,      # White for filtering
            'ANALYZING': Colors.BOLD,       # Bold for analysis
        }
        
        # Check if record has action attribute and apply color
        if hasattr(record, 'action') and record.action:
            action_color = action_colors.get(record.action, Colors.INFO)
            record.msg = f"{action_color}[{record.action}]{Colors.ENDC} {record.msg}"
        else:
            # Check message content for operation keywords and apply colors
            msg_lower = str(record.msg).lower()
            if any(keyword in msg_lower for keyword in ['scraping', 'scrape']):
                record.msg = f"{Colors.HEADER}[SCRAPING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['processing', 'process']):
                record.msg = f"{Colors.SUCCESS}[PROCESSING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['saving', 'save', 'saved']):
                record.msg = f"{Colors.WARNING}[SAVING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['loading', 'load', 'loaded']):
                record.msg = f"{Colors.CYAN}[LOADING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['initializing', 'initialized', 'starting']):
                record.msg = f"{Colors.MAGENTA}[INITIALIZING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['filtering', 'filter']):
                record.msg = f"{Colors.WHITE}[FILTERING]{Colors.ENDC} {record.msg}"
            elif any(keyword in msg_lower for keyword in ['analyzing', 'analysis']):
                record.msg = f"{Colors.BOLD}[ANALYZING]{Colors.ENDC} {record.msg}"
            
        record.msg = f"{color}{record.msg}{Colors.ENDC}"
        return super().format(record)

def cleanup_old_logs(max_logs=5):
    """Keep only the most recent log files"""
    log_files = glob('logs/house_scraper_*.log')
    log_files.sort(reverse=True)
    for old_log in log_files[max_logs:]:
        try:
            os.remove(old_log)
        except OSError:
            pass

def setup_logger(name):
    """Setup and return a logger instance with both file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Disable propagation to prevent duplicate logs from parent loggers
    logger.propagate = False

    # Remove any existing handlers
    logger.handlers = []

    # Clean up old logs before creating new one
    cleanup_old_logs()

    # File handler (without colors)
    file_handler = logging.FileHandler(f'logs/house_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    # Console handler (with colors)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger

class ScraperLogger:
    """Enhanced logger wrapper with action-specific methods for scraper operations"""
    
    def __init__(self, logger_name):
        self.logger = setup_logger(logger_name)
    
    def _log_with_action(self, level, action, message):
        """Log a message with a specific action type"""
        record = self.logger.makeRecord(
            self.logger.name, level, '', 0, message, (), None
        )
        record.action = action
        self.logger.handle(record)
    
    def scraping(self, message):
        """Log scraping operations in purple"""
        self._log_with_action(logging.INFO, 'SCRAPING', message)
    
    def processing(self, message):
        """Log processing operations in green"""
        self._log_with_action(logging.INFO, 'PROCESSING', message)
    
    def saving(self, message):
        """Log saving operations in yellow"""
        self._log_with_action(logging.INFO, 'SAVING', message)
    
    def loading(self, message):
        """Log loading operations in cyan"""
        self._log_with_action(logging.INFO, 'LOADING', message)
    
    def initializing(self, message):
        """Log initialization operations in magenta"""
        self._log_with_action(logging.INFO, 'INITIALIZING', message)
    
    def filtering(self, message):
        """Log filtering operations in white"""
        self._log_with_action(logging.INFO, 'FILTERING', message)
    
    def analyzing(self, message):
        """Log analysis operations in bold"""
        self._log_with_action(logging.INFO, 'ANALYZING', message)
    
    def info(self, message):
        """Regular info log"""
        self.logger.info(message)
    
    def warning(self, message):
        """Warning log"""
        self.logger.warning(message)
    
    def error(self, message):
        """Error log"""
        self.logger.error(message)
    
    def debug(self, message):
        """Debug log"""
        self.logger.debug(message)
