# Troubleshooting Guide

## Build Issues

### Problem: `ModuleNotFoundError: No module named 'gui'`
**Solution**: This indicates PyInstaller isn't including the source files properly.
- Run: `python build.py` (uses the updated spec file with correct data inclusion)
- Make sure the `src` directory exists and contains all Python files

### Problem: `ImportError: cannot import name 'simpledialog' from 'tkinter'`
**Solution**: Missing tkinter submodules in PyInstaller.
- The updated spec file now includes all required tkinter modules
- This is fixed in the current build configuration

### Problem: `PyInstaller not found`
**Solution**: 
```bash
pip install pyinstaller
```

### Problem: Build fails with permission errors
**Solution**:
- Close any running instances of the application
- Run build script as administrator if needed
- Delete build and dist folders manually if they exist

## Runtime Issues

### Problem: Application doesn't start
**Solution**:
1. Check if all dependencies are installed: `pip install -r requirements.txt`
2. Try running from source first: `python main.py`
3. Check Windows Defender/Antivirus - they sometimes block new executables

### Problem: Authentication fails
**Solution**:
1. Verify Client ID and Client Secret are correct
2. Ensure redirect URI is exactly: `http://localhost:8080/callback`
3. Check that scope includes `user_rates`
4. Try clearing config: Delete `~/.shikimori_updater/config.json`

### Problem: PotPlayer monitoring doesn't work
**Solution**:
1. Make sure PotPlayer is actually running when you start monitoring
2. Check that anime files follow standard naming conventions:
   - `[Group] Anime Name - Episode [Quality]`
   - `Anime Name - Episode`
   - `Anime Name Episode Number`
3. Verify the anime is in your Shikimori list
4. Check that the detected episode number is +1 from current progress

### Problem: Anime not found/matched
**Solution**:
1. Check anime naming in the file matches Shikimori database
2. Add the anime to your list manually first
3. Use the Search & Add feature to find the correct anime
4. Check for typos in anime names

## Development Issues

### Problem: Import errors when running from source
**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_imports.py
```

### Problem: Missing dependencies during development
**Solution**:
Install additional packages as needed:
```bash
pip install requests psutil python-dotenv Pillow
```

## Quick Fixes

### Reset Configuration
Delete the config file:
- Windows: `%USERPROFILE%\.shikimori_updater\config.json`

### Clean Build
```bash
# Remove old build files
rmdir /s build dist
del "*.spec"

# Rebuild
python build.py
```

### Test Build
```bash
# Test imports work
python test_imports.py

# Test executable
python test_exe.py
```

### Manual Build
If the build script fails:
```bash
pip install pyinstaller
pyinstaller "Shikimori Updater.spec"
```

## Common Error Messages

### `[WinError 5] Access is denied`
- Close the application if it's running
- Run command prompt as administrator
- Check antivirus isn't blocking the operation

### `ModuleNotFoundError: No module named 'requests'`
- Install missing dependency: `pip install requests`
- Or install all dependencies: `pip install -r requirements.txt`

### `Failed to get user information`
- Check internet connection
- Verify Shikimori is accessible
- Check if tokens have expired (will auto-refresh)

### `No match found for [anime name]`
- Add anime to your Shikimori list first
- Check anime name matches exactly
- Try different naming patterns

## Getting Help

If you encounter an issue not covered here:

1. **Check the logs**: Look in the application directory for any log files
2. **Test with source**: Try running `python main.py` instead of the executable
3. **Verify environment**: Run `python test_imports.py` to check all modules load
4. **Clean install**: Delete config and rebuild from scratch

## Report Issues

When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Error message (full traceback)
- Steps to reproduce
- Whether it works from source vs executable
