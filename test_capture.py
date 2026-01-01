"""Test script for Phase 1: Capture the game window."""

from pathlib import Path
from fatewarscraper.capture import capture_game_window, find_window_by_title
import win32gui


def main():
    # Configuration
    window_title = "Fate War"  # Adjust if your window title is different
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Phase 1: Window Capture Test")
    print("=" * 60)
    print(f"\nSearching for window: '{window_title}'...")

    try:
        # First, let's see what window we found
        hwnd = find_window_by_title(window_title)
        if hwnd is None:
            print(f"\n✗ Window not found!")
            return 1

        # Show what we found
        actual_title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        print(f"✓ Found window:")
        print(f"  Title: '{actual_title}'")
        print(f"  Handle: {hwnd}")
        print(f"  Position: ({rect[0]}, {rect[1]}) to ({rect[2]}, {rect[3]})")
        print(f"  Size: {rect[2] - rect[0]}x{rect[3] - rect[1]} pixels")

        # Capture the window
        img = capture_game_window(window_title)

        print(f"\n✓ Window captured successfully!")
        print(f"  Captured size: {img.size[0]}x{img.size[1]} pixels")

        # Save the image
        output_path = output_dir / "test_capture.png"
        img.save(output_path)

        print(f"\n✓ Saved to: {output_path}")
        print(f"\nNext steps:")
        print(f"  1. Open {output_path} and examine the layout")
        print(f"  2. If it's the WRONG window, check the title above")
        print(f"  3. Note where the member list is located")

    except RuntimeError as e:
        print(f"\n✗ Error: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Make sure Fate War is running")
        print(f"  - Check the exact window title (case doesn't matter)")
        print(f"  - Try adjusting 'window_title' in this script")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())