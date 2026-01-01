"""Helper script to find the exact window title for Fate War."""

import win32gui


def list_all_windows():
    """List all visible window titles."""
    windows = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Only show windows with titles
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(enum_callback, 0)
    return windows


def main():
    print("=" * 60)
    print("All Visible Windows")
    print("=" * 60)
    print("\nLooking for windows with titles...\n")

    windows = list_all_windows()

    for hwnd, title in sorted(windows, key=lambda x: x[1].lower()):
        print(f"  {title}")

    print(f"\n{'=' * 60}")
    print(f"Total: {len(windows)} windows")
    print("=" * 60)
    print("\nInstructions:")
    print("  1. Find 'Fate War' in the list above")
    print("  2. Copy the EXACT title")
    print("  3. Update window_title in test_capture.py")
    print("\nNote: Make sure the Fate War game is running!")


if __name__ == "__main__":
    main()