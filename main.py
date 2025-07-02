#!/usr/bin/env python3
"""
Shikimori Updater - Main Application Entry Point
Tracks anime episodes from media players and updates Shikimori list
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Handle both development and PyInstaller environments
def setup_path():
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        application_path = sys._MEIPASS
        src_path = os.path.join(application_path, 'src')
    else:
        # Running as script
        application_path = os.path.dirname(__file__)
        src_path = os.path.join(application_path, 'src')
    
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

setup_path()

# Initialize logging first
from utils.logger import get_logger
logger = get_logger('main')

from gui.main_window import MainWindow
from core.config import Config

def main():
    """Main application entry point"""
    try:
        # Test logging
        logger.info("Starting Shikimori Updater application")
        
        # Initialize configuration
        config = Config()
        
        # Create main window
        root = tk.Tk()
        app = MainWindow(root, config)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
