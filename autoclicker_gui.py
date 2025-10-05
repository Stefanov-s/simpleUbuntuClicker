#!/usr/bin/env python3
"""
Simple Autoclicker GUI for Ubuntu
A modern GUI interface for the autoclicker with tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import platform
from pynput import keyboard
import pyautogui

# Configure pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

class AutoclickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Autoclicker for Ubuntu")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Detect platform
        self.platform = platform.system().lower()
        if self.platform == "windows":
            self.root.title("Simple Autoclicker (Windows)")
        
        # Variables
        self.primary_active = False
        self.secondary_active = False
        self.start_time = None
        self.primary_interval = 5  # seconds
        self.secondary_interval = 30  # seconds
        self.primary_thread = None
        self.secondary_thread = None
        self.keyboard_listener = None
        
        # Create GUI
        self.create_widgets()
        self.setup_keyboard_listener()
        
    def create_widgets(self):
        """Create and layout GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Simple Autoclicker for Ubuntu", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Primary Clicker Section
        primary_frame = ttk.LabelFrame(main_frame, text="Primary Clicker", padding="10")
        primary_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        primary_frame.columnconfigure(1, weight=1)
        
        # Primary interval
        ttk.Label(primary_frame, text="Interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.primary_interval_var = tk.StringVar(value="5")
        primary_spinbox = ttk.Spinbox(primary_frame, from_=1, to=3600, width=10, 
                                    textvariable=self.primary_interval_var)
        primary_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Primary status and control
        self.primary_status_var = tk.StringVar(value="OFF")
        self.primary_status_label = ttk.Label(primary_frame, textvariable=self.primary_status_var, 
                                              font=("Arial", 12, "bold"))
        self.primary_status_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.primary_button = ttk.Button(primary_frame, text="Start Primary", 
                                        command=self.toggle_primary)
        self.primary_button.grid(row=1, column=1, sticky=tk.E, pady=(10, 0))
        
        # Secondary Clicker Section
        secondary_frame = ttk.LabelFrame(main_frame, text="Secondary Clicker", padding="10")
        secondary_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        secondary_frame.columnconfigure(1, weight=1)
        
        # Secondary enable checkbox
        self.secondary_enabled_var = tk.BooleanVar()
        secondary_check = ttk.Checkbutton(secondary_frame, text="Enable Secondary Clicker",
                                        variable=self.secondary_enabled_var,
                                        command=self.toggle_secondary_enable)
        secondary_check.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Secondary interval (initially disabled)
        ttk.Label(secondary_frame, text="Interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.secondary_interval_var = tk.StringVar(value="30")
        self.secondary_spinbox = ttk.Spinbox(secondary_frame, from_=1, to=3600, width=10,
                                           textvariable=self.secondary_interval_var, state="disabled")
        self.secondary_spinbox.grid(row=1, column=1, sticky=tk.W)
        
        # Secondary status and control
        self.secondary_status_var = tk.StringVar(value="OFF")
        self.secondary_status_label = ttk.Label(secondary_frame, textvariable=self.secondary_status_var,
                                               font=("Arial", 12, "bold"))
        self.secondary_status_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        self.secondary_button = ttk.Button(secondary_frame, text="Start Secondary",
                                         command=self.toggle_secondary, state="disabled")
        self.secondary_button.grid(row=2, column=1, sticky=tk.E, pady=(10, 0))
        
        # Control Section
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        # Stop all button
        self.stop_all_button = ttk.Button(control_frame, text="Stop All", 
                                         command=self.stop_all, state="disabled")
        self.stop_all_button.pack(side=tk.LEFT)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_text = tk.Text(status_frame, height=6, width=50, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Initial status message
        self.log_message("Autoclicker GUI ready!")
        self.log_message(f"Platform: {self.platform.title()}")
        self.log_message("Press F1 to toggle primary clicker, F2 to toggle secondary clicker")
        if self.platform == "linux":
            self.log_message("Move mouse to top-left corner for emergency stop")
        else:
            self.log_message("Use Stop All button or close window to stop")
        
    def setup_keyboard_listener(self):
        """Setup keyboard listener for F1/F2 hotkeys."""
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            self.keyboard_listener.start()
            self.log_message("Keyboard listener started - F1/F2 hotkeys active")
        except Exception as e:
            self.log_message(f"Warning: Could not start keyboard listener: {e}")
            self.log_message("Hotkeys may not work - use GUI buttons instead")
    
    def on_key_press(self, key):
        """Handle key press events."""
        try:
            if key == keyboard.Key.f1:
                self.root.after(0, self.toggle_primary)
            elif key == keyboard.Key.f2 and self.secondary_enabled_var.get():
                self.root.after(0, self.toggle_secondary)
        except AttributeError:
            pass
    
    def toggle_primary(self):
        """Toggle primary clicker on/off."""
        if not self.primary_active:
            self.start_primary()
        else:
            self.stop_primary()
    
    def start_primary(self):
        """Start primary clicker."""
        try:
            self.primary_interval = int(self.primary_interval_var.get())
            if self.primary_interval <= 0:
                messagebox.showerror("Error", "Interval must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for interval")
            return
        
        self.primary_active = True
        self.start_time = time.time()
        self.primary_status_var.set("ON")
        self.primary_status_label.configure(foreground="green")
        self.primary_button.configure(text="Stop Primary")
        
        # Start primary thread
        self.primary_thread = threading.Thread(target=self.primary_click_thread, daemon=True)
        self.primary_thread.start()
        
        self.log_message("Primary clicker started")
        self.update_stop_all_button()
    
    def stop_primary(self):
        """Stop primary clicker."""
        self.primary_active = False
        self.primary_status_var.set("OFF")
        self.primary_status_label.configure(foreground="red")
        self.primary_button.configure(text="Start Primary")
        
        # Reset start_time if no clickers are active
        if not self.secondary_active:
            self.start_time = None
        
        self.log_message("Primary clicker stopped")
        self.update_stop_all_button()
    
    def toggle_secondary(self):
        """Toggle secondary clicker on/off."""
        if not self.secondary_active:
            self.start_secondary()
        else:
            self.stop_secondary()
    
    def start_secondary(self):
        """Start secondary clicker."""
        try:
            self.secondary_interval = int(self.secondary_interval_var.get())
            if self.secondary_interval <= 0:
                messagebox.showerror("Error", "Interval must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for interval")
            return
        
        self.secondary_active = True
        if self.start_time is None:
            self.start_time = time.time()
        self.secondary_status_var.set("ON")
        self.secondary_status_label.configure(foreground="green")
        self.secondary_button.configure(text="Stop Secondary")
        
        # Start secondary thread
        self.secondary_thread = threading.Thread(target=self.secondary_click_thread, daemon=True)
        self.secondary_thread.start()
        
        self.log_message("Secondary clicker started")
        self.update_stop_all_button()
    
    def stop_secondary(self):
        """Stop secondary clicker."""
        self.secondary_active = False
        self.secondary_status_var.set("OFF")
        self.secondary_status_label.configure(foreground="red")
        self.secondary_button.configure(text="Start Secondary")
        
        # Reset start_time if no clickers are active
        if not self.primary_active:
            self.start_time = None
        
        self.log_message("Secondary clicker stopped")
        self.update_stop_all_button()
    
    def toggle_secondary_enable(self):
        """Enable/disable secondary clicker controls."""
        if self.secondary_enabled_var.get():
            self.secondary_spinbox.configure(state="normal")
            self.secondary_button.configure(state="normal")
            self.log_message("Secondary clicker enabled")
        else:
            if self.secondary_active:
                self.stop_secondary()
            self.secondary_spinbox.configure(state="disabled")
            self.secondary_button.configure(state="disabled")
            self.log_message("Secondary clicker disabled")
    
    def stop_all(self):
        """Stop all clickers."""
        if self.primary_active:
            self.stop_primary()
        if self.secondary_active:
            self.stop_secondary()
        self.log_message("All clickers stopped")
    
    
    def primary_click_thread(self):
        """Thread function for primary autoclicker."""
        last_click_time = 0
        while self.primary_active:
            if self.start_time is not None:
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed % self.primary_interval < 0.1 and elapsed - last_click_time >= self.primary_interval * 0.9:
                    current_x, current_y = pyautogui.position()
                    pyautogui.click(current_x, current_y)
                    last_click_time = elapsed
                    self.root.after(0, lambda: self.log_message(f"Primary click at {elapsed:.1f}s at ({current_x}, {current_y})"))
            time.sleep(0.01)
    
    def secondary_click_thread(self):
        """Thread function for secondary autoclicker."""
        last_click_time = 0
        while self.secondary_active:
            if self.start_time is not None:
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed % self.secondary_interval < 0.1 and elapsed - last_click_time >= self.secondary_interval * 0.9:
                    current_x, current_y = pyautogui.position()
                    pyautogui.click(current_x, current_y)
                    last_click_time = elapsed
                    self.root.after(0, lambda: self.log_message(f"Secondary click at {elapsed:.1f}s at ({current_x}, {current_y})"))
            time.sleep(0.01)
    
    def update_stop_all_button(self):
        """Update stop all button state."""
        if self.primary_active or self.secondary_active:
            self.stop_all_button.configure(state="normal")
        else:
            self.stop_all_button.configure(state="disabled")
    
    def log_message(self, message):
        """Add message to status log."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
    
    def on_closing(self):
        """Handle window closing."""
        self.stop_all()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.root.destroy()

def main():
    """Main function."""
    root = tk.Tk()
    app = AutoclickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
