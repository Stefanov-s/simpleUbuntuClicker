#!/usr/bin/env python3
"""
Autoclicker Launcher
Detects platform and runs the appropriate version (GUI or terminal).
"""

import sys
import platform
import subprocess
import os

def main():
    """Main launcher function."""
    system = platform.system().lower()
    
    print("=== Simple Autoclicker Launcher ===")
    print(f"Platform: {system.title()}")
    print()
    
    # Check if GUI is available
    try:
        import tkinter
        gui_available = True
        print("✓ GUI (tkinter) available")
    except ImportError:
        gui_available = False
        print("✗ GUI (tkinter) not available")
    
    # Check if terminal version is available
    terminal_available = os.path.exists("autoclicker.py")
    if terminal_available:
        print("✓ Terminal version available")
    else:
        print("✗ Terminal version not found")
    
    print()
    
    # Choose version to run
    if gui_available:
        print("Starting GUI version...")
        try:
            from autoclicker_gui import main as gui_main
            gui_main()
        except Exception as e:
            print(f"Error starting GUI: {e}")
            if terminal_available:
                print("Falling back to terminal version...")
                subprocess.run([sys.executable, "autoclicker.py"])
    elif terminal_available:
        print("Starting terminal version...")
        subprocess.run([sys.executable, "autoclicker.py"])
    else:
        print("Error: No autoclicker version available!")
        sys.exit(1)

if __name__ == "__main__":
    main()
