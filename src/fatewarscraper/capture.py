from __future__ import annotations

import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

import mss
from PIL import Image

user32 = ctypes.WinDLL("user32", use_last_error=True)

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]


def _get_window_title(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def find_window_by_title_substring(title_substring: str) -> Optional[int]:
    """
    Returns window handle (HWND) of the first visible window whose title contains title_substring.
    Case-insensitive.
    """
    title_substring = title_substring.lower()
    found_hwnd = {"hwnd": None}

    def callback(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _get_window_title(hwnd)
        if title and title_substring in title.lower():
            found_hwnd["hwnd"] = hwnd
            return False  # stop enumeration
        return True

    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return found_hwnd["hwnd"]


def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise OSError("GetWindowRect failed")
    return rect.left, rect.top, rect.right, rect.bottom


def capture_window(title_substring: str, bring_to_front: bool = True) -> Image.Image:
    """
    Capture a screenshot of the window whose title contains title_substring.
    """
    hwnd = find_window_by_title_substring(title_substring)
    if hwnd is None:
        raise RuntimeError(
            f"Could not find a visible window containing title: '{title_substring}'. "
            f"Make sure the game is running in WINDOWED mode and its title contains that text."
        )

    if bring_to_front:
        user32.SetForegroundWindow(hwnd)

    left, top, right, bottom = get_window_rect(hwnd)
    width = max(0, right - left)
    height = max(0, bottom - top)
    if width == 0 or height == 0:
        raise RuntimeError("Window has zero size (is it minimized?)")

    with mss.mss() as sct:
        region = {"left": left, "top": top, "width": width, "height": height}
        shot = sct.grab(region)
        return Image.frombytes("RGB", shot.size, shot.rgb)
