# Ubuntu Setup Guide for GUI Autoclicker

## Prerequisites (Same as Terminal Version)

### 1. **Install Python 3.11+**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 2. **Add User to Input Group** (Required for pynput)
```bash
sudo usermod -aG input $USER
sudo reboot  # REQUIRED - reboot for changes to take effect
```

### 3. **Verify X11 Session** (Not Wayland)
```bash
echo $XDG_SESSION_TYPE
# Should return 'x11', not 'wayland'
# If wayland, switch to X11 via login screen session selector
```

## Additional Requirements for GUI

### 4. **Install tkinter** (GUI Framework)
```bash
# For Ubuntu 20.04+
sudo apt install python3-tk

# For older Ubuntu versions
sudo apt install python3-tkinter
```

### 5. **Install Python Dependencies**
```bash
# Option 1: Virtual Environment (Recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: System-wide (if virtual env fails)
pip3 install --user -r requirements.txt
# OR
pip3 install --break-system-packages -r requirements.txt
```

## Running the GUI

### **Method 1: Direct GUI**
```bash
python3 autoclicker_gui.py
```

### **Method 2: Smart Launcher**
```bash
python3 run_autoclicker.py
```

### **Method 3: Test First**
```bash
python3 test_gui.py  # Test if everything works
```

## Troubleshooting

### **GUI Won't Start**
```bash
# Test tkinter
python3 -c "import tkinter; print('tkinter works')"

# If error: install tkinter
sudo apt install python3-tk
```

### **Hotkeys Don't Work**
```bash
# Check input group
groups $USER
# Should show 'input' in the list

# If not in input group:
sudo usermod -aG input $USER
sudo reboot
```

### **Clicks Don't Work**
```bash
# Check session type
echo $XDG_SESSION_TYPE
# Should be 'x11'

# Check if running as root (don't do this)
whoami
# Should be your username, not 'root'
```

### **Permission Errors**
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 autoclicker_gui.py
```

## What's Different from Terminal Version

### **New Files Added:**
- `autoclicker_gui.py` - GUI interface
- `run_autoclicker.py` - Smart launcher
- `test_gui.py` - Test script

### **Additional Dependencies:**
- `python3-tk` - For GUI framework
- Same `pynput` and `pyautogui` as before

### **Same Requirements:**
- Input group membership
- X11 session (not Wayland)
- Python 3.11+

## Quick Setup Script

```bash
#!/bin/bash
# Quick setup for Ubuntu GUI autoclicker

echo "=== Ubuntu GUI Autoclicker Setup ==="

# Install Python and tkinter
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv python3-tk

# Add to input group
sudo usermod -aG input $USER

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Setup complete! Please reboot your system."
echo "After reboot, run: python3 autoclicker_gui.py"
```

## Button Differences Explained

### **Stop All Button:**
- **What it does**: Gracefully stops all active clickers
- **When enabled**: Only when at least one clicker is running
- **Behavior**: Normal stop, no confirmation dialog

### **Emergency Stop Button:**
- **What it does**: Instantly stops everything with confirmation
- **When enabled**: Always available
- **Behavior**: Shows confirmation dialog, then stops all clickers
- **Use case**: When you need to stop immediately and confirm the action
