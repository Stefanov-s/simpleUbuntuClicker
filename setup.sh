#!/bin/bash

# Simple Autoclicker Setup Script for Ubuntu

echo "=== Simple Autoclicker Setup ==="
echo

# Check if running on Ubuntu
if ! command -v apt &> /dev/null; then
    echo "Error: This script is designed for Ubuntu/Debian systems."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python3_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$python3_version >= 3.11" | bc -l) -eq 0 ]]; then
    echo "Installing Python 3.11..."
    sudo apt update
    sudo apt install -y python3.11 python3.11-pip python3.11-venv
else
    echo "Python $python3_version found - OK"
fi

# Add user to input group
echo "Adding user to input group..."
if groups $USER | grep -q "\binput\b"; then
    echo "User already in input group - OK"
else
    echo "Adding user to input group (requires sudo)..."
    sudo usermod -aG input $USER
    echo "User added to input group. Please reboot your system for changes to take effect."
fi

# Check X11 session
echo "Checking display session..."
if [[ "$XDG_SESSION_TYPE" == "x11" ]]; then
    echo "X11 session detected - OK"
else
    echo "Warning: Not running on X11 session. Current session: $XDG_SESSION_TYPE"
    echo "For best compatibility, please switch to X11 session via login screen."
fi

# Install Python packages
echo "Installing Python packages..."
if command -v pip3 &> /dev/null; then
    # Try to install with --user first, if that fails, use --break-system-packages
    if pip3 install --user pynput pyautogui 2>/dev/null; then
        echo "Python packages installed with --user - OK"
    else
        echo "Trying with --break-system-packages flag..."
        pip3 install --break-system-packages pynput pyautogui
        echo "Python packages installed with --break-system-packages - OK"
    fi
else
    echo "Error: pip3 not found. Please install python3-pip first."
    exit 1
fi

echo
echo "=== Setup Complete ==="
echo "Next steps:"
echo "1. Reboot your system if you were added to the input group"
echo "2. Run: python3 autoclicker.py"
echo "3. If you encounter issues, check the README.md for troubleshooting"

