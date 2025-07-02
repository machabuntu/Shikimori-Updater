"""
Logging utility for Shikimori Updater
Provides both console and file logging
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime

class Logger:
    """Centralized logging for the application"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        Logger._initialized = True
        
        # Create logs directory
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            app_dir = Path.home() / ".shikimori_updater"
        else:
            # Running as script
            app_dir = Path.home() / ".shikimori_updater"
        
        self.log_dir = app_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger('ShikimoriUpdater')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler - always log to file
        log_file = self.log_dir / f"shikimori_updater_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler - only if console is available
        try:
            # Check if we have a console available
            if sys.stdout and sys.stdout.isatty():
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(simple_formatter)
                self.logger.addHandler(console_handler)
        except:
            # No console available (running as Windows app without console)
            pass
        
        # Log startup
        self.logger.info("=" * 50)
        self.logger.info("Shikimori Updater started")
        self.logger.info(f"Log file: {log_file}")
        self.logger.info("=" * 50)
    
    def get_logger(self, name=None):
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'ShikimoriUpdater.{name}')
        return self.logger
    
    def get_log_file_path(self):
        """Get the current log file path"""
        log_file = self.log_dir / f"shikimori_updater_{datetime.now().strftime('%Y%m%d')}.log"
        return str(log_file)

# Global logger instance
_global_logger = Logger()

def get_logger(name=None):
    """Get a logger instance"""
    return _global_logger.get_logger(name)

def get_log_file_path():
    """Get the current log file path"""
    return _global_logger.get_log_file_path()
