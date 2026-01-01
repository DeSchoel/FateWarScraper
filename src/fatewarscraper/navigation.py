"""Navigation and interaction with the Fate War game UI."""

import time
import sys
from typing import Optional, Tuple
from PIL import Image
import numpy as np

if sys.platform == "win32":
    import win32gui
    import win32api
    import win32con
    from ctypes import windll

from .capture import capture_window, find_window_by_title
from .ocr import get_reader


def find_text_coordinates(hwnd: int, target_text: str) -> Optional[Tuple[int, int]]:
    """Find the center coordinates of a specific text within the window.
    
    Args:
        hwnd: Window handle
        target_text: Text to search for
        
    Returns:
        (x, y) coordinates relative to the window client area, or None if not found
    """
    img = capture_window(hwnd)
    reader = get_reader(['en'])
    img_array = np.array(img)
    
    results = reader.readtext(img_array)
    
    # Simple fuzzy matching for the button labels
    target_clean = target_text.lower().replace(" ", "")
    
    # Sort results by confidence to find the best match
    results.sort(key=lambda x: x[2], reverse=True)
    
    # Try exact match first
    for bbox, text, conf in results:
        text_clean = text.lower().replace(" ", "")
        if target_clean == text_clean:
            center_x = int(sum(p[0] for p in bbox) / 4)
            center_y = int(sum(p[1] for p in bbox) / 4)
            print(f"Found exact match for '{target_text}' at ({center_x}, {center_y}) with confidence {conf:.2f}")
            return center_x, center_y

    # Fallback to fuzzy matching
    for bbox, text, conf in results:
        text_clean = text.lower().replace(" ", "")
        if target_clean in text_clean or text_clean in target_clean:
            # Calculate center of the bounding box
            # bbox is [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            center_x = int(sum(p[0] for p in bbox) / 4)
            center_y = int(sum(p[1] for p in bbox) / 4)
            print(f"Found fuzzy match for '{target_text}' in '{text}' at ({center_x}, {center_y}) with confidence {conf:.2f}")
            return center_x, center_y
            
    return None


def click_at(hwnd: int, x: int, y: int) -> None:
    """Click at specific coordinates relative to window client area."""
    rect = win32gui.GetWindowRect(hwnd)
    window_x = rect[0]
    window_y = rect[1]
    
    screen_x = window_x + x
    screen_y = window_y + y
    
    # Bring to foreground
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.1)
    
    # Move and click
    windll.user32.SetCursorPos(screen_x, screen_y)
    time.sleep(0.1)
    
    # Send left click
    # MOUSEEVENTF_LEFTDOWN = 0x0002
    # MOUSEEVENTF_LEFTUP = 0x0004
    windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.5) # Wait for UI to update


def select_category(window_title: str, category_name: str) -> bool:
    """Find and click a category button in the game window.
    
    Args:
        window_title: Title of the game window
        category_name: Name of the category to select
        
    Returns:
        True if successful, False otherwise
    """
    hwnd = find_window_by_title(window_title)
    if not hwnd:
        print(f"Error: Window '{window_title}' not found.")
        return False
        
    print(f"Selecting category: {category_name}...")
    coords = find_text_coordinates(hwnd, category_name)
    
    if coords:
        click_at(hwnd, coords[0], coords[1])
        return True
    else:
        print(f"Warning: Could not find button for '{category_name}'")
        return False
