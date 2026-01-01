"""Test script for Phase 3: OCR examination."""

from pathlib import Path
from fatewarscraper.ocr import configure_tesseract, ocr_image_file


def main():
    # Configuration
    output_dir = Path("outputs")

    print("=" * 60)
    print("Phase 3: OCR Test")
    print("=" * 60)
    print("\nConfiguring Tesseract...")
    configure_tesseract()

    # Find all cropped images
    crop_files = sorted(output_dir.glob("crop_*.png"))

    if not crop_files:
        print("\n✗ No cropped images found!")
        print("  Run test_scroll.py first to generate crops.")
        return 1

    print(f"\nFound {len(crop_files)} cropped images")
    print("\nRunning OCR on first 5 images for testing...")
    print("=" * 60)

    # Test OCR on first few images
    for i, crop_file in enumerate(crop_files[:5]):
        print(f"\n[{crop_file.name}]")
        print("-" * 60)

        try:
            lines = ocr_image_file(crop_file)

            if lines:
                for j, line in enumerate(lines, 1):
                    print(f"  {j}: {line}")
            else:
                print("  (no text detected)")

        except Exception as e:
            print(f"  ERROR: {e}")

    # Save full OCR output to file
    print("\n" + "=" * 60)
    print("Saving full OCR output to ocr_test.txt...")

    output_file = output_dir / "ocr_test.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for crop_file in crop_files:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"{crop_file.name}\n")
            f.write(f"{'=' * 60}\n")

            try:
                lines = ocr_image_file(crop_file)
                for line in lines:
                    f.write(f"{line}\n")
            except Exception as e:
                f.write(f"ERROR: {e}\n")

    print(f"✓ Saved to {output_file}")
    print("\n" + "=" * 60)
    print("Next steps:")
    print("=" * 60)
    print(f"1. Open {output_file}")
    print(f"2. Examine the OCR output format")
    print(f"3. Share 10-20 sample lines with me")
    print(f"4. I'll design the parser based on actual data!")

    return 0


if __name__ == "__main__":
    exit(main())