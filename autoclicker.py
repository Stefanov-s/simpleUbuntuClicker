#!/usr/bin/env python3
"""
Simple Autoclicker for Ubuntu
A terminal-based autoclicker with primary and optional secondary clickers.
Uses F1 to toggle primary clicker and F2 to toggle secondary clicker.
"""

import time
import threading
from pynput import keyboard
import pyautogui

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# Global variables
first_clicker_active = False
second_clicker_active = False
start_time = None
mouse_x, mouse_y = 0, 0
primary_interval = 0
secondary_interval = None

def get_user_input():
    """Collect user input for intervals and secondary clicker preference."""
    global primary_interval, secondary_interval
    
    print("=== Simple Autoclicker for Ubuntu ===")
    print("Press F1 to toggle primary clicker, F2 to toggle secondary clicker")
    print("Move mouse to top-left corner to stop the application")
    print()
    
    # Get primary clicker interval
    while True:
        try:
            minutes = int(input("Enter minutes for primary clicker: "))
            seconds = int(input("Enter seconds for primary clicker: "))
            if minutes < 0 or seconds < 0:
                print("Please enter non-negative numbers.")
                continue
            primary_interval = minutes * 60 + seconds
            if primary_interval == 0:
                print("Interval must be greater than 0.")
                continue
            break
        except ValueError:
            print("Please enter valid numbers.")
    
    # Ask about secondary clicker
    while True:
        choice = input("Enable secondary clicker? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            while True:
                try:
                    minutes = int(input("Enter minutes for secondary clicker: "))
                    seconds = int(input("Enter seconds for secondary clicker: "))
                    if minutes < 0 or seconds < 0:
                        print("Please enter non-negative numbers.")
                        continue
                    secondary_interval = minutes * 60 + seconds
                    if secondary_interval == 0:
                        print("Interval must be greater than 0.")
                        continue
                    break
                except ValueError:
                    print("Please enter valid numbers.")
            break
        elif choice in ['n', 'no']:
            secondary_interval = None
            break
        else:
            print("Please enter 'y' or 'n'.")

def click_thread(interval, active_flag_ref, clicker_name):
    """Thread function for autoclicker."""
    last_click_time = 0
    while True:
        if active_flag_ref[0] and start_time is not None:
            current_time = time.time()
            elapsed = current_time - start_time
            # Only click if enough time has passed since last click
            if elapsed % interval < 0.1 and elapsed - last_click_time >= interval * 0.9:
                pyautogui.click(mouse_x, mouse_y)
                last_click_time = elapsed
                print(f"{clicker_name} click at {elapsed:.1f}s")
        time.sleep(0.01)

def on_key_press(key):
    """Handle key press events."""
    global first_clicker_active, second_clicker_active, start_time
    
    try:
        if key == keyboard.Key.f1:
            first_clicker_active = not first_clicker_active
            if first_clicker_active:
                start_time = time.time()
                print("Primary clicker: ON")
            else:
                print("Primary clicker: OFF")
                
        elif key == keyboard.Key.f2 and secondary_interval is not None:
            second_clicker_active = not second_clicker_active
            if second_clicker_active:
                if start_time is None:
                    start_time = time.time()
                print("Secondary clicker: ON")
            else:
                print("Secondary clicker: OFF")
                
    except AttributeError:
        pass

def main():
    """Main function."""
    global mouse_x, mouse_y, start_time
    
    # Get initial mouse position
    mouse_x, mouse_y = pyautogui.position()
    print(f"Mouse position captured: ({mouse_x}, {mouse_y})")
    
    # Get user input
    get_user_input()
    
    # Create and start threads
    primary_thread = threading.Thread(target=click_thread, 
                                    args=(primary_interval, [first_clicker_active], "Primary"),
                                    daemon=True)
    primary_thread.start()
    
    secondary_thread = None
    if secondary_interval is not None:
        secondary_thread = threading.Thread(target=click_thread,
                                          args=(secondary_interval, [second_clicker_active], "Secondary"),
                                          daemon=True)
        secondary_thread.start()
    
    # Start keyboard listener
    with keyboard.Listener(on_press=on_key_press) as listener:
        print("\nAutoclicker ready! Press F1 to start primary clicker.")
        if secondary_interval is not None:
            print("Press F2 to start secondary clicker.")
        print("Press Ctrl+C to exit.")
        
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nExiting...")
            first_clicker_active = False
            second_clicker_active = False

if __name__ == "__main__":
    main()
