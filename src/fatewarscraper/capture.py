"""Window capture functionality for Fate War game."""

import sys
import time
from typing import Optional

from PIL import Image

if sys.platform == "win32":
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll


def find_window_by_title(title: str) -> Optional[int]:
    """Find a window handle by EXACT title match.

    Args:
        title: Exact window title to search for

    Returns:
        Window handle (HWND) if found, None otherwise
    """
    if sys.platform != "win32":
        raise RuntimeError("Window capture is only supported on Windows")

    result = None

    def enum_callback(current_hwnd: int, lparam: int) -> bool:
        nonlocal result
        if win32gui.IsWindowVisible(current_hwnd):
            window_text = win32gui.GetWindowText(current_hwnd)
            if window_text == title:  # EXACT match only
                result = current_hwnd
                return False  # Stop searching
        return True

    try:
        win32gui.EnumWindows(enum_callback, 0)
    except Exception:
        pass

    return result


def capture_window(hwnd: int) -> Image.Image:
    """Capture a window by its handle and return as PIL Image.

    Args:
        hwnd: Window handle to capture

    Returns:
        PIL Image of the window contents

    Raises:
        RuntimeError: If capture fails
    """
    if sys.platform != "win32":
        raise RuntimeError("Window capture is only supported on Windows")

    try:
        # Get window dimensions (client area only, not including title bar)
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bottom - top

        # Get device contexts
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # Create bitmap
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)

        # Try PrintWindow first (works better for some windows)
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

        # If PrintWindow fails, try BitBlt
        if result == 0:
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

        # Convert to PIL Image
        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr,
            'raw',
            'BGRX',
            0,
            1
        )

        # Cleanup
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        return img

    except Exception as e:
        raise RuntimeError(f"Failed to capture window: {e}") from e


def capture_game_window(window_title: str) -> Image.Image:
    """Find and capture the game window by EXACT title match.

    Args:
        window_title: Exact title of the game window to capture

    Returns:
        PIL Image of the game window

    Raises:
        RuntimeError: If window is not found or capture fails
    """
    hwnd = find_window_by_title(window_title)
    if hwnd is None:
        raise RuntimeError(
            f"Window with exact title '{window_title}' not found. "
            f"Make sure the game is running and visible."
        )

    return capture_window(hwnd)


def scroll_window(hwnd: int, scroll_amount: int = -1) -> None:
    """Scroll a window using mouse wheel.

    Sends scroll events to the center of the member list region.

    Args:
        hwnd: Window handle to scroll
        scroll_amount: Scroll amount (negative = scroll down, positive = scroll up).
                       Each unit is approximately 120 (one wheel "click")
                       Use -1 for small scrolls with overlap

    Raises:
        RuntimeError: If scrolling fails
    """
    if sys.platform != "win32":
        raise RuntimeError("Window scrolling is only supported on Windows")

    try:
        # Get window position
        rect = win32gui.GetWindowRect(hwnd)
        window_x = rect[0]
        window_y = rect[1]

        # Member list center (relative to window CLIENT area)
        # Approximate center of visible member list
        list_center_x = 700
        list_center_y = 400

        # Absolute screen coordinates
        screen_x = window_x + list_center_x
        screen_y = window_y + list_center_y

        # Bring window to foreground
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            # Sometimes SetForegroundWindow fails if we don't own the process
            # or if it's already in the foreground. Often ignorable.
            pass
        time.sleep(0.1)

        # Move mouse to center of list
        windll.user32.SetCursorPos(screen_x, screen_y)
        time.sleep(0.05)

        # Send mouse wheel scroll
        # MOUSEEVENTF_WHEEL = 0x0800
        windll.user32.mouse_event(0x0800, 0, 0, scroll_amount * 120, 0)

        time.sleep(0.15)  # Wait for scroll animation

    except Exception as e:
        raise RuntimeError(f"Failed to scroll window: {e}") from e


def images_are_similar(img1: Image.Image, img2: Image.Image, threshold: float = 0.98) -> bool:
    """Check if two images are similar (to detect if scrolling reached the end).

    Only compares the BOTTOM portion of images to detect if new content appeared.

    Args:
        img1: First image
        img2: Second image
        threshold: Similarity threshold (0.0 to 1.0). Default 0.98 = 98% similar

    Returns:
        True if images are similar (likely at bottom of list), False otherwise
    """
    if img1.size != img2.size:
        return False

    # Convert to same mode for comparison
    if img1.mode != img2.mode:
        img2 = img2.convert(img1.mode)

    # Only compare bottom 30% of image
    height = img1.size[1]
    bottom_start = int(height * 0.7)

    img1_bottom = img1.crop((0, bottom_start, img1.size[0], height))
    img2_bottom = img2.crop((0, bottom_start, img2.size[0], height))

    # Pixel comparison
    import numpy as np
    arr1 = np.array(img1_bottom)
    arr2 = np.array(img2_bottom)

    identical = np.sum(arr1 == arr2)
    total = arr1.size
    similarity = identical / total

    return similarity >= threshold


def capture_with_scroll(
    window_title: str,
    max_scrolls: int = 50,
    scroll_amount: int = -1,
    scroll_delay: float = 0.4
) -> list[Image.Image]:
    """Capture multiple screenshots while scrolling down the member list.

    Strategy for handling inconsistent scroll distances:
    - Use SMALL scroll amounts (-1) to create overlap
    - Capture MANY screenshots
    - Skip duplicate images at the end

    Args:
        window_title: Exact title of game window
        max_scrolls: Maximum number of scroll attempts (default 50)
        scroll_amount: Scroll clicks per iteration (default -1 for small overlap)
        scroll_delay: Seconds to wait after scroll (default 0.4)

    Returns:
        List of captured images (unique screenshots with overlap)

    Raises:
        RuntimeError: If window not found or capture fails
    """
    hwnd = find_window_by_title(window_title)
    if hwnd is None:
        raise RuntimeError(
            f"Window with exact title '{window_title}' not found. "
            f"Make sure the game is running and visible."
        )

    captures = []
    consecutive_similar = 0

    # First capture (includes podium)
    print("Capturing initial screenshot...")
    img = capture_window(hwnd)
    captures.append(img)

    # Scroll and capture until bottom
    for i in range(max_scrolls):
        print(f"Scroll {i+1}/{max_scrolls}...", end=" ")

        # Scroll down
        scroll_window(hwnd, scroll_amount)
        time.sleep(scroll_delay)

        # Capture
        img_new = capture_window(hwnd)

        # Check if we've reached the bottom
        # Require 3 consecutive similar images to confirm
        if images_are_similar(img, img_new, threshold=0.98):
            consecutive_similar += 1
            print(f"(similar #{consecutive_similar})")
            if consecutive_similar >= 3:
                print(f"\nReached bottom (3 consecutive similar images)")
                break
            # Don't add similar images to avoid duplicates at the end
        else:
            consecutive_similar = 0
            print("(new content)")
            # Only add to captures if it's different
            captures.append(img_new)

        # Always update img for next comparison
        img = img_new

    print(f"\n✓ Captured {len(captures)} unique screenshots")
    return captures