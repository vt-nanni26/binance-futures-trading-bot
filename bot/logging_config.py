"""
Logging configuration module
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the trading bot.
    
    Args:
        log_file: Path to the log file. If None, uses default naming.
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log file name with timestamp if not specified
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"trading_bot_{timestamp}.log"
    else:
        log_file = Path(log_file)
    
    # Configure root logger
    logger = logging.getLogger("TradingBot")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler for detailed logging
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Console handler for user-friendly output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger