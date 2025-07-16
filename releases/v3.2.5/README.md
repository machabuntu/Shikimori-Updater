# Shikimori Updater

**A powerful, modern GUI application for automatically tracking anime episodes and managing your Shikimori list with intelligent scrobbling, smart status management, and comprehensive Telegram notifications.**

![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🌟 Key Features

### 🎯 **Intelligent Anime Management**
- **Modern Tab-based Interface** - Separate tabs for Watching, Completed, Plan to Watch, On Hold, Dropped, and Rewatching
- **Smart Status Transitions** - Automatically moves anime from "Plan to Watch" to "Watching" when progress increases
- **Dual List Support** - Full anime and manga list management with dedicated interfaces
- **Dynamic Progress Tracking** - Real-time episode/chapter counters with instant UI updates
- **Enhanced Search & Add** - Find and add anime/manga with duplicate detection and smart filtering

### 🤖 **Automatic Scrobbling System**
- **Media Player Integration** - Monitors PotPlayer (all variants) for opened video files
- **Smart Episode Detection** - Advanced regex-based parsing of anime names and episode numbers
- **Intelligent Matching** - Uses synonyms, alternative titles, and fuzzy matching with 85%+ accuracy
- **Progress Validation** - Only updates if detected episode is exactly +1 from current progress
- **Auto-completion** - Automatically marks anime as completed when final episode is watched

### 📊 **Advanced Status Management**
- **Rewatching Support** - Auto-resets episodes to 0 and tracks rewatch count
- **Score-based Completion** - Auto-completes anime when max episodes reached and score is set
- **Status Change Tracking** - Comprehensive logging of all status transitions
- **Manual Override** - Full manual control over episodes, scores, and status

### 🔔 **Telegram Integration**
- **Progress Notifications** - Real-time updates when episodes are watched
- **Completion Alerts** - Notifications when anime/manga are completed
- **Status Change Updates** - Alerts for drops, rewatching, and other status changes
- **Rich Formatting** - HTML-formatted messages with clickable anime links
- **Granular Control** - Individual toggles for different notification types

### ⚡ **Performance & Caching**
- **Intelligent Caching** - Local cache system for instant startup and reduced API calls
- **Synonym Database** - Enhanced matching using comprehensive title databases
- **Efficient Updates** - Cache-based updates instead of full API refreshes
- **Background Syncing** - Non-blocking API operations for smooth user experience

### 🎨 **Modern UI/UX**
- **Dark/Light Themes** - Toggle between modern dark and light interfaces
- **System Tray Support** - Minimize to tray with full control menu
- **Compact Controls** - Streamlined progress controls in the main toolbar
- **Non-intrusive Feedback** - Status messages instead of blocking dialogs
- **Windows Integration** - Optional startup with Windows and modern styling

## 📋 System Requirements

- **Operating System:** Windows 10/11 (required for PotPlayer integration)
- **Python:** 3.8 or higher
- **Internet:** Active connection for Shikimori API
- **Media Player:** PotPlayer (any variant) for automatic scrobbling
- **Account:** Active Shikimori account

## 🚀 Quick Start

### Option 1: Pre-built Executable (Recommended)

1. **Download** the latest release from GitHub
2. **Extract** the ZIP file to your desired location
3. **Run** `Shikimori Updater.exe`
4. **Follow** the setup wizard for first-time configuration

### Option 2: Run from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ShikimoriUpdater.git
cd ShikimoriUpdater

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Build Your Own Executable

```bash
# Auto-build with included script
python build.py

# Or build manually
pip install pyinstaller
pyinstaller "Shikimori Updater.spec"
```

## ⚙️ Initial Setup

### 1. Create Shikimori API Application

1. Visit [Shikimori OAuth Applications](https://shikimori.one/oauth/applications)
2. Click **"New Application"**
3. Configure your application:
   - **Name:** `Shikimori Updater` (or your preferred name)
   - **Redirect URI:** `http://localhost:8080/callback`
   - **Scopes:** `user_rates` (required for list management)
4. **Save** and copy your `Client ID` and `Client Secret`

### 2. First-Time Authentication

1. **Launch** Shikimori Updater
2. **Click** "Menu" → "Authentication..."
3. **Enter** your Client ID and Client Secret
4. **Click** "Start Authorization" (opens browser)
5. **Authorize** the application on Shikimori
6. **Copy** the authorization code from the redirect URL
7. **Paste** the code and click "Complete Authorization"
8. **Save** your credentials

### 3. Optional: Configure Telegram Notifications

1. **Create** a Telegram bot via [@BotFather](https://t.me/botfather)
2. **Get** your bot token and chat/channel ID
3. **Open** Menu → Options → Notifications tab
4. **Enable** Telegram notifications and enter your credentials
5. **Choose** which events to receive notifications for

## 📖 Usage Guide

### Anime & Manga List Management

- **View Lists:** Switch between "Anime List" and "Manga List" tabs
- **Filter by Status:** Use status tabs (Watching, Completed, etc.)
- **Search:** Use the search box to find specific titles
- **Quick Edit:** Use compact controls in the toolbar for selected anime
- **Bulk Operations:** Right-click for context menus and batch actions

### Automatic Scrobbling

1. **Enable Monitoring:** Menu → "Start/Stop Scrobbling"
2. **Open Videos:** Play anime episodes in PotPlayer
3. **Watch:** After 1+ minutes of viewing, progress updates automatically
4. **Verification:** Only episodes that are +1 from current progress are counted
5. **Completion:** Anime auto-completes when final episode is watched (if scored)

### Adding New Content

1. **Search Tab:** Use "Search & Add" to find new anime/manga
2. **Select Status:** Choose which list to add content to
3. **Quick Add:** Double-click entries for instant addition
4. **Smart Filtering:** Already-owned content is automatically hidden

### Manual Progress Control

- **Episode/Chapter Controls:** Use +/- buttons or direct entry
- **Score Management:** Select scores from dropdown (1-10 or remove)
- **Status Changes:** Use status dropdown for manual transitions
- **Batch Updates:** Select multiple items for bulk operations

## 📁 Project Structure

```
ShikimoriUpdater/
├── main.py                          # Application entry point
├── build.py                         # Automated build script
├── setup.py                         # Installation helper
├── requirements.txt                 # Python dependencies
├── Shikimori Updater.spec          # PyInstaller configuration
│
├── src/
│   ├── core/
│   │   ├── config.py               # Configuration management
│   │   └── cache.py                # Intelligent caching system
│   │
│   ├── api/
│   │   └── shikimori_client.py     # Shikimori API integration
│   │
│   ├── gui/
│   │   ├── main_window.py          # Main application window
│   │   ├── anime_list_frame.py     # Anime list interface
│   │   ├── manga_list_frame.py     # Manga list interface
│   │   ├── search_frame.py         # Search and add functionality
│   │   ├── options_dialog.py       # Settings configuration
│   │   ├── auth_dialog.py          # Authentication dialogs
│   │   └── modern_style.py         # UI theming system
│   │
│   └── utils/
│       ├── player_monitor.py       # Media player detection
│       ├── anime_matcher.py        # Basic name matching
│       ├── enhanced_anime_matcher.py # Advanced synonym matching
│       ├── telegram_notifier.py    # Telegram integration
│       ├── notification_manager.py # Notification system
│       └── logger.py               # Logging framework
```

## 🔧 Configuration

### Configuration Files
- **Main Config:** `~/.shikimori_updater/config.json`
- **Cache Location:** `%LOCALAPPDATA%/ShikimoriUpdater/cache/`
- **Logs:** Application logs are stored in the cache directory

### Key Settings
```json
{
  "monitoring": {
    "auto_start": false,
    "min_watch_time": 60,
    "supported_players": ["PotPlayer64.exe", "PotPlayer.exe", "PotPlayerMini64.exe", "PotPlayerMini.exe"]
  },
  "ui": {
    "dark_theme": false,
    "minimize_to_tray": false,
    "close_to_tray": false
  },
  "telegram": {
    "enabled": false,
    "send_progress": false,
    "send_completed": true,
    "send_dropped": false,
    "send_rewatching": false
  }
}
```

## 🎯 Supported Media Players

- **PotPlayer** (64-bit and 32-bit)
- **PotPlayerMini** (64-bit and 32-bit)

*Note: Additional players can be added by modifying the configuration.*

## 🔍 Troubleshooting

### Common Issues

**Authentication Problems:**
- Verify Client ID and Client Secret are correct
- Ensure redirect URI is exactly `http://localhost:8080/callback`
- Check that `user_rates` scope is granted

**Scrobbling Not Working:**
- Confirm PotPlayer is running and supported
- Check that anime files use standard naming conventions
- Verify the anime exists in your Shikimori list
- Ensure Windows process access permissions

**Episode Detection Issues:**
- Use standard naming: `[Group] Anime Name - Episode ## [Quality]`
- Avoid special characters in episode numbers
- Check that episode number is +1 from current progress

**Performance Issues:**
- Clear cache: Menu → "Clear Cache"
- Refresh synonyms: Menu → "Refresh Synonyms"
- Check internet connection stability

### Debug Information
- **Logs:** Menu → "View Logs" for detailed error information
- **Version:** Check title bar for current version
- **Cache Status:** Monitor status bar for cache operations

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/yourusername/ShikimoriUpdater.git
cd ShikimoriUpdater
pip install -r requirements.txt

# Run in development mode
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Shikimori](https://shikimori.one)** - Excellent anime database and API
- **[PotPlayer](https://potplayer.daum.net)** - Fantastic media player for anime
- **The Anime Community** - Inspiration and feedback
- **Contributors** - Everyone who helped improve this project

## 📞 Support

Need help? Here's how to get support:

1. **Check** the troubleshooting section above
2. **Review** application logs (Menu → "View Logs")
3. **Search** existing GitHub issues
4. **Create** a new issue with:
   - Detailed error description
   - Steps to reproduce
   - System information (Windows version, Python version)
   - Relevant log excerpts (remove sensitive data)

## 🚀 Changelog

### v3.0.0 (Latest)
- ✨ **Smart Status Transitions** - Auto-move from "Plan to Watch" to "Watching"
- 📱 **Telegram Integration** - Rich notifications with granular controls
- 📚 **Manga Support** - Full manga list management with chapter/volume tracking
- 🎨 **Enhanced UI** - Modern dark/light themes with improved layouts
- ⚡ **Performance Boost** - Optimized caching and background operations
- 🔍 **Advanced Matching** - Synonym support for better anime detection
- 🔧 **System Integration** - Tray support, startup options, and Windows integration

### v2.0.0
- 🏗️ **Complete Rewrite** - Modern architecture with improved reliability
- 📑 **Tab-based Interface** - Organized status management
- 💾 **Smart Caching** - Intelligent local data management
- 🔄 **Rewatching Support** - Comprehensive rewatch tracking
- 🎯 **Enhanced Accuracy** - Improved episode detection algorithms

### v1.0.0
- 🎉 **Initial Release** - Core functionality implementation
- 🔐 **OAuth Integration** - Secure Shikimori authentication
- 📺 **Basic Scrobbling** - PotPlayer integration
- 📋 **List Management** - Basic anime list operations
