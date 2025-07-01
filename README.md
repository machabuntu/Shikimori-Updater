# Shikimori Updater

A modern GUI application that automatically tracks anime episodes from media players and updates your progress on Shikimori with advanced features and smart caching.

## Features

### Core Features
1. **Shikimori Authentication** - OAuth integration with Shikimori API
2. **Advanced Anime List Management** - Tab-based interface with real-time counters and smart filtering
3. **Efficient Caching System** - Fast loading and updates using local cache with selective refresh
4. **Manual Progress Control** - Update episode progress, scores, and status with instant feedback
5. **Automatic Status Updates** - Smart completion detection and rewatching support
6. **Media Player Monitoring** - Tracks opened videos in PotPlayer and updates progress automatically
7. **Smart Episode Detection** - Only updates progress if the detected episode is +1 from current progress
8. **Enhanced Anime Matching** - Uses synonyms, alternative titles, and fuzzy matching for better detection
9. **Search & Add** - Search for anime and add them to your list with duplicate detection
10. **System Tray Support** - Minimize to tray and control from system tray menu

### New Interface Features
- **Tab-based Status Filter** - Separate tabs for Watching, Completed, Plan to Watch, etc.
- **Dynamic Counters** - Real-time count updates for each status tab with filter support
- **Compact Controls** - Streamlined episode and status controls in the toolbar
- **Smart Filtering** - Hide already-owned anime from search results
- **Status Messages** - Non-intrusive status updates instead of popup dialogs

### Advanced Features
- **Rewatching Support** - Automatically resets episodes to 0 and increments rewatch counter
- **Auto-completion from Rewatching** - Completes anime when final episode is reached while rewatching
- **Efficient Updates** - Cache-based updates instead of full API refreshes
- **Enhanced Synonym Support** - Better anime name matching using comprehensive title database

## Requirements

- Python 3.8 or higher
- Windows (for PotPlayer monitoring)
- Internet connection
- Shikimori account

## Installation

### Option 1: Run from Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ShikimoriUpdater.git
   cd ShikimoriUpdater
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Option 2: Build Executable

1. **Run the build script:**
   ```bash
   python build.py
   ```
   This will automatically install PyInstaller if needed and build the executable.

2. **Alternative manual build:**
   ```bash
   pip install pyinstaller
   pyinstaller shikimori_updater.spec
   ```
   
   The executable will be created in the `dist` folder.

3. **Quick run:**
   ```bash
   # On Windows
   run.bat
   
   # Or directly
   .\dist\"Shikimori Updater.exe"
   ```

## Setup

### 1. Create Shikimori API Application

Before using the application, you need to create a Shikimori API application:

1. Go to [Shikimori OAuth Applications](https://shikimori.one/oauth/applications)
2. Click "New Application"
3. Fill in the form:
   - **Name**: Shikimori Updater (or any name you prefer)
   - **Redirect URI**: `http://localhost:8080/callback`
   - **Scopes**: `user_rates`
4. Save the application
5. Copy the **Client ID** and **Client Secret**

### 2. First Run Authentication

1. Launch the application
2. Click "Login to Shikimori"
3. Enter your Client ID and Client Secret
4. Click "Start Authorization" - this will open your browser
5. Authorize the application on Shikimori
6. Copy the authorization code from the redirect URL
7. Paste it in the application and click "Complete Authorization"
8. Save and close the dialog

## Usage

### Managing Your Anime List

- **View List**: The "Anime List" tab shows all your anime organized by status
- **Filter**: Use the status dropdown and search box to filter anime
- **Edit Anime**: Double-click or right-click to edit anime details
- **Update Progress**: Manually update episode progress
- **Set Scores**: Add or update anime scores
- **Change Status**: Move anime between different status categories

### Adding New Anime

- **Search**: Use the "Search & Add" tab to find new anime
- **Add to List**: Select an anime and choose which status to add it as
- **Bulk Operations**: Double-click to quickly add anime

### Automatic Monitoring

1. **Start Monitoring**: Click "Start Monitoring" in the toolbar
2. **Open Videos**: Open anime episodes in PotPlayer
3. **Automatic Updates**: After watching for 1+ minutes, progress updates automatically
4. **Episode Validation**: Only episodes that are +1 from current progress are counted
5. **Auto-Complete**: Anime automatically moves to "Completed" when finished and scored

## File Structure

```
ShikimoriUpdater/
│
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Configuration management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── shikimori_client.py  # Shikimori API client
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── player_monitor.py    # Media player monitoring
│   │   └── anime_matcher.py     # Anime name matching
│   │
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py       # Main application window
│       ├── auth_dialog.py       # Authentication dialog
│       ├── anime_list_frame.py  # Anime list display
│       └── search_frame.py      # Search and add functionality
```

## Dependencies

- **requests** - HTTP client for API calls
- **psutil** - Process monitoring for media players
- **python-dotenv** - Environment variable management
- **Pillow** - Image processing (if needed for icons)

## Supported Media Players

- PotPlayer (64-bit and 32-bit versions)
- PotPlayerMini (64-bit and 32-bit versions)

## Configuration

The application stores configuration in `~/.shikimori_updater/config.json`:

- API credentials (Client ID/Secret, tokens)
- Window position and size
- Monitoring settings
- Supported player processes

## Troubleshooting

### Authentication Issues
- Make sure Client ID and Client Secret are correct
- Check that redirect URI is exactly `http://localhost:8080/callback`
- Ensure the scope includes `user_rates`

### Monitoring Not Working
- Check that PotPlayer is in the supported players list
- Verify the application has permission to read process information
- Make sure anime files follow standard naming conventions

### Episode Detection Issues
- Use standard anime naming patterns: `[Group] Anime Name - Episode [Quality]`
- Ensure episode numbers are clearly separated from anime names
- Check that the anime is in your Shikimori list

### Build Issues
- Make sure all dependencies are installed
- Use Python 3.8+ for best compatibility
- On Windows, ensure Visual C++ Build Tools are available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Shikimori API for providing anime data
- PotPlayer for being an excellent media player
- The anime community for inspiration

## Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the application logs
3. Create an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - System information
   - Log files (remove sensitive information)

## Changelog

### v2.0.0 (Latest)
- **Tab-based Interface**: Replaced dropdown status filter with dedicated tabs
- **Dynamic Counters**: Real-time anime count for each status with filter support
- **Enhanced Caching**: Efficient cache-based updates for faster performance
- **Rewatching Support**: Auto-reset episodes and rewatch counter management
- **Smart Search**: Hide already-owned anime from search results
- **Status Messages**: Non-intrusive feedback instead of popup dialogs
- **Improved UI Layout**: Compact controls and better organization
- **Enhanced Synonym Support**: Better anime matching with comprehensive title database
- **System Tray Integration**: Minimize to tray with system tray controls
- **Cache Management**: Manual cache clearing and synonym refresh options

### v1.0.0 (Initial Release)
- Complete Shikimori integration
- PotPlayer monitoring
- Full GUI interface
- Automatic progress updates
- Manual anime management
- Search and add functionality
