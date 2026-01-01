"""Debug script to visualize preprocessing."""

from pathlib import Path
from PIL import Image
from fatewarscraper.preprocess import preprocess_for_ocr


def main():
    output_dir = Path("outputs")
    debug_dir = output_dir / "debug_preprocessing"
    debug_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Preprocessing Debug - Saving Preprocessed Images")
    print("=" * 60)

    # Find first regular crop
    crop_files = sorted([f for f in output_dir.glob("crop_*.png")
                         if "podium" not in f.name and "regular" not in f.name])

    if not crop_files:
        print("No crop files found!")
        return 1

    # Take first crop
    test_file = crop_files[0]
    print(f"\nProcessing: {test_file.name}")

    img = Image.open(test_file)

    # Extract first row
    row_height = 80
    row_top = 0
    row_bottom = row_top + row_height

    # Crop each field
    rank_crop = img.crop((0, row_top, 66, row_bottom))
    name_crop = img.crop((159, row_top, 363, row_bottom))
    power_crop = img.crop((763, row_top, 941, row_bottom))

    # Save original crops
    rank_crop.save(debug_dir / "1_rank_original.png")
    name_crop.save(debug_dir / "2_name_original.png")
    power_crop.save(debug_dir / "3_power_original.png")

    # Preprocess
    rank_processed = preprocess_for_ocr(rank_crop)
    name_processed = preprocess_for_ocr(name_crop)
    power_processed = preprocess_for_ocr(power_crop)

    # Save preprocessed
    rank_processed.save(debug_dir / "4_rank_processed.png")
    name_processed.save(debug_dir / "5_name_processed.png")
    power_processed.save(debug_dir / "6_power_processed.png")

    print(f"\n✓ Saved debug images to: {debug_dir}")
    print(f"\nCheck these files:")
    print(f"  - 1-3: Original crops")
    print(f"  - 4-6: After preprocessing (grayscale, contrast, threshold)")
    print(f"\nThe processed images should have:")
    print(f"  - Black text on white background")
    print(f"  - High contrast")
    print(f"  - No gray areas")
    print(f"\nIf the text is unclear, we need to adjust the preprocessing!")

    return 0


if __name__ == "__main__":
    exit(main())