#!/usr/bin/env python3
"""
Test script for GUI autoclicker
"""

import sys
import platform

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import tkinter
        print("✓ tkinter available")
    except ImportError as e:
        print(f"✗ tkinter not available: {e}")
        return False
    
    try:
        import pynput
        print("✓ pynput available")
    except ImportError as e:
        print(f"✗ pynput not available: {e}")
        return False
    
    try:
        import pyautogui
        print("✓ pyautogui available")
    except ImportError as e:
        print(f"✗ pyautogui not available: {e}")
        return False
    
    return True

def test_gui_creation():
    """Test if GUI can be created."""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from autoclicker_gui import AutoclickerGUI
        
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        app = AutoclickerGUI(root)
        print("✓ GUI created successfully")
        
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ GUI creation failed: {e}")
        return False

def main():
    """Main test function."""
    print("=== GUI Autoclicker Test ===")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print()
    
    if not test_imports():
        print("\n❌ Import test failed - install missing dependencies")
        return False
    
    if not test_gui_creation():
        print("\n❌ GUI creation test failed")
        return False
    
    print("\n✅ All tests passed! GUI should work correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
