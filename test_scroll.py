"""Test script for Phase 2: Small scrolls with overlap."""

from pathlib import Path
from fatewarscraper.capture import capture_with_scroll
from fatewarscraper.preprocess import crop_member_list_first, crop_member_list_scrolled

def main():
    # Configuration
    window_title = "Fate War"
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Phase 2: Overlap Scrolling Test")
    print("=" * 60)
    print("\nStrategy:")
    print("  - Small scroll increments (-1 click)")
    print("  - Many captures with overlap")
    print("  - Duplicates removed later during OCR")
    print("\nMake sure:")
    print("  1. Fate War is running")
    print("  2. Alliance member list is open")
    print("  3. You're at the TOP of the list (scroll up manually first!)")
    print("\nStarting in 3 seconds...")

    import time
    time.sleep(3)

    try:
        # Capture with small scrolls
        print(f"\nCapturing with overlap scrolling...")
        captures = capture_with_scroll(
            window_title,
            max_scrolls=50,      # Allow many scrolls
            scroll_amount=-1,    # Small scroll
            scroll_delay=0.4     # Wait for animation
        )

        print(f"\n{'='*60}")
        print(f"Processing {len(captures)} captures...")
        print(f"{'='*60}")

        # Save all full captures for debugging
        print(f"\nSaving full captures...")
        for i, img in enumerate(captures):
            path = output_dir / f"scroll_{i:03d}_full.png"
            img.save(path)
        print(f"  Saved {len(captures)} full captures")

        # Process first screenshot separately (has podium)
        print(f"\nProcessing first screenshot (with podium)...")
        podium, regular_first = crop_member_list_first(captures[0])

        podium_path = output_dir / "crop_000_podium.png"
        podium.save(podium_path)
        print(f"  Saved podium: {podium_path}")

        regular_path = output_dir / "crop_000_regular.png"
        regular_first.save(regular_path)
        print(f"  Saved regular rows: {regular_path}")

        # Process remaining screenshots (scrolled, no podium)
        print(f"\nProcessing scrolled screenshots...")
        for i in range(2, len(captures)):
            cropped = crop_member_list_scrolled(captures[i])
            path = output_dir / f"crop_{i:03d}.png"
            cropped.save(path)
            if i % 10 == 0:
                print(f"  Processed {i}/{len(captures)-1}...")

        print(f"  Saved {len(captures)-1} scrolled crops")

        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"\nResults in outputs/ directory:")
        print(f"  - scroll_XXX_full.png: {len(captures)} full window captures")
        print(f"  - crop_000_podium.png: Top 3 podium")
        print(f"  - crop_000_regular.png: Ranks 4-5 from first screenshot")
        print(f"  - crop_001.png to crop_{len(captures)-1:03d}.png: Scrolled captures")
        print(f"\nNext steps:")
        print(f"  1. Check the cropped images - do they show member rows?")
        print(f"  2. You'll see LOTS of duplicates - that's OK!")
        print(f"  3. OCR will process all and remove duplicates")
        print(f"  4. Ready for Phase 3: OCR + deduplication!")

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())