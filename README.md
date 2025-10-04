# Simple Autoclicker for Ubuntu

A lightweight, terminal-based autoclicker application for Ubuntu that performs mouse clicks at user-defined intervals.

## Features

- **Primary Autoclicker**: Always active when toggled, clicks at a user-specified interval
- **Optional Secondary Autoclicker**: Can be enabled to click at a separate interval
- **Hotkey Control**: F1 toggles primary clicker, F2 toggles secondary clicker
- **Synchronization**: Both clickers start from the same timestamp to prevent drift
- **Consistent Position**: Clicks occur at the mouse position when the app starts
- **Terminal-Based**: No GUI dependencies, lightweight and reliable

## Prerequisites

- Ubuntu with X11 session (not Wayland)
- Python 3.11 or higher
- User must be in the input group

## Setup

1. **Install Python 3.11+** (if not already installed):
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-pip
   ```

2. **Add user to input group** (required for pynput):
   ```bash
   sudo usermod -aG input $USER
   ```
   Then **reboot** your system for the changes to take effect.

3. **Verify X11 session**:
   ```bash
   echo $XDG_SESSION_TYPE
   ```
   Should return `x11`. If it returns `wayland`, switch to X11 via the login screen session selector.

4. **Install required libraries**:
   ```bash
   # Option 1: Try with --user flag first
   pip3 install --user -r requirements.txt
   
   # Option 2: If that fails, use --break-system-packages
   pip3 install --break-system-packages -r requirements.txt
   
   # Option 3: Use virtual environment (recommended)
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   python3 autoclicker.py
   ```

2. **Configure intervals**:
   - Enter minutes and seconds for the primary clicker
   - Choose whether to enable a secondary clicker
   - If enabled, enter its interval

3. **Control the clickers**:
   - Press **F1** to toggle the primary clicker
   - Press **F2** to toggle the secondary clicker (if enabled)
   - Press **Ctrl+C** to exit the application
   - Move mouse to top-left corner to trigger failsafe stop

## Example

```
=== Simple Autoclicker for Ubuntu ===
Press F1 to toggle primary clicker, F2 to toggle secondary clicker
Move mouse to top-left corner to stop the application

Enter minutes for primary clicker: 0
Enter seconds for primary clicker: 5
Enable secondary clicker? (y/n): y
Enter minutes for secondary clicker: 0
Enter seconds for secondary clicker: 30
Mouse position captured: (500, 300)

Autoclicker ready! Press F1 to start primary clicker.
Press F2 to start secondary clicker.
Press Ctrl+C to exit.
```

## Troubleshooting

- **Hotkeys not working**: Ensure you're in the input group and have rebooted
- **Clicks not occurring**: Verify X11 session and mouse position
- **Permission errors**: Check input group membership with `groups $USER`
- **"Externally managed environment" error**: Use one of these solutions:
  - `pip3 install --break-system-packages -r requirements.txt`
  - Or use virtual environment: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- **Library issues**: Use a virtual environment: `python3 -m venv env && source env/bin/activate`

## Notes

- The application captures the mouse position at startup and clicks at that exact location
- Both clickers synchronize to prevent temporal drift
- The application is designed to be lightweight and reliable on Ubuntu
- X11 session is recommended for best compatibility with pyautogui

