"""
Main GUI Window for Shikimori Updater
"""

import tkinter as tk
from tkinter import ttk, messagebox
try:
    from tkinter import simpledialog
except ImportError:
    import tkinter.simpledialog as simpledialog
import threading
import webbrowser
import os
from typing import Dict, List, Any, Optional
try:
    import pystray
    from PIL import Image, ImageDraw
    # Test that pystray can be initialized
    test_image = Image.new('RGB', (16, 16), 'black')
    test_icon = pystray.Icon('test', test_image)
    TRAY_AVAILABLE = True
    print("System tray functionality available")
except ImportError as e:
    print(f"System tray not available - ImportError: {e}")
    TRAY_AVAILABLE = False
except Exception as e:
    print(f"System tray not available - Error: {e}")
    TRAY_AVAILABLE = False

from api.shikimori_client import ShikimoriClient
from utils.player_monitor import PlayerMonitor, EpisodeInfo
from utils.anime_matcher import AnimeMatcher
from utils.enhanced_anime_matcher import EnhancedAnimeMatcher
from gui.auth_dialog import AuthDialog
from gui.anime_list_frame import AnimeListFrame
from gui.search_frame import SearchFrame
from gui.options_dialog import OptionsDialog
from core.cache import CacheManager

class MainWindow:
    """Main application window"""
    
    def __init__(self, root: tk.Tk, config):
        self.root = root
        self.config = config
        self.shikimori = ShikimoriClient(config)
        self.player_monitor = PlayerMonitor(config)
        self.cache_manager = CacheManager(config)
        # Use enhanced matcher with synonym support
        self.anime_matcher = EnhancedAnimeMatcher(self.shikimori, self.cache_manager)
        
        # Data
        self.current_user = None
        self.anime_list_data: Dict[str, List[Dict[str, Any]]] = {}
        self.monitoring_active = False
        self.tray_icon = None
        self.window_minimized = False
        
        # Setup window
        self._setup_window()
        self._create_widgets()
        self._setup_monitoring()
        
        # Load initial data if authenticated
        if config.is_authenticated:
            self._load_user_data()
            
            # Auto-start monitoring if enabled
            if self.config.get('monitoring.auto_start', False):
                self.root.after(2000, self._toggle_monitoring)  # Start after 2 seconds delay
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Shikimori Updater")
        
        # Set window size and position
        width = self.config.get('window.width', 1000)
        height = self.config.get('window.height', 700)
        x = self.config.get('window.x')
        y = self.config.get('window.y')
        
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")
            # Center window
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Save window position on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Handle window state changes for tray functionality
        self.root.bind('<Unmap>', self._on_minimize)
        self.root.bind('<Map>', self._on_restore)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialize system tray if available
        if TRAY_AVAILABLE:
            self._setup_system_tray()
    
    def _create_widgets(self):
        """Create main window widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        self._create_toolbar(main_frame)
        
        # Status bar
        self._create_status_bar(main_frame)
        
        # Main content area
        self._create_content_area(main_frame)
    
    def _create_toolbar(self, parent):
        """Create toolbar with main controls"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Menu dropdown
        menu_frame = ttk.Frame(toolbar)
        menu_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2)
        
        self.menu_button = ttk.Menubutton(menu_frame, text="Menu")
        self.menu_button.pack(side=tk.LEFT)
        
        # Create dropdown menu
        self.menu = tk.Menu(self.menu_button, tearoff=0)
        self.menu_button.config(menu=self.menu)
        
        self.menu.add_command(label="Authentication...", command=self._handle_auth)
        self.menu.add_separator()
        self.menu.add_command(label="Start/Stop Monitoring", command=self._toggle_monitoring)
        self.menu.add_separator()
        self.menu.add_command(label="Refresh List", command=lambda: self._refresh_list(force_refresh=True))
        self.menu.add_separator()
        self.menu.add_command(label="Options...", command=self._show_options)
        # Add cache management to menu
        self.menu.add_separator()
        self.menu.add_command(label="Clear Cache", command=self._clear_cache)
        self.menu.add_command(label="Refresh Synonyms", command=self._refresh_synonyms)
        
        # User status
        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2)
        
        self.user_label = ttk.Label(user_frame, text="Not logged in")
        self.user_label.pack(side=tk.LEFT)
        
        # Monitoring status
        monitor_status_frame = ttk.Frame(toolbar)
        monitor_status_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2)
        
        ttk.Label(monitor_status_frame, text="Monitoring:").pack(side=tk.LEFT, padx=(0, 5))
        self.monitor_status = ttk.Label(monitor_status_frame, text="Stopped", foreground="red")
        self.monitor_status.pack(side=tk.LEFT)
        
        # Compact anime info panel  
        self._create_compact_anime_info(toolbar)
    
    def _create_compact_anime_info(self, parent):
        """Create a compact anime info panel in the toolbar"""
        info_frame = ttk.LabelFrame(parent, text="Selected Anime")
        info_frame.pack(side=tk.LEFT, padx=(0, 10), pady=2, ipadx=5, ipady=2)

        # Anime name (shortened)
        self.compact_anime_name_var = tk.StringVar(value="None")
        name_label = ttk.Label(info_frame, textvariable=self.compact_anime_name_var, font=("Arial", 9, "bold"))
        name_label.pack(side=tk.LEFT, padx=(2, 10))

        # Progress control
        progress_frame = ttk.Frame(info_frame)
        progress_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(progress_frame, text="Ep:").pack(side=tk.LEFT, padx=(0, 2))

        # Episode entry (compact)
        self.compact_episode_var = tk.StringVar(value="0")
        self.compact_episode_entry = ttk.Entry(progress_frame, textvariable=self.compact_episode_var, width=4, justify=tk.CENTER)
        self.compact_episode_entry.pack(side=tk.LEFT, padx=2)
        self.compact_episode_entry.bind('<Return>', self._on_compact_episode_entry)
        self.compact_episode_entry.bind('<FocusOut>', self._on_compact_episode_entry)
        self.compact_episode_entry.bind('<FocusIn>', self._on_compact_episode_focus_in)
        self.compact_episode_entry.bind('<KeyPress>', self._on_compact_episode_key_press)

        self.compact_total_episodes_var = tk.StringVar(value="/?")
        ttk.Label(progress_frame, textvariable=self.compact_total_episodes_var).pack(side=tk.LEFT, padx=(2, 0))

        # Status control (compact)
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 2))

        self.compact_status_var = tk.StringVar(value="-")
        self.compact_status_combo = ttk.Combobox(status_frame, textvariable=self.compact_status_var,
                                                values=["-"] + list(self.shikimori.STATUSES.values()),
                                                width=12, state="readonly")
        self.compact_status_combo.pack(side=tk.LEFT)
        self.compact_status_combo.bind('<<ComboboxSelected>>', self._on_compact_status_changed)

        # Score control (compact)
        score_frame = ttk.Frame(info_frame)
        score_frame.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(score_frame, text="Score:").pack(side=tk.LEFT, padx=(0, 2))

        self.compact_score_var = tk.StringVar(value="-")
        self.compact_score_combo = ttk.Combobox(score_frame, textvariable=self.compact_score_var,
                                               values=["-"] + [str(i) for i in range(1, 11)],
                                               width=3, state="readonly")
        self.compact_score_combo.pack(side=tk.LEFT)
        self.compact_score_combo.bind('<<ComboboxSelected>>', self._on_compact_score_changed)
        
        # Initially disable controls
        self._set_compact_controls_enabled(False)
    
    def _create_monitoring_info_panel(self, parent):
        """Create a panel to show current monitoring status"""
        monitor_frame = ttk.Frame(parent, padding="5")
        monitor_frame.pack(side=tk.RIGHT, padx=(10, 0), pady=5)

        self.current_anime_var = tk.StringVar(value="Now Watching: None")
        ttk.Label(monitor_frame, textvariable=self.current_anime_var, font=("Arial", 10)).pack(anchor=tk.W)

    def _create_status_bar(self, parent):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Status message on the left
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(
            fill=tk.X, side=tk.LEFT)
        
        # Add monitoring info panel on the right
        self._create_monitoring_info_panel(status_frame)
    
    def _create_anime_info_panel(self, parent):
        """Create anime info panel with controls"""
        self.selected_anime = None
        
        info_frame = ttk.LabelFrame(parent, text="Selected Anime", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main info area
        main_info = ttk.Frame(info_frame)
        main_info.pack(fill=tk.X)
        
        # Left side - Anime info
        left_frame = ttk.Frame(main_info)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Anime name
        self.anime_name_var = tk.StringVar(value="No anime selected")
        anime_name_label = ttk.Label(left_frame, textvariable=self.anime_name_var, 
                                    font=("Arial", 11, "bold"))
        anime_name_label.pack(anchor=tk.W)
        
        # Anime details
        self.anime_details_var = tk.StringVar(value="")
        anime_details_label = ttk.Label(left_frame, textvariable=self.anime_details_var, 
                                       foreground="gray")
        anime_details_label.pack(anchor=tk.W)
        
        # Right side - Controls
        controls_frame = ttk.Frame(main_info)
        controls_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Progress control
        progress_frame = ttk.Frame(controls_frame)
        progress_frame.pack(pady=(0, 10))
        
        ttk.Label(progress_frame, text="Episodes:").pack(side=tk.LEFT)
        
        # Decrease button
        self.decrease_btn = ttk.Button(progress_frame, text="-", width=3,
                                      command=self._decrease_progress)
        self.decrease_btn.pack(side=tk.LEFT, padx=(5, 2))
        
        # Episode entry
        self.episode_var = tk.StringVar(value="0")
        self.episode_entry = ttk.Entry(progress_frame, textvariable=self.episode_var, 
                                      width=8, justify=tk.CENTER)
        self.episode_entry.pack(side=tk.LEFT, padx=2)
        self.episode_entry.bind('<Return>', self._on_episode_entry)
        self.episode_entry.bind('<FocusOut>', self._on_episode_entry)
        self.episode_entry.bind('<FocusIn>', self._on_episode_focus_in)
        self.episode_entry.bind('<KeyPress>', self._on_episode_key_press)
        
        # Total episodes label
        self.total_episodes_var = tk.StringVar(value="/ ?")
        ttk.Label(progress_frame, textvariable=self.total_episodes_var).pack(side=tk.LEFT, padx=(2, 5))
        
        # Increase button
        self.increase_btn = ttk.Button(progress_frame, text="+", width=3,
                                      command=self._increase_progress)
        self.increase_btn.pack(side=tk.LEFT, padx=(2, 5))
        
        # Score control
        score_frame = ttk.Frame(controls_frame)
        score_frame.pack()
        
        ttk.Label(score_frame, text="Score:").pack(side=tk.LEFT)
        
        self.score_var = tk.StringVar(value="Not scored")
        self.score_combo = ttk.Combobox(score_frame, textvariable=self.score_var,
                                       values=["Not scored"] + [str(i) for i in range(1, 11)],
                                       width=12, state="readonly")
        self.score_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.score_combo.bind('<<ComboboxSelected>>', self._on_score_changed)
        
        # Initially disable controls
        self._set_compact_controls_enabled(False)
    
    def _create_content_area(self, parent):
        """Create main content area with notebook"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Anime List tab
        self.anime_list_frame = AnimeListFrame(self.notebook, self)
        self.notebook.add(self.anime_list_frame, text="Anime List")
        
        # Search tab
        self.search_frame = SearchFrame(self.notebook, self)
        self.notebook.add(self.search_frame, text="Search & Add")
    
    def _setup_monitoring(self):
        """Setup player monitoring callbacks"""
        self.player_monitor.on_episode_detected = self._on_episode_detected
        self.player_monitor.on_episode_watched = self._on_episode_watched
        self.player_monitor.on_player_closed = self._on_player_closed
    
    def _handle_auth(self):
        """Handle authentication"""
        if self.config.is_authenticated:
            # Already authenticated, offer to logout
            if messagebox.askyesno("Logout", "Do you want to logout from Shikimori?"):
                self._logout()
        else:
            # Show authentication dialog
            auth_dialog = AuthDialog(self.root, self.config, self.shikimori)
            self.root.wait_window(auth_dialog.dialog)
            
            if self.config.is_authenticated:
                self._load_user_data()
    
    def _logout(self):
        """Logout from Shikimori"""
        self.config.set('shikimori.access_token', None)
        self.config.set('shikimori.refresh_token', None)
        self.config.set('shikimori.user_id', None)
        
        self.current_user = None
        self.anime_list_data.clear()
        
        self._update_auth_ui()
        self.anime_list_frame.clear_list()
        self._set_status("Logged out")
    
    def _load_user_data(self):
        """Load user data from Shikimori"""
        def load_data():
            try:
                self._set_status("Loading user data...")
                
                # Get current user
                self.current_user = self.shikimori.get_current_user()
                if not self.current_user:
                    messagebox.showerror("Error", "Failed to get user information")
                    return
                
                # Update UI on main thread
                self.root.after(0, self._update_auth_ui)
                
                # Load anime list
                self._refresh_list_data()
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load user data: {str(e)}"))
                self.root.after(0, lambda: self._set_status("Error loading data"))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def _refresh_list(self, force_refresh: bool = False):
        """Refresh anime list from Shikimori"""
        if not self.config.is_authenticated:
            messagebox.showwarning("Warning", "Please login to Shikimori first")
            return
        
        def refresh_data():
            try:
                self._refresh_list_data(force_refresh=force_refresh)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh list: {str(e)}"))
                self.root.after(0, lambda: self._set_status("Error refreshing list"))
        
        threading.Thread(target=refresh_data, daemon=True).start()
    
    def _reload_from_cache(self):
        """Reload anime list from cache (for reflecting manual updates)"""
        if not self.current_user:
            return
        
        def reload_data():
            try:
                user_id = self.current_user['id']
                cached_data = self.cache_manager.load_anime_list(user_id)
                
                if cached_data:
                    self.anime_list_data = cached_data
                    total_anime = sum(len(anime_list) for anime_list in cached_data.values())
                    
                    # Update UI on main thread
                    self.root.after(0, lambda: self.anime_list_frame.update_list(self.anime_list_data))
                    self.root.after(0, lambda: self._set_status(f"Updated from cache - {total_anime} anime"))
                else:
                    # Fallback to full refresh if cache not available
                    self.root.after(0, lambda: self._refresh_list(force_refresh=True))
                    
            except Exception as e:
                print(f"Error reloading from cache: {e}")
                # Fallback to full refresh on error
                self.root.after(0, lambda: self._refresh_list(force_refresh=True))
        
        threading.Thread(target=reload_data, daemon=True).start()
    
    def _refresh_list_data(self, force_refresh: bool = False):
        """Refresh anime list data (called from background thread)"""
        if not self.current_user:
            return
        
        user_id = self.current_user['id']
        
        # Try to load from cache first (unless forced refresh)
        if not force_refresh:
            self.root.after(0, lambda: self._set_status("Loading anime list from cache..."))
            cached_data = self.cache_manager.load_anime_list(user_id)
            
            if cached_data:
                self.anime_list_data = cached_data
                total_anime = sum(len(anime_list) for anime_list in cached_data.values())
                
                # Update UI on main thread
                self.root.after(0, lambda: self.anime_list_frame.update_list(self.anime_list_data))
                self.root.after(0, lambda: self._set_status(f"Anime list loaded from cache - {total_anime} anime"))
                
                # Initialize enhanced matching with synonyms
                if self.current_user:
                    self.anime_matcher.initialize_detailed_cache(self.current_user['id'], self.anime_list_data)
                return
        
        # Load from API if no cache or forced refresh
        self.root.after(0, lambda: self._set_status("Refreshing anime list from Shikimori..."))
        
        total_anime = 0
        
        # Load all statuses
        for i, status_key in enumerate(self.shikimori.STATUSES.keys()):
            status_display = self.shikimori.STATUSES[status_key]
            self.root.after(0, lambda s=status_display: self._set_status(f"Loading {s} anime..."))
            
            anime_list = self.shikimori.get_user_anime_list(user_id, status_key)
            self.anime_list_data[status_key] = anime_list
            total_anime += len(anime_list)
            
            # Update progress
            progress = f"Loaded {total_anime} anime so far..."
            self.root.after(0, lambda p=progress: self._set_status(p))
        
        # Save to cache
        self.cache_manager.save_anime_list(user_id, self.anime_list_data)
        
        # Update UI on main thread
        self.root.after(0, lambda: self.anime_list_frame.update_list(self.anime_list_data))
        self.root.after(0, lambda: self._set_status(f"Anime list updated - {total_anime} anime loaded"))
        
        # Initialize enhanced matching with synonyms
        if self.current_user:
            self.anime_matcher.initialize_detailed_cache(self.current_user['id'], self.anime_list_data)
    
    def _update_auth_ui(self):
        """Update authentication UI elements"""
        if self.current_user:
            username = self.current_user.get('nickname', 'Unknown')
            self.user_label.config(text=f"Logged in as: {username}")
        else:
            self.user_label.config(text="Not logged in")
    
    def _toggle_monitoring(self):
        """Toggle player monitoring"""
        if not self.config.is_authenticated:
            messagebox.showwarning("Warning", "Please login to Shikimori first")
            return
        
        if self.monitoring_active:
            self.player_monitor.stop_monitoring()
            self.monitoring_active = False
            self.monitor_status.config(text="Stopped", foreground="red")
            self.current_anime_var.set("Now Watching: None")  # Clear current episode display
        else:
            self.player_monitor.start_monitoring()
            self.monitoring_active = True
            self.monitor_status.config(text="Active", foreground="green")
    
    def _on_episode_detected(self, episode_info: EpisodeInfo):
        """Handle detected episode"""
        # Check if anime is in user's list
        if self._is_anime_in_list(episode_info.anime_name):
            anime_display = f"Now Watching: {episode_info.anime_name} - Episode {episode_info.episode_number}"
        else:
            anime_display = f"Anime not in list: {episode_info.anime_name} - Episode {episode_info.episode_number}"
        
        self.root.after(0, lambda: self.current_anime_var.set(anime_display))
    
    def _on_episode_watched(self, episode_info: EpisodeInfo, watch_time: float):
        """Handle watched episode"""
        def process_episode():
            try:
                # Find matching anime in user's list
                all_anime = []
                for anime_list in self.anime_list_data.values():
                    all_anime.extend(anime_list)
                
                match_result = self.anime_matcher.find_best_match(
                    episode_info.anime_name, all_anime, episode_info.episode_number)
                
                if match_result:
                    anime_entry, similarity = match_result
                    anime_data = anime_entry['anime']
                    anime_name = anime_data.get('name', episode_info.anime_name)
                    
                    # Check if episode number is +1 from current progress
                    current_episodes = anime_entry.get('episodes', 0)
                    target_episode = episode_info.episode_number
                    
                    # Allow update if episode is next (+1) or if we want to allow re-watching same episode
                    if target_episode == current_episodes + 1 or target_episode == current_episodes:
                        # Update progress
                        rate_id = anime_entry['id']
                        anime_data = anime_entry['anime']
                        total_episodes = anime_data.get('episodes', 0)
                        
                        # Determine new status
                        new_status = None
                        if total_episodes > 0 and target_episode >= total_episodes:
                            # Check if anime is scored
                            current_score = anime_entry.get('score', 0)
                            if current_score > 0:
                                new_status = 'completed'
                        
                        # Update on Shikimori
                        success = self.shikimori.update_anime_progress(
                            rate_id, target_episode, status=new_status)
                        
                        if success:
                            anime_name = anime_data.get('name', episode_info.anime_name)
                            message = f"Updated {anime_name} to episode {target_episode}"
                            if new_status == 'completed':
                                message += " (Completed)"
                            
                            self.root.after(0, lambda: self._set_status(message))
                            # Update only this specific anime in the list instead of full refresh
                            # Update the local data first
                            anime_entry['episodes'] = target_episode
                            if new_status:
                                anime_entry['status'] = new_status
                            self.root.after(0, lambda: self._update_single_anime(anime_entry))
                        else:
                            self.root.after(0, lambda: self._set_status(
                                f"Failed to update {episode_info.anime_name}"))
                    else:
                        self.root.after(0, lambda: self._set_status(
                            f"Episode {target_episode} is not next for {episode_info.anime_name}"))
                else:
                    self.root.after(0, lambda: self._set_status(
                        f"No match found for {episode_info.anime_name}"))
                    
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error processing episode: {str(e)}"))
        
        threading.Thread(target=process_episode, daemon=True).start()
    
    def _is_anime_in_list(self, anime_name: str) -> bool:
        """Check if anime is in user's list using fuzzy matching"""
        if not self.anime_list_data:
            return False
        
        # Get all anime from user's list
        all_anime = []
        for anime_list in self.anime_list_data.values():
            all_anime.extend(anime_list)
        
        # Use anime matcher to find if there's a match
        match_result = self.anime_matcher.find_best_match(anime_name, all_anime)
        return match_result is not None
    
    def _on_player_closed(self):
        """Handle when player is closed - clear the monitoring panel"""
        # Always clear the panel when any player closes for now
        self.current_anime_var.set("Now Watching: None")
    
    def _set_status(self, message: str, auto_clear: bool = True):
        """Set status bar message"""
        self.status_var.set(message)
        # Auto-clear status after 10 seconds if requested
        if auto_clear and not message.startswith(("Loading", "Loaded", "Refreshing")):
            self.root.after(10000, lambda: self.status_var.set("") 
                           if self.status_var.get() == message else None)
    
    def _on_closing(self):
        """Handle window closing"""
        # Check if should close to tray
        if self.config.get('ui.close_to_tray', False) and TRAY_AVAILABLE:
            self._hide_to_tray()
            return
        
        self._actually_close()
    
    def _actually_close(self):
        """Actually close the application"""
        # Save window position
        geometry = self.root.geometry()
        parts = geometry.split('+')
        if len(parts) >= 3:
            size = parts[0]
            x = parts[1]
            y = parts[2]
            
            width, height = size.split('x')
            self.config.set('window.width', int(width))
            self.config.set('window.height', int(height))
            self.config.set('window.x', int(x))
            self.config.set('window.y', int(y))
        
        # Stop monitoring
        if self.monitoring_active:
            self.player_monitor.stop_monitoring()
        
        # Stop system tray
        if self.tray_icon and hasattr(self.tray_icon, 'stop'):
            try:
                self.tray_icon.stop()
            except:
                pass
        
        self.root.destroy()
    
    # Public methods for other components
    def get_shikimori_client(self) -> ShikimoriClient:
        """Get Shikimori client instance"""
        return self.shikimori
    
    def get_anime_list_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get current anime list data"""
        return self.anime_list_data
    
    def refresh_anime_list(self):
        """Public method to refresh anime list (forces full refresh and cache rebuild)"""
        self._refresh_list(force_refresh=True)
    
    # Anime info panel methods
    def set_selected_anime(self, anime_entry: Optional[Dict[str, Any]]):
        """Set the currently selected anime in the info panel"""
        # If we're changing selection and there are pending changes, apply them to the current anime first
        if hasattr(self, 'selected_anime') and hasattr(self, 'episode_editing_anime') and self.selected_anime and anime_entry != self.selected_anime:
            self._commit_pending_episode_changes()
        
        self.selected_anime = anime_entry
        
        if anime_entry:
            anime = anime_entry.get('anime', {})
            
            # Update compact panel
            name = anime.get('name', 'Unknown')
            # Truncate long names for compact display
            if len(name) > 25:
                display_name = name[:22] + "..."
            else:
                display_name = name
            self.compact_anime_name_var.set(display_name)
            
            # Update progress in compact panel
            current_episodes = anime_entry.get('episodes', 0)
            total_episodes = anime.get('episodes', 0)
            self.compact_episode_var.set(str(current_episodes))
            self.compact_total_episodes_var.set(f"/{total_episodes if total_episodes else '?'}")
            
            # Note: Main episode entry removed - only using compact panel
            
            # Update status in compact panel
            status = anime_entry.get('status', '')
            if status in self.shikimori.STATUSES:
                status_display = self.shikimori.STATUSES[status]
                self.compact_status_var.set(status_display)
            else:
                self.compact_status_var.set("-")
            
            # Update score in compact panel
            score = anime_entry.get('score', 0)
            if score > 0:
                self.compact_score_var.set(str(score))
            else:
                self.compact_score_var.set("-")
            
            # Enable compact controls
            self._set_compact_controls_enabled(True)
        else:
            # Clear compact selection
            self.compact_anime_name_var.set("None")
            self.compact_episode_var.set("0")
            self.compact_total_episodes_var.set("/?")
            self.compact_status_var.set("-")
            self.compact_score_var.set("-")
            
            # Note: Main episode entry removed - only using compact panel
            
            # Disable compact controls
            self._set_compact_controls_enabled(False)
    
    def _set_controls_enabled(self, enabled: bool):
        """Enable or disable the anime controls (placeholder - only compact controls used)"""
        pass
    
    def _decrease_progress(self):
        """Decrease episode progress by 1"""
        if not self.selected_anime:
            return
        
        try:
            current = int(self.compact_episode_var.get())
            new_value = max(0, current - 1)
            self.compact_episode_var.set(str(new_value))
            self._update_progress(new_value)
        except ValueError:
            pass
    
    def _increase_progress(self):
        """Increase episode progress by 1"""
        if not self.selected_anime:
            return
        
        try:
            current = int(self.compact_episode_var.get())
            total = self.selected_anime['anime'].get('episodes', 9999)
            new_value = min(total if total else 9999, current + 1)
            self.compact_episode_var.set(str(new_value))
            self._update_progress(new_value)
        except ValueError:
            pass
    
    # Main episode entry methods removed - only using compact panel now
    
    # Main score change method removed - only using compact panel now
    
    def _commit_pending_episode_changes(self):
        """Commit any pending episode changes before changing selection"""
        if hasattr(self, 'episode_editing_anime') and self.episode_editing_anime and hasattr(self, 'episode_editing_original_value') and self.episode_editing_original_value is not None:
            try:
                current_value = self.compact_episode_var.get()
                if current_value != self.episode_editing_original_value:
                    new_value = int(current_value)
                    total = self.episode_editing_anime['anime'].get('episodes', 9999)
                    new_value = max(0, min(total if total else 9999, new_value))
                    
                    current_episodes = self.episode_editing_anime.get('episodes', 0)
                    if new_value != current_episodes:
                        self._update_progress_for_anime(self.episode_editing_anime, new_value)
            except ValueError:
                pass
            
            # Clear editing state
            self.episode_editing_anime = None
            self.episode_editing_original_value = None
    
    def _update_progress(self, episodes: int):
        """Update anime progress on Shikimori"""
        if not self.selected_anime:
            return
        
        self._update_progress_for_anime(self.selected_anime, episodes)
    
    def _update_progress_for_anime(self, anime_entry: Dict[str, Any], episodes: int):
        """Update anime progress on Shikimori for specific anime"""
        if not anime_entry:
            return
        
        def update_data():
            try:
                rate_id = anime_entry['id']
                anime_name = anime_entry['anime'].get('name', 'Unknown')
                
                # Check if should auto-complete
                total_episodes = anime_entry['anime'].get('episodes', 0)
                current_score = anime_entry.get('score', 0)
                current_status = anime_entry.get('status', '')
                new_status = None
                rewatches_increment = 0
                
                # Special logic for Rewatching status
                if current_status == 'rewatching' and total_episodes > 0 and episodes >= total_episodes:
                    # Auto-complete from Rewatching and increment rewatches
                    new_status = 'completed'
                    rewatches_increment = 1
                elif total_episodes > 0 and episodes >= total_episodes and current_score > 0:
                    new_status = 'completed'
                
                # Prepare rewatches field for API call
                additional_fields = {}
                if rewatches_increment > 0:
                    current_rewatches = anime_entry.get('rewatches', 0) or 0
                    additional_fields['rewatches'] = current_rewatches + rewatches_increment
                
                success = self.shikimori.update_anime_progress(
                    rate_id, episodes=episodes, status=new_status, **additional_fields)
                
                if success:
                    message = f"Updated {anime_name} to episode {episodes}"
                    if new_status == 'completed':
                        message += " (Completed)"
                    
                    self.root.after(0, lambda: self._set_status(message))
                    
                    # Update cache directly and reload from cache
                    if self.current_user:
                        anime_id = anime_entry['id']
                        update_data = {'episodes': episodes}
                        if new_status:
                            update_data['status'] = new_status
                        
                        # Update cache and reload
                        self._update_cache_and_reload(anime_id, update_data)
                else:
                    self.root.after(0, lambda: self._set_status(f"Failed to update {anime_name}"))
                    # Reset to previous value
                    prev_episodes = anime_entry.get('episodes', 0)
                    self.root.after(0, lambda: self.compact_episode_var.set(str(prev_episodes)))
                    
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error updating progress: {str(e)}"))
        
        threading.Thread(target=update_data, daemon=True).start()
    
    def _update_score(self, score: int):
        """Update anime score on Shikimori"""
        if not self.selected_anime:
            return
        
        def update_data():
            try:
                rate_id = self.selected_anime['id']
                anime_name = self.selected_anime['anime'].get('name', 'Unknown')
                
                success = self.shikimori.update_anime_progress(
                    rate_id, episodes=self.selected_anime.get('episodes', 0), score=score)
                
                if success:
                    if score > 0:
                        self.root.after(0, lambda: self._set_status(f"Set {anime_name} score to {score}"))
                    else:
                        self.root.after(0, lambda: self._set_status(f"Removed score for {anime_name}"))
                    
                    # Update cache directly and reload from cache
                    if self.current_user:
                        anime_id = self.selected_anime['id']
                        self._update_cache_and_reload(anime_id, {'score': score})
                else:
                    self.root.after(0, lambda: self._set_status(f"Failed to update {anime_name} score"))
                    # Reset to previous value
                    prev_score = self.selected_anime.get('score', 0)
                    if prev_score > 0:
                        self.root.after(0, lambda: self.compact_score_var.set(str(prev_score)))
                    else:
                        self.root.after(0, lambda: self.compact_score_var.set("-"))
                    
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error updating score: {str(e)}"))
        
        threading.Thread(target=update_data, daemon=True).start()
    
    def _set_compact_controls_enabled(self, enabled: bool):
        """Enable or disable the compact anime controls"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.compact_episode_entry.config(state=state)
        self.compact_status_combo.config(state="readonly" if enabled else tk.DISABLED)
        self.compact_score_combo.config(state="readonly" if enabled else tk.DISABLED)
    
    def _on_compact_episode_focus_in(self, event=None):
        """Handle when compact episode entry gets focus - record which anime we're editing"""
        if self.selected_anime:
            # Initialize editing attributes if they don't exist
            if not hasattr(self, 'episode_editing_anime'):
                self.episode_editing_anime = None
            if not hasattr(self, 'episode_editing_original_value'):
                self.episode_editing_original_value = None
            
            self.episode_editing_anime = self.selected_anime
            self.episode_editing_original_value = self.compact_episode_var.get()
    
    def _on_compact_episode_key_press(self, event=None):
        """Handle key press in compact episode entry - mark that we're editing"""
        if self.selected_anime:
            # Initialize editing attributes if they don't exist
            if not hasattr(self, 'episode_editing_anime'):
                self.episode_editing_anime = None
            
            self.episode_editing_anime = self.selected_anime
    
    def _on_compact_episode_entry(self, event=None):
        """Handle manual episode entry in compact panel"""
        # Use the anime we started editing, not the currently selected one
        target_anime = self.episode_editing_anime if self.episode_editing_anime else self.selected_anime
        
        if not target_anime:
            return
        
        try:
            new_value = int(self.compact_episode_var.get())
            total = target_anime['anime'].get('episodes', 9999)
            new_value = max(0, min(total if total else 9999, new_value))
            
            # Only update if the value actually changed
            current = target_anime.get('episodes', 0)
            if new_value != current:
                self.compact_episode_var.set(str(new_value))
                self._update_progress_for_anime(target_anime, new_value)
            
            # Clear editing state
            if hasattr(self, 'episode_editing_anime'):
                self.episode_editing_anime = None
            if hasattr(self, 'episode_editing_original_value'):
                self.episode_editing_original_value = None
            
        except ValueError:
            # Reset to original value if invalid
            if self.episode_editing_original_value is not None:
                self.compact_episode_var.set(self.episode_editing_original_value)
            else:
                current = target_anime.get('episodes', 0)
                self.compact_episode_var.set(str(current))
            
            # Clear editing state
            if hasattr(self, 'episode_editing_anime'):
                self.episode_editing_anime = None
            if hasattr(self, 'episode_editing_original_value'):
                self.episode_editing_original_value = None
    
    def _on_compact_score_changed(self, event=None):
        """Handle score change in compact panel"""
        if not self.selected_anime:
            return
        
        score_text = self.compact_score_var.get()
        if score_text == "-":
            score = 0
        else:
            try:
                score = int(score_text)
            except ValueError:
                return
        
        self._update_score(score)
    
    def _on_compact_status_changed(self, event=None):
        """Handle status change in compact panel"""
        if not self.selected_anime:
            return
        
        status_text = self.compact_status_var.get()
        if status_text == "-":
            return
        
        # Convert status display back to API key
        status_map = {v: k for k, v in self.shikimori.STATUSES.items()}
        new_status = status_map.get(status_text)
        
        if new_status:
            self._update_status(new_status)
    
    def _update_status(self, status: str):
        """Update anime status on Shikimori"""
        if not self.selected_anime:
            return
        
        def update_data():
            try:
                rate_id = self.selected_anime['id']
                anime_name = self.selected_anime['anime'].get('name', 'Unknown')
                
                # Special handling for Rewatching status
                episodes_to_update = self.selected_anime.get('episodes', 0)
                if status == 'rewatching':
                    episodes_to_update = 0  # Set episodes to 0 when changing to Rewatching
                
                success = self.shikimori.update_anime_progress(
                    rate_id, episodes=episodes_to_update, status=status)
                
                if success:
                    status_display = self.shikimori.STATUSES.get(status, status)
                    message = f"Changed {anime_name} status to {status_display}"
                    if status == 'rewatching':
                        message += " (episodes reset to 0)"
                    self.root.after(0, lambda: self._set_status(message))
                    
                    # Update cache directly and reload from cache
                    if self.current_user:
                        anime_id = self.selected_anime['id']
                        update_data = {'status': status}
                        if status == 'rewatching':
                            update_data['episodes'] = 0
                        self._update_cache_and_reload(anime_id, update_data)
                else:
                    self.root.after(0, lambda: self._set_status(f"Failed to update {anime_name} status"))
                    # Reset to previous value
                    prev_status = self.selected_anime.get('status', '')
                    if prev_status in self.shikimori.STATUSES:
                        prev_status_display = self.shikimori.STATUSES[prev_status]
                        self.root.after(0, lambda: self.compact_status_var.set(prev_status_display))
                    else:
                        self.root.after(0, lambda: self.compact_status_var.set("-"))
                    
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Error updating status: {str(e)}"))
        
        threading.Thread(target=update_data, daemon=True).start()
    
    def _add_anime_cache_and_reload(self, anime_entry: Dict[str, Any]):
        """Add anime to cache and reload from cache to reflect changes"""
        def add_and_reload():
            if self.current_user:
                user_id = self.current_user['id']
                # Add the anime to cache
                cache_updated = self.cache_manager.add_anime_to_cache(user_id, anime_entry)
                
                if cache_updated:
                    # Reload from updated cache
                    self.root.after(0, self._reload_from_cache)
                else:
                    # Fallback to full refresh if cache update failed
                    self.root.after(0, lambda: self._refresh_list(force_refresh=True))
        
        threading.Thread(target=add_and_reload, daemon=True).start()
    
    def _update_cache_and_reload(self, anime_id: int, updates: Dict[str, Any]):
        """Update cache directly and reload from cache to reflect changes"""
        def update_and_reload():
            if self.current_user:
                user_id = self.current_user['id']
                # Update the cache file directly
                cache_updated = self.cache_manager.update_anime_in_cache(user_id, anime_id, updates)
                
                if cache_updated:
                    # Reload from updated cache
                    self.root.after(0, self._reload_from_cache)
                else:
                    # Fallback to full refresh if cache update failed
                    self.root.after(0, lambda: self._refresh_list(force_refresh=True))
        
        threading.Thread(target=update_and_reload, daemon=True).start()
    
    def _setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not TRAY_AVAILABLE:
            print("System tray not available - skipping setup")
            return
        
        try:
            # Create a more visible icon with better contrast
            image = Image.new('RGBA', (32, 32), (0, 0, 0, 0))  # Transparent background
            draw = ImageDraw.Draw(image)
            
            # Draw a blue circle background
            draw.ellipse([2, 2, 30, 30], fill='#0078D4', outline='#005A9E', width=2)
            
            # Draw the letter 'S' in white
            try:
                # Try to use a built-in font
                from PIL import ImageFont
                font = ImageFont.load_default()
                # Calculate text position to center it
                bbox = draw.textbbox((0, 0), 'S', font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (32 - text_width) // 2
                y = (32 - text_height) // 2 - 2
                draw.text((x, y), 'S', fill='white', font=font)
            except:
                # Fallback to simple text without font
                draw.text((10, 8), 'S', fill='white')
            
            # Create tray menu
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", self._show_from_tray, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Start/Stop Monitoring", self._toggle_monitoring_from_tray),
                pystray.MenuItem("Refresh List", self._refresh_from_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._exit_from_tray)
            )
            
            # Create tray icon with double-click handler
            self.tray_icon = pystray.Icon(
                "Shikimori Updater",
                image,
                "Shikimori Updater - Double-click to show",
                menu
            )
            
            # Set double-click action to show window
            self.tray_icon.default_action = self._show_from_tray
            
            print("System tray icon created successfully")
            
        except Exception as e:
            print(f"Failed to setup system tray: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_minimize(self, event):
        """Handle window minimize event"""
        if (event.widget == self.root and 
            self.config.get('ui.minimize_to_tray', False) and 
            TRAY_AVAILABLE):
            
            # Use a delay to ensure the window state has changed
            self.root.after(100, self._check_and_hide_to_tray)
    
    def _on_restore(self, event):
        """Handle window restore event"""
        if event.widget == self.root:
            self.window_minimized = False
    
    def _check_and_hide_to_tray(self):
        """Check if window is iconified and hide to tray if needed"""
        if self.root.state() == 'iconic' and TRAY_AVAILABLE:
            self._hide_to_tray()
    
    def _hide_to_tray(self):
        """Hide window to system tray"""
        if not TRAY_AVAILABLE:
            print("Cannot hide to tray - functionality not available")
            return
        
        if not self.tray_icon:
            print("Cannot hide to tray - tray icon not initialized")
            return
        
        try:
            self.root.withdraw()
            self.window_minimized = True
            
            if not hasattr(self.tray_icon, '_running') or not self.tray_icon._running:
                # Start tray icon in a separate thread
                self.tray_icon._running = True
                print("Starting system tray icon...")
                
                def run_tray():
                    try:
                        self.tray_icon.run()
                    except Exception as e:
                        print(f"Error running tray icon: {e}")
                
                threading.Thread(target=run_tray, daemon=True).start()
            else:
                print("Tray icon already running")
            
        except Exception as e:
            print(f"Error hiding to tray: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_from_tray(self, icon=None, item=None):
        """Show window from system tray"""
        print("Show from tray called")
        self.root.after(0, self._restore_window)
    
    def _restore_window(self):
        """Restore window from tray"""
        print("Restoring window from tray")
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.window_minimized = False
            print("Window restored successfully")
        except Exception as e:
            print(f"Error restoring window: {e}")
    
    def _toggle_monitoring_from_tray(self, icon=None, item=None):
        """Toggle monitoring from tray menu"""
        self.root.after(0, self._toggle_monitoring)
    
    def _refresh_from_tray(self, icon=None, item=None):
        """Refresh anime list from tray menu"""
        self.root.after(0, lambda: self._refresh_list(force_refresh=True))
    
    def _exit_from_tray(self, icon=None, item=None):
        """Exit application from tray menu"""
        print("Exit from tray called")
        # Stop the tray icon first
        if self.tray_icon and hasattr(self.tray_icon, 'stop'):
            try:
                self.tray_icon.stop()
            except:
                pass
        self.root.after(0, self._actually_close)
    
    def _clear_cache(self):
        """Clear anime list cache"""
        if not self.current_user:
            messagebox.showwarning("Warning", "Please login first")
            return
        
        if messagebox.askyesno("Clear Cache", "Are you sure you want to clear the anime list cache?"):
            self.cache_manager.clear_cache(self.current_user['id'])
            self._set_status("Cache cleared")
    
    def _refresh_synonyms(self):
        """Force refresh synonym cache for better anime matching"""
        if not self.current_user or not self.anime_list_data:
            messagebox.showwarning("Warning", "Please login and load anime list first")
            return
        
        if messagebox.askyesno("Refresh Synonyms", 
                              "This will re-download detailed anime info including synonyms for better matching.\n\n"
                              "This may take a few minutes. Continue?"):
            self.anime_matcher.force_refresh_synonyms(self.current_user['id'], self.anime_list_data)
            self._set_status("Refreshing synonyms in background...")
    
    def _show_options(self):
        """Show options dialog"""
        options_dialog = OptionsDialog(self.root, self.config)
        self.root.wait_window(options_dialog.dialog)
        
        if options_dialog.changes_made:
            # Update player monitor with new settings
            self.player_monitor.min_watch_time = self.config.get('monitoring.min_watch_time', 60)
            
            # Check if auto-start monitoring is enabled and we're logged in
            if self.config.get('monitoring.auto_start', False) and self.config.is_authenticated and not self.monitoring_active:
                self._toggle_monitoring()
    
    def _update_single_anime(self, anime_entry: Dict[str, Any]):
        """Update a single anime entry in the local data and refresh only that item"""
        if not anime_entry:
            return
        
        # Find and update the anime in local data
        found = False
        old_status_key = None
        
        for status_key, anime_list in self.anime_list_data.items():
            for i, entry in enumerate(anime_list):
                if entry.get('id') == anime_entry.get('id'):
                    old_status_key = status_key
                    new_status = anime_entry.get('status', '')
                    
                    # If status changed, we need to move the anime
                    if new_status != status_key and new_status in self.anime_list_data:
                        # Remove from old list
                        self.anime_list_data[status_key].pop(i)
                        # Add to new list  
                        self.anime_list_data[new_status].append(anime_entry)
                    else:
                        # Just update in place
                        self.anime_list_data[status_key][i] = anime_entry
                    
                    found = True
                    break
            
            if found:
                break
        
        if found:
            # Update the UI display efficiently - only refresh the tree view
            self.anime_list_frame.update_list(self.anime_list_data)
            # Update the selected anime in the info panel if it's the same one
            if self.selected_anime and self.selected_anime.get('id') == anime_entry.get('id'):
                self.set_selected_anime(anime_entry)
            # Update the item_data in anime_list_frame to maintain consistency
            self.anime_list_frame._sync_item_data_with_updated_entry(anime_entry)
        else:
            # If not found, do a full refresh as fallback
            self._refresh_list()
