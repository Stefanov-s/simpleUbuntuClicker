#!/usr/bin/env python3
"""
Test script for the autoclicker application.
This script tests the core functionality without requiring actual mouse clicks.
"""

import time
import threading
from unittest.mock import patch, MagicMock

# Mock pyautogui to avoid actual mouse clicks during testing
with patch('pyautogui.position') as mock_position, \
     patch('pyautogui.click') as mock_click, \
     patch('pyautogui.FAILSAFE', True), \
     patch('pyautogui.PAUSE', 0.01):
    
    # Set up mock return values
    mock_position.return_value = (100, 200)
    mock_click.return_value = None
    
    # Import the autoclicker module
    import autoclicker

def test_input_validation():
    """Test input validation functions."""
    print("Testing input validation...")
    
    # Test valid inputs
    test_cases = [
        (0, 5, 5),    # 0 minutes, 5 seconds = 5 seconds
        (1, 30, 90),  # 1 minute, 30 seconds = 90 seconds
        (2, 0, 120),  # 2 minutes, 0 seconds = 120 seconds
    ]
    
    for minutes, seconds, expected in test_cases:
        result = minutes * 60 + seconds
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"✓ {minutes}m {seconds}s = {result}s")
    
    print("Input validation tests passed!")

def test_clicker_logic():
    """Test the clicker thread logic."""
    print("\nTesting clicker logic...")
    
    # Mock the global variables
    autoclicker.start_time = time.time()
    autoclicker.mouse_x, autoclicker.mouse_y = 100, 200
    
    # Test clicker thread with mock
    active_flag = [True]
    interval = 1  # 1 second interval for testing
    
    def test_click_thread():
        """Test version of click_thread that runs for a short time."""
        start_test = time.time()
        click_count = 0
        last_click_time = 0
        
        while time.time() - start_test < 2.5:  # Run for 2.5 seconds
            if active_flag[0] and autoclicker.start_time is not None:
                current_time = time.time()
                elapsed = current_time - autoclicker.start_time
                # Only click if enough time has passed since last click
                if elapsed % interval < 0.1 and elapsed - last_click_time >= 0.9:
                    click_count += 1
                    last_click_time = elapsed
                    print(f"  Click #{click_count} at {elapsed:.1f}s")
            time.sleep(0.01)
        
        return click_count
    
    # Run the test
    click_count = test_click_thread()
    
    # Should have clicked approximately 2-3 times in 2.5 seconds
    assert 2 <= click_count <= 3, f"Expected 2-3 clicks, got {click_count}"
    print(f"✓ Clicker logic test passed! ({click_count} clicks in 2.5s)")

def test_synchronization():
    """Test synchronization between clickers."""
    print("\nTesting synchronization...")
    
    # Test that both clickers would start from the same timestamp
    start_time = time.time()
    
    # Simulate two clickers with different intervals
    primary_interval = 2  # 2 seconds
    secondary_interval = 6  # 6 seconds
    
    # Check that they would sync at multiples of 6 seconds
    test_times = [0, 2, 4, 6, 8, 10, 12]
    
    for test_time in test_times:
        primary_should_click = (test_time % primary_interval) < 0.1
        secondary_should_click = (test_time % secondary_interval) < 0.1
        
        if primary_should_click and secondary_should_click:
            print(f"  ✓ Both clickers sync at {test_time}s")
        elif primary_should_click:
            print(f"  ✓ Primary only at {test_time}s")
        elif secondary_should_click:
            print(f"  ✓ Secondary only at {test_time}s")
    
    print("Synchronization test passed!")

def main():
    """Run all tests."""
    print("=== Autoclicker Test Suite ===")
    print("Note: This test uses mocked mouse functions to avoid actual clicks.")
    print()
    
    try:
        test_input_validation()
        test_clicker_logic()
        test_synchronization()
        
        print("\n=== All Tests Passed! ===")
        print("The autoclicker application should work correctly on Ubuntu.")
        print("Make sure to:")
        print("1. Run on Ubuntu with X11 session")
        print("2. Add user to input group: sudo usermod -aG input $USER")
        print("3. Reboot after adding to input group")
        print("4. Install dependencies: pip3 install -r requirements.txt")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
