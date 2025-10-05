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
        self.root.geometry("550x550")
        self.root.resizable(True, True)
        
        # Make window always on top
        self.root.attributes('-topmost', True)
        
        # Detect platform
        self.platform = platform.system().lower()
        if self.platform == "windows":
            self.root.title("Simple Autoclicker (Windows)")
        
        # Variables
        self.primary_active = False
        self.secondary_active = False
        self.tertiary_active = False
        self.start_time = None
        self.primary_interval = 5  # seconds
        self.secondary_interval = 30  # seconds
        self.tertiary_interval = 60  # seconds
        self.primary_thread = None
        self.secondary_thread = None
        self.tertiary_thread = None
        self.keyboard_listener = None
        
        # Coordinate settings
        self.primary_use_coordinates = False
        self.secondary_use_coordinates = False
        self.tertiary_use_coordinates = False
        self.primary_click_x = 0
        self.primary_click_y = 0
        self.secondary_click_x = 0
        self.secondary_click_y = 0
        self.tertiary_click_x = 0
        self.tertiary_click_y = 0
        
        # Create GUI
        self.create_widgets()
        self.setup_keyboard_listener()
        
        # Recorder variables
        self.recording = False
        self.playing = False
        self.recorded_clicks = []
        self.replay_count = 1
        self.current_replay = 0
        self.recorder_thread = None
        
    def create_widgets(self):
        """Create and layout GUI widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_clicker_tab()
        self.create_recorder_tab()
        
    def create_clicker_tab(self):
        """Create the main autoclicker tab."""
        # Main frame
        main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(main_frame, text="Autoclicker")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Simple Autoclicker for Ubuntu", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Clicker Controls (Compact)
        controls_frame = ttk.LabelFrame(main_frame, text="Clicker Controls", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Primary Clicker (Always visible)
        primary_row = ttk.Frame(controls_frame)
        primary_row.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        primary_row.columnconfigure(1, weight=1)
        
        # Primary interval
        ttk.Label(primary_row, text="Interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.primary_interval_var = tk.StringVar(value="5")
        primary_spinbox = ttk.Spinbox(primary_row, from_=1, to=3600, width=10, 
                                    textvariable=self.primary_interval_var)
        primary_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Primary coordinate settings
        coord_frame = ttk.Frame(primary_row)
        coord_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.primary_coord_var = tk.BooleanVar()
        coord_check = ttk.Checkbutton(coord_frame, text="Use fixed coordinates",
                                     variable=self.primary_coord_var, command=self.toggle_primary_coords)
        coord_check.grid(row=0, column=0, sticky=tk.W)
        
        self.primary_coord_button = ttk.Button(coord_frame, text="Set Coordinates", 
                                             command=self.set_primary_coordinates, state="disabled")
        self.primary_coord_button.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        self.primary_coord_label = ttk.Label(coord_frame, text="Coordinates: Not set", 
                                           font=("Arial", 9), foreground="gray")
        self.primary_coord_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Primary status and control
        self.primary_status_var = tk.StringVar(value="OFF")
        self.primary_status_label = ttk.Label(primary_row, textvariable=self.primary_status_var, 
                                              font=("Arial", 12, "bold"))
        self.primary_status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        self.primary_button = ttk.Button(primary_row, text="Start Primary", 
                                        command=self.toggle_primary)
        self.primary_button.grid(row=2, column=1, sticky=tk.E, pady=(5, 0))
        
        # Secondary Clicker (Collapsible)
        self.secondary_enabled_var = tk.BooleanVar()
        self.secondary_check = ttk.Checkbutton(controls_frame, text="Enable Secondary Clicker",
                                             variable=self.secondary_enabled_var,
                                             command=self.toggle_secondary_enable)
        self.secondary_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Secondary controls (hidden by default)
        self.secondary_controls_frame = ttk.Frame(controls_frame)
        
        # Tertiary Clicker (Collapsible)
        self.tertiary_enabled_var = tk.BooleanVar()
        self.tertiary_check = ttk.Checkbutton(controls_frame, text="Enable Tertiary Clicker",
                                            variable=self.tertiary_enabled_var,
                                            command=self.toggle_tertiary_enable)
        self.tertiary_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Tertiary controls (hidden by default)
        self.tertiary_controls_frame = ttk.Frame(controls_frame)
        
        # Control Section
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0))
        
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
    
    def create_recorder_tab(self):
        """Create the recorder tab."""
        # Main frame
        recorder_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(recorder_frame, text="Recorder")
        
        # Configure grid weights
        recorder_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(recorder_frame, text="Click Sequence Recorder", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Recording Section
        record_frame = ttk.LabelFrame(recorder_frame, text="Recording", padding="10")
        record_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        record_frame.columnconfigure(1, weight=1)
        
        # Record button
        self.record_button = ttk.Button(record_frame, text="Start Recording", 
                                      command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Recording status
        self.recording_status_var = tk.StringVar(value="Not Recording")
        self.recording_status_label = ttk.Label(record_frame, textvariable=self.recording_status_var,
                                               font=("Arial", 12, "bold"))
        self.recording_status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Clear button
        self.clear_button = ttk.Button(record_frame, text="Clear Sequence", 
                                      command=self.clear_sequence, state="disabled")
        self.clear_button.grid(row=0, column=2, sticky=tk.E)
        
        
        # Sequence display
        seq_frame = ttk.LabelFrame(recorder_frame, text="Recorded Sequence", padding="10")
        seq_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        seq_frame.columnconfigure(0, weight=1)
        
        self.sequence_text = tk.Text(seq_frame, height=8, width=60, wrap=tk.WORD, state="disabled")
        self.sequence_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for sequence text
        seq_scrollbar = ttk.Scrollbar(seq_frame, orient=tk.VERTICAL, command=self.sequence_text.yview)
        seq_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.sequence_text.configure(yscrollcommand=seq_scrollbar.set)
        
        # Playback Section
        playback_frame = ttk.LabelFrame(recorder_frame, text="Playback", padding="10")
        playback_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        playback_frame.columnconfigure(1, weight=1)
        
        # Repeat count
        ttk.Label(playback_frame, text="Repeat Count:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.repeat_var = tk.StringVar(value="1")
        repeat_spinbox = ttk.Spinbox(playback_frame, from_=1, to=1000, width=10,
                                    textvariable=self.repeat_var)
        repeat_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Replay interval
        ttk.Label(playback_frame, text="Interval between replays (seconds):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.replay_interval_var = tk.StringVar(value="0")
        replay_interval_spinbox = ttk.Spinbox(playback_frame, from_=0, to=3600, width=10,
                                            textvariable=self.replay_interval_var)
        replay_interval_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Play button
        self.play_button = ttk.Button(playback_frame, text="Play Sequence", 
                                    command=self.toggle_playback, state="disabled")
        self.play_button.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        
        # Playback status
        self.playback_status_var = tk.StringVar(value="Ready")
        self.playback_status_label = ttk.Label(playback_frame, textvariable=self.playback_status_var,
                                             font=("Arial", 12, "bold"))
        self.playback_status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(playback_frame, textvariable=self.progress_var,
                                      font=("Arial", 10))
        self.progress_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Instructions
        instructions_frame = ttk.Frame(recorder_frame)
        instructions_frame.grid(row=4, column=0, columnspan=3, pady=(20, 0))
        
        instructions_text = ttk.Label(instructions_frame, 
                                     text="Instructions: 1) Click 'Start Recording' 2) Perform your click sequence 3) Click 'Stop Recording' 4) Set repeat count 5) Click 'Play Sequence'",
                                     font=("Arial", 9), foreground="gray")
        instructions_text.pack()
        
        # Hotkey info
        hotkey_text = ttk.Label(instructions_frame, 
                               text="Hotkeys: F1=Primary, F2=Secondary, F3=Tertiary, F4=Recording, F5=Playback (Ubuntu optimized)",
                               font=("Arial", 9), foreground="blue")
        hotkey_text.pack()
        
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
            elif key == keyboard.Key.f3 and self.tertiary_enabled_var.get():
                self.root.after(0, self.toggle_tertiary)
            elif key == keyboard.Key.f4:
                self.root.after(0, self.toggle_recording)
            elif key == keyboard.Key.f5:
                self.root.after(0, self.toggle_playback)
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
    
    def toggle_tertiary(self):
        """Toggle tertiary clicker on/off."""
        if not self.tertiary_active:
            self.start_tertiary()
        else:
            self.stop_tertiary()
    
    def start_tertiary(self):
        """Start tertiary clicker."""
        try:
            self.tertiary_interval = int(self.tertiary_interval_var.get())
            if self.tertiary_interval <= 0:
                messagebox.showerror("Error", "Interval must be greater than 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for interval")
            return
        
        self.tertiary_active = True
        if self.start_time is None:
            self.start_time = time.time()
        self.tertiary_status_var.set("ON")
        self.tertiary_status_label.configure(foreground="green")
        self.tertiary_button.configure(text="Stop Tertiary")
        
        # Start tertiary thread
        self.tertiary_thread = threading.Thread(target=self.tertiary_click_thread, daemon=True)
        self.tertiary_thread.start()
        
        self.log_message("Tertiary clicker started")
        self.update_stop_all_button()
    
    def stop_tertiary(self):
        """Stop tertiary clicker."""
        self.tertiary_active = False
        self.tertiary_status_var.set("OFF")
        self.tertiary_status_label.configure(foreground="red")
        self.tertiary_button.configure(text="Start Tertiary")
        
        # Reset start_time if no clickers are active
        if not self.primary_active and not self.secondary_active:
            self.start_time = None
        
        self.log_message("Tertiary clicker stopped")
        self.update_stop_all_button()
    
    def toggle_secondary_enable(self):
        """Enable/disable secondary clicker controls."""
        if self.secondary_enabled_var.get():
            self.create_secondary_controls()
            self.log_message("Secondary clicker enabled")
        else:
            if self.secondary_active:
                self.stop_secondary()
            self.hide_secondary_controls()
            self.log_message("Secondary clicker disabled")
    
    def toggle_tertiary_enable(self):
        """Enable/disable tertiary clicker controls."""
        if self.tertiary_enabled_var.get():
            self.create_tertiary_controls()
            self.log_message("Tertiary clicker enabled")
        else:
            if self.tertiary_active:
                self.stop_tertiary()
            self.hide_tertiary_controls()
            self.log_message("Tertiary clicker disabled")
    
    def create_secondary_controls(self):
        """Create secondary clicker controls."""
        self.secondary_controls_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.secondary_controls_frame.columnconfigure(1, weight=1)
        
        # Secondary interval
        ttk.Label(self.secondary_controls_frame, text="Interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.secondary_interval_var = tk.StringVar(value="30")
        self.secondary_spinbox = ttk.Spinbox(self.secondary_controls_frame, from_=1, to=3600, width=10,
                                           textvariable=self.secondary_interval_var)
        self.secondary_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Secondary coordinate settings
        sec_coord_frame = ttk.Frame(self.secondary_controls_frame)
        sec_coord_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.secondary_coord_var = tk.BooleanVar()
        sec_coord_check = ttk.Checkbutton(sec_coord_frame, text="Use fixed coordinates",
                                        variable=self.secondary_coord_var, command=self.toggle_secondary_coords)
        sec_coord_check.grid(row=0, column=0, sticky=tk.W)
        
        self.secondary_coord_button = ttk.Button(sec_coord_frame, text="Set Coordinates", 
                                               command=self.set_secondary_coordinates, state="disabled")
        self.secondary_coord_button.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        self.secondary_coord_label = ttk.Label(sec_coord_frame, text="Coordinates: Not set", 
                                             font=("Arial", 9), foreground="gray")
        self.secondary_coord_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Secondary status and control
        self.secondary_status_var = tk.StringVar(value="OFF")
        self.secondary_status_label = ttk.Label(self.secondary_controls_frame, textvariable=self.secondary_status_var,
                                               font=("Arial", 12, "bold"))
        self.secondary_status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        self.secondary_button = ttk.Button(self.secondary_controls_frame, text="Start Secondary",
                                         command=self.toggle_secondary)
        self.secondary_button.grid(row=2, column=1, sticky=tk.E, pady=(5, 0))
    
    def create_tertiary_controls(self):
        """Create tertiary clicker controls."""
        self.tertiary_controls_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.tertiary_controls_frame.columnconfigure(1, weight=1)
        
        # Tertiary interval
        ttk.Label(self.tertiary_controls_frame, text="Interval (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.tertiary_interval_var = tk.StringVar(value="60")
        self.tertiary_spinbox = ttk.Spinbox(self.tertiary_controls_frame, from_=1, to=3600, width=10,
                                          textvariable=self.tertiary_interval_var)
        self.tertiary_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Tertiary coordinate settings
        tert_coord_frame = ttk.Frame(self.tertiary_controls_frame)
        tert_coord_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.tertiary_coord_var = tk.BooleanVar()
        tert_coord_check = ttk.Checkbutton(tert_coord_frame, text="Use fixed coordinates",
                                         variable=self.tertiary_coord_var, command=self.toggle_tertiary_coords)
        tert_coord_check.grid(row=0, column=0, sticky=tk.W)
        
        self.tertiary_coord_button = ttk.Button(tert_coord_frame, text="Set Coordinates", 
                                              command=self.set_tertiary_coordinates, state="disabled")
        self.tertiary_coord_button.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        self.tertiary_coord_label = ttk.Label(tert_coord_frame, text="Coordinates: Not set", 
                                            font=("Arial", 9), foreground="gray")
        self.tertiary_coord_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Tertiary status and control
        self.tertiary_status_var = tk.StringVar(value="OFF")
        self.tertiary_status_label = ttk.Label(self.tertiary_controls_frame, textvariable=self.tertiary_status_var,
                                              font=("Arial", 12, "bold"))
        self.tertiary_status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        self.tertiary_button = ttk.Button(self.tertiary_controls_frame, text="Start Tertiary",
                                        command=self.toggle_tertiary)
        self.tertiary_button.grid(row=2, column=1, sticky=tk.E, pady=(5, 0))
    
    def hide_secondary_controls(self):
        """Hide secondary clicker controls."""
        self.secondary_controls_frame.grid_remove()
    
    def hide_tertiary_controls(self):
        """Hide tertiary clicker controls."""
        self.tertiary_controls_frame.grid_remove()
    
    def toggle_primary_coords(self):
        """Toggle primary coordinate mode."""
        self.primary_use_coordinates = self.primary_coord_var.get()
        if self.primary_use_coordinates:
            self.primary_coord_button.configure(state="normal")
            self.log_message("Primary clicker: Coordinate mode enabled")
        else:
            self.primary_coord_button.configure(state="disabled")
            self.log_message("Primary clicker: Mouse tracking mode")
    
    def toggle_secondary_coords(self):
        """Toggle secondary coordinate mode."""
        self.secondary_use_coordinates = self.secondary_coord_var.get()
        if self.secondary_use_coordinates:
            self.secondary_coord_button.configure(state="normal")
            self.log_message("Secondary clicker: Coordinate mode enabled")
        else:
            self.secondary_coord_button.configure(state="disabled")
            self.log_message("Secondary clicker: Mouse tracking mode")
    
    def toggle_tertiary_coords(self):
        """Toggle tertiary coordinate mode."""
        self.tertiary_use_coordinates = self.tertiary_coord_var.get()
        if self.tertiary_use_coordinates:
            self.tertiary_coord_button.configure(state="normal")
            self.log_message("Tertiary clicker: Coordinate mode enabled")
        else:
            self.tertiary_coord_button.configure(state="disabled")
            self.log_message("Tertiary clicker: Mouse tracking mode")
    
    def set_primary_coordinates(self):
        """Set primary clicker coordinates by clicking."""
        self.root.withdraw()  # Hide window
        self.log_message("Click anywhere to set primary coordinates...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.primary_click_x = x
                self.primary_click_y = y
                self.primary_coord_label.configure(text=f"Coordinates: ({x}, {y})", foreground="green")
                self.log_message(f"Primary coordinates set to ({x}, {y})")
                self.log_message(f"DEBUG: Stored coordinates are now ({self.primary_click_x}, {self.primary_click_y})")
                self.root.deiconify()  # Show window again
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_secondary_coordinates(self):
        """Set secondary clicker coordinates by clicking."""
        self.root.withdraw()  # Hide window
        self.log_message("Click anywhere to set secondary coordinates...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.secondary_click_x = x
                self.secondary_click_y = y
                self.secondary_coord_label.configure(text=f"Coordinates: ({x}, {y})", foreground="green")
                self.log_message(f"Secondary coordinates set to ({x}, {y})")
                self.root.deiconify()  # Show window again
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def set_tertiary_coordinates(self):
        """Set tertiary clicker coordinates by clicking."""
        self.root.withdraw()  # Hide window
        self.log_message("Click anywhere to set tertiary coordinates...")
        
        def on_click(x, y, button, pressed):
            if pressed:
                self.tertiary_click_x = x
                self.tertiary_click_y = y
                self.tertiary_coord_label.configure(text=f"Coordinates: ({x}, {y})", foreground="green")
                self.log_message(f"Tertiary coordinates set to ({x}, {y})")
                self.root.deiconify()  # Show window again
                return False  # Stop listener
        
        # Start mouse listener
        from pynput import mouse
        listener = mouse.Listener(on_click=on_click)
        listener.start()
    
    def stop_all(self):
        """Stop all clickers."""
        if self.primary_active:
            self.stop_primary()
        if self.secondary_active:
            self.stop_secondary()
        if self.tertiary_active:
            self.stop_tertiary()
        self.log_message("All clickers stopped")
    
    
    def primary_click_thread(self):
        """Thread function for primary autoclicker."""
        last_click_time = 0
        while self.primary_active:
            if self.start_time is not None:
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed % self.primary_interval < 0.1 and elapsed - last_click_time >= self.primary_interval * 0.9:
                    if self.primary_use_coordinates:
                        # Use fixed coordinates
                        self.root.after(0, lambda: self.log_message(f"DEBUG: Using coordinates ({self.primary_click_x}, {self.primary_click_y})"))
                        pyautogui.click(self.primary_click_x, self.primary_click_y)
                        self.root.after(0, lambda: self.log_message(f"Primary click at {elapsed:.1f}s at fixed coordinates ({self.primary_click_x}, {self.primary_click_y})"))
                    else:
                        # Use current mouse position
                        current_x, current_y = pyautogui.position()
                        pyautogui.click(current_x, current_y)
                        self.root.after(0, lambda: self.log_message(f"Primary click at {elapsed:.1f}s at mouse position ({current_x}, {current_y})"))
                    last_click_time = elapsed
            time.sleep(0.01)
    
    def secondary_click_thread(self):
        """Thread function for secondary autoclicker."""
        last_click_time = 0
        while self.secondary_active:
            if self.start_time is not None:
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed % self.secondary_interval < 0.1 and elapsed - last_click_time >= self.secondary_interval * 0.9:
                    if self.secondary_use_coordinates:
                        # Use fixed coordinates
                        pyautogui.click(self.secondary_click_x, self.secondary_click_y)
                        self.root.after(0, lambda: self.log_message(f"Secondary click at {elapsed:.1f}s at fixed coordinates ({self.secondary_click_x}, {self.secondary_click_y})"))
                    else:
                        # Use current mouse position
                        current_x, current_y = pyautogui.position()
                        pyautogui.click(current_x, current_y)
                        self.root.after(0, lambda: self.log_message(f"Secondary click at {elapsed:.1f}s at mouse position ({current_x}, {current_y})"))
                    last_click_time = elapsed
            time.sleep(0.01)
    
    def tertiary_click_thread(self):
        """Thread function for tertiary autoclicker."""
        last_click_time = 0
        while self.tertiary_active:
            if self.start_time is not None:
                current_time = time.time()
                elapsed = current_time - self.start_time
                if elapsed % self.tertiary_interval < 0.1 and elapsed - last_click_time >= self.tertiary_interval * 0.9:
                    if self.tertiary_use_coordinates:
                        # Use fixed coordinates
                        pyautogui.click(self.tertiary_click_x, self.tertiary_click_y)
                        self.root.after(0, lambda: self.log_message(f"Tertiary click at {elapsed:.1f}s at fixed coordinates ({self.tertiary_click_x}, {self.tertiary_click_y})"))
                    else:
                        # Use current mouse position
                        current_x, current_y = pyautogui.position()
                        pyautogui.click(current_x, current_y)
                        self.root.after(0, lambda: self.log_message(f"Tertiary click at {elapsed:.1f}s at mouse position ({current_x}, {current_y})"))
                    last_click_time = elapsed
            time.sleep(0.01)
    
    def update_stop_all_button(self):
        """Update stop all button state."""
        if self.primary_active or self.secondary_active or self.tertiary_active:
            self.stop_all_button.configure(state="normal")
        else:
            self.stop_all_button.configure(state="disabled")
    
    def log_message(self, message):
        """Add message to status log."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
    
    def toggle_recording(self):
        """Toggle recording on/off."""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording clicks."""
        self.recording = True
        self.recorded_clicks = []
        self.recording_status_var.set("Recording...")
        self.recording_status_label.configure(foreground="red")
        self.record_button.configure(text="Stop Recording")
        self.clear_button.configure(state="disabled")
        self.play_button.configure(state="disabled")
        
        # Clear sequence display
        self.sequence_text.configure(state="normal")
        self.sequence_text.delete(1.0, tk.END)
        self.sequence_text.insert(tk.END, "Recording... Click anywhere to record clicks.\n")
        self.sequence_text.configure(state="disabled")
        
        self.log_message("Recording started - click anywhere to record")
        
        # Start mouse listener for recording
        self.start_click_listener()
    
    def stop_recording(self):
        """Stop recording clicks."""
        self.recording = False
        self.recording_status_var.set("Recording Stopped")
        self.recording_status_label.configure(foreground="green")
        self.record_button.configure(text="Start Recording")
        self.clear_button.configure(state="normal")
        
        if self.recorded_clicks:
            self.play_button.configure(state="normal")
            self.update_sequence_display()
            self.log_message(f"Recording stopped - {len(self.recorded_clicks)} clicks recorded")
        else:
            self.log_message("Recording stopped - no clicks recorded")
    
    def start_click_listener(self):
        """Start listening for clicks to record."""
        def on_click(x, y, button, pressed):
            if pressed and self.recording:
                click_time = time.time()
                self.recorded_clicks.append({
                    'x': x, 'y': y, 'button': str(button), 'time': click_time
                })
                self.log_message(f"Recorded click at ({x}, {y})")
        
        from pynput import mouse
        self.click_listener = mouse.Listener(on_click=on_click)
        self.click_listener.start()
        self.log_message("Click listener started successfully")
    
    def update_sequence_display(self):
        """Update the sequence display."""
        self.sequence_text.configure(state="normal")
        self.sequence_text.delete(1.0, tk.END)
        
        if not self.recorded_clicks:
            self.sequence_text.insert(tk.END, "No clicks recorded.")
        else:
            self.sequence_text.insert(tk.END, f"Recorded {len(self.recorded_clicks)} clicks:\n\n")
            for i, click in enumerate(self.recorded_clicks):
                self.sequence_text.insert(tk.END, f"{i+1}. Click at ({click['x']}, {click['y']}) - {click['button']}\n")
        
        self.sequence_text.configure(state="disabled")
    
    def clear_sequence(self):
        """Clear the recorded sequence."""
        self.recorded_clicks = []
        self.sequence_text.configure(state="normal")
        self.sequence_text.delete(1.0, tk.END)
        self.sequence_text.insert(tk.END, "Sequence cleared.")
        self.sequence_text.configure(state="disabled")
        self.play_button.configure(state="disabled")
        self.log_message("Sequence cleared")
    
    
    def toggle_playback(self):
        """Toggle playback on/off."""
        if not self.playing:
            self.start_playback()
        else:
            self.stop_playback()
    
    def start_playback(self):
        """Start playing the recorded sequence."""
        if not self.recorded_clicks:
            messagebox.showerror("Error", "No sequence recorded to play!")
            return
        
        try:
            self.replay_count = int(self.repeat_var.get())
            self.replay_interval = int(self.replay_interval_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for repeat count and interval!")
            return
        
        self.playing = True
        self.current_replay = 0
        self.play_button.configure(text="Stop Playback")
        self.record_button.configure(state="disabled")
        self.clear_button.configure(state="disabled")
        
        self.log_message(f"Starting playback - {self.replay_count} repetitions")
        
        # Start playback thread
        self.recorder_thread = threading.Thread(target=self.playback_thread, daemon=True)
        self.recorder_thread.start()
    
    def stop_playback(self):
        """Stop playing the recorded sequence."""
        self.playing = False
        self.play_button.configure(text="Play Sequence")
        self.record_button.configure(state="normal")
        self.clear_button.configure(state="normal")
        self.playback_status_var.set("Stopped")
        self.progress_var.set("")
        self.log_message("Playback stopped")
    
    def playback_thread(self):
        """Thread function for playing back recorded sequence."""
        for replay in range(self.replay_count):
            if not self.playing:
                break
            
            self.current_replay = replay + 1
            self.root.after(0, lambda: self.playback_status_var.set(f"Playing... ({self.current_replay}/{self.replay_count})"))
            self.root.after(0, lambda: self.progress_var.set(f"Replay {self.current_replay} of {self.replay_count}"))
            
            # Play the sequence
            for i, click in enumerate(self.recorded_clicks):
                if not self.playing:
                    break
                
                # Wait for the timing (if not first click)
                if i > 0:
                    time_diff = click['time'] - self.recorded_clicks[i-1]['time']
                    if time_diff > 0:
                        time.sleep(time_diff)
                
                # Perform the click
                pyautogui.click(click['x'], click['y'])
                self.root.after(0, lambda i=i: self.log_message(f"Playback click {i+1} at ({self.recorded_clicks[i]['x']}, {self.recorded_clicks[i]['y']})"))
            
            # Wait between repetitions (if not last)
            if replay < self.replay_count - 1 and self.replay_interval > 0:
                time.sleep(self.replay_interval)
        
        # Playback finished
        self.root.after(0, self.stop_playback)
        self.root.after(0, lambda: self.log_message("Playback completed"))
    
    def on_closing(self):
        """Handle window closing."""
        self.stop_all()
        if self.recording:
            self.stop_recording()
        if self.playing:
            self.stop_playback()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if hasattr(self, 'click_listener') and self.click_listener:
            self.click_listener.stop()
        self.root.destroy()

def main():
    """Main function."""
    root = tk.Tk()
    app = AutoclickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
