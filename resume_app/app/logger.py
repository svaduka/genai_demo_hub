import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Global logger object
logger = None

def configure_logging(app_name="gen_ai_app"):
    """Set up file and console logging with appropriate log levels and app name."""
    global logger
    
    if logger is not None:
        # If logger is already initialized, return the existing one
        return logger

    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Get the current date for log filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"logs/{app_name}_log_{current_date}.log"
    
    # Configure the logger with the app name
    logger = logging.getLogger(app_name)
    # logger.setLevel(logging.DEBUG)  # Set default level to DEBUG

    # Create file handler (log to file) with debug level
    file_handler = RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=5)  # Max 5MB per file, with 5 backups
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create console handler (log to console) with info level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"{app_name} logger initialized")

    return logger

def log_msg(msg, level=logging.INFO):
    """
    Utility function to log messages at different levels using the global logger.
    :param level: Log level ('info', 'debug', 'error').
    :param message: The message to log.
    """
    if logger is None:
        raise Exception("Logger is not initialized. Call configure_logging() first.")

    logger.log(level, msg)