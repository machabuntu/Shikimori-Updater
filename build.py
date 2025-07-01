#!/usr/bin/env python3
"""
Build script for creating Shikimori Updater executable
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is available")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Use spec file if it exists, otherwise use command line
    spec_files = ["Shikimori Updater.spec", "shikimori_updater.spec"]
    spec_file = None
    for spec in spec_files:
        if os.path.exists(spec):
            spec_file = spec
            break
    
    if spec_file:
        print(f"Using spec file for build: {spec_file}")
        cmd = [
            "pyinstaller",
            "--clean",     # Clean PyInstaller cache
            "--noconfirm", # Overwrite output directory
            spec_file
        ]
    else:
        print("Using command line build...")
        # PyInstaller command
        cmd = [
            "pyinstaller",
            "--name", "Shikimori Updater",
            "--windowed",  # No console window
            "--onefile",   # Single executable file
            "--clean",     # Clean PyInstaller cache
            "--noconfirm", # Overwrite output directory
            "--add-data", "src;src",  # Include src directory
            "main.py"
        ]
        
        # Add icon if it exists
        if os.path.exists("icon.ico"):
            cmd.extend(["--icon", "icon.ico"])
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def copy_files():
    """Copy additional files to dist folder"""
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        print("✗ Dist directory not found")
        return False
    
    files_to_copy = [
        "README.md",
        "requirements.txt"
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            try:
                shutil.copy2(file, dist_dir)
                print(f"✓ Copied {file}")
            except Exception as e:
                print(f"! Could not copy {file}: {e}")
    
    return True

def main():
    """Main build function"""
    print("Shikimori Updater Build Script")
    print("=" * 40)
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("\nBuild failed. Please install PyInstaller manually:")
        print("pip install pyinstaller")
        return False
    
    # Build executable
    if not build_executable():
        print("\nBuild failed. Check the output above for errors.")
        return False
    
    # Copy additional files
    copy_files()
    
    print("\n" + "=" * 40)
    print("✓ Build completed successfully!")
    
    exe_path = os.path.join("dist", "Shikimori Updater.exe")
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"\nExecutable created: {exe_path}")
        print(f"Size: {size:.1f} MB")
        print("\nYou can now distribute the 'dist' folder")
        print("or just the executable file.")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error during build: {e}")
        print("Please check the requirements and try again.")
