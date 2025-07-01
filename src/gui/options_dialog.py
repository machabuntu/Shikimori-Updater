"""
Options Dialog - Configure application settings
"""

import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import os
import sys
from pathlib import Path

class OptionsDialog:
    """Dialog for configuring application settings"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.changes_made = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Options")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        self._create_widgets()
    
    def _center_dialog(self):
        """Center dialog on parent"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - 450) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - 400) // 2
        self.dialog.geometry(f"450x400+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Startup options
        startup_frame = ttk.LabelFrame(main_frame, text="Startup Options", padding="10")
        startup_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Add to Windows startup
        self.startup_var = tk.BooleanVar()
        startup_check = ttk.Checkbutton(startup_frame, text="Add application to Windows startup",
                                       variable=self.startup_var)
        startup_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Enable monitoring by default
        self.auto_monitor_var = tk.BooleanVar()
        auto_monitor_check = ttk.Checkbutton(startup_frame, text="Enable monitoring by default on start",
                                            variable=self.auto_monitor_var)
        auto_monitor_check.pack(anchor=tk.W)
        
        # Monitoring options
        monitor_frame = ttk.LabelFrame(main_frame, text="Monitoring Options", padding="10")
        monitor_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Watch time setting
        watch_time_frame = ttk.Frame(monitor_frame)
        watch_time_frame.pack(fill=tk.X)
        
        ttk.Label(watch_time_frame, text="Update anime progress after:").pack(side=tk.LEFT)
        
        self.watch_time_var = tk.IntVar()
        watch_time_spin = ttk.Spinbox(watch_time_frame, textvariable=self.watch_time_var,
                                     from_=1, to=60, width=5)
        watch_time_spin.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(watch_time_frame, text="minutes").pack(side=tk.LEFT)
        
        # System Tray options
        tray_frame = ttk.LabelFrame(main_frame, text="System Tray Options", padding="10")
        tray_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Minimize to tray
        self.minimize_to_tray_var = tk.BooleanVar()
        minimize_tray_check = ttk.Checkbutton(tray_frame, text="Minimize to system tray instead of taskbar",
                                            variable=self.minimize_to_tray_var)
        minimize_tray_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Close to tray
        self.close_to_tray_var = tk.BooleanVar()
        close_tray_check = ttk.Checkbutton(tray_frame, text="Close to system tray instead of exiting",
                                         variable=self.close_to_tray_var)
        close_tray_check.pack(anchor=tk.W)
        
        # Add note about dependencies
        try:
            import pystray
            from PIL import Image
        except ImportError:
            note_label = ttk.Label(tray_frame, text="Note: Install 'pystray' and 'pillow' packages for tray functionality", 
                                 foreground="orange", font=("Arial", 8))
            note_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Load current values
        self._load_current_values()
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(buttons_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(buttons_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def _load_current_values(self):
        """Load current configuration values"""
        # Check if app is in startup
        self.startup_var.set(self._is_in_startup())
        
        # Auto-monitor setting
        self.auto_monitor_var.set(self.config.get('monitoring.auto_start', False))
        
        # Watch time setting (convert from seconds to minutes)
        watch_time_seconds = self.config.get('monitoring.min_watch_time', 60)
        self.watch_time_var.set(watch_time_seconds // 60)
        
        # System tray settings
        self.minimize_to_tray_var.set(self.config.get('ui.minimize_to_tray', False))
        self.close_to_tray_var.set(self.config.get('ui.close_to_tray', False))
    
    def _is_in_startup(self):
        """Check if application is in Windows startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run")
            try:
                winreg.QueryValueEx(key, "ShikimoriUpdater")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def _add_to_startup(self):
        """Add application to Windows startup"""
        try:
            # Get path to executable
            if getattr(sys, 'frozen', False):
                # Running as exe
                app_path = sys.executable
            else:
                # Running as script
                app_path = f'"{sys.executable}" "{os.path.abspath("main.py")}"'
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "ShikimoriUpdater", 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to startup: {str(e)}")
            return False
    
    def _remove_from_startup(self):
        """Remove application from Windows startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "ShikimoriUpdater")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            # Already not in startup
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove from startup: {str(e)}")
            return False
    
    def _save_changes(self):
        """Save configuration changes"""
        try:
            # Handle startup setting
            if self.startup_var.get():
                if not self._is_in_startup():
                    if not self._add_to_startup():
                        return
            else:
                if self._is_in_startup():
                    if not self._remove_from_startup():
                        return
            
            # Save auto-monitor setting
            self.config.set('monitoring.auto_start', self.auto_monitor_var.get())
            
            # Save watch time setting (convert minutes to seconds)
            watch_time_minutes = self.watch_time_var.get()
            self.config.set('monitoring.min_watch_time', watch_time_minutes * 60)
            
            # Save system tray settings
            self.config.set('ui.minimize_to_tray', self.minimize_to_tray_var.get())
            self.config.set('ui.close_to_tray', self.close_to_tray_var.get())
            
            self.changes_made = True
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
