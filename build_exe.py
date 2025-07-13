#!/usr/bin/env python3
"""
Build script for creating a self-contained executable of the Map to VMF Converter.
This script uses PyInstaller to package the application into a standalone executable.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building Map to VMF Converter executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # Don't show console window on Windows
        "--name=Map2VMF_Converter",     # Name of the executable
        "--icon=icon.ico",              # Icon file (if exists)
        "--add-data=README.md;.",       # Include README in the package
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.QtWidgets",
        "map2vmf.py"
    ]
    
    # Remove icon option if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build executable: {e}")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist."""
    if os.path.exists("icon.ico"):
        print("✓ Icon file already exists")
        return
    
    print("Creating simple icon file...")
    try:
        # Create a simple .ico file using PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 256x256 image
            img = Image.new('RGBA', (256, 256), (70, 130, 180, 255))  # Steel blue background
            draw = ImageDraw.Draw(img)
            
            # Draw a simple "M" for Map
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            draw.text((128, 128), "map2vmf", fill=(255, 255, 255, 255), font=font, anchor="mm")
            
            # Save as ICO
            img.save("icon.ico", format='ICO')
            print("✓ Icon file created")
        except ImportError:
            print("PIL not available, skipping icon creation")
    except Exception as e:
        print(f"Could not create icon: {e}")

def cleanup():
    """Clean up build artifacts."""
    print("Cleaning up build artifacts...")
    
    # Remove build directory
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("✓ Removed build directory")
    
    # Remove spec file
    if os.path.exists("Map2VMF_Converter.spec"):
        os.remove("Map2VMF_Converter.spec")
        print("✓ Removed spec file")

def main():
    """Main build process."""
    print("=== Map to VMF Converter - Build Script ===")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("map2vmf.py"):
        print("✗ Error: map2vmf.py not found in current directory")
        print("Please run this script from the project root directory")
        return False
    
    # Check and install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Create icon if needed
    create_icon()
    
    # Build the executable
    if not build_executable():
        return False
    
    # Clean up
    cleanup()
    
    print()
    print("=== Build Complete ===")
    print("✓ Executable created: dist/Map2VMF_Converter.exe")
    print()
    print("The executable is now ready to use!")
    print("- It's completely self-contained (no Python installation needed)")
    print("- It includes all necessary dependencies")
    print("- It can be distributed to other computers")
    print()
    print("To run the executable:")
    print("  Windows: Double-click Map2VMF_Converter.exe")
    print("  Linux/Mac: ./Map2VMF_Converter")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 