"""Visual debug - draw boxes on image to show crop regions."""

from pathlib import Path
from PIL import Image, ImageDraw


def main():
    output_dir = Path("outputs")

    # Find first regular crop
    crop_files = sorted([f for f in output_dir.glob("crop_*.png")
                         if "podium" not in f.name and "regular" not in f.name])

    if not crop_files:
        print("No crop files found!")
        return 1

    test_file = crop_files[0]
    print(f"Drawing crop regions on: {test_file.name}")

    img = Image.open(test_file)
    draw = ImageDraw.Draw(img)

    # Draw boxes for first 3 rows
    for row_num in range(3):
        row_top = row_num * 90
        row_bottom = row_top + 80

        # Rank box (RED)
        draw.rectangle([(0, row_top), (66, row_bottom)], outline='red', width=3)
        draw.text((5, row_top + 5), f"R{row_num + 1}", fill='red')

        # Name box (GREEN)
        draw.rectangle([(159, row_top), (363, row_bottom)], outline='green', width=3)
        draw.text((165, row_top + 5), f"N{row_num + 1}", fill='green')

        # Power box (BLUE)
        draw.rectangle([(763, row_top), (941, row_bottom)], outline='blue', width=3)
        draw.text((770, row_top + 5), f"P{row_num + 1}", fill='blue')

    # Save
    debug_dir = output_dir / "debug_coords"
    debug_dir.mkdir(exist_ok=True)
    output_path = debug_dir / "crop_with_boxes.png"
    img.save(output_path)

    print(f"\n✓ Saved visual debug to: {output_path}")
    print("\nOpen this image and check:")
    print("  RED boxes = Rank field")
    print("  GREEN boxes = Name field")
    print("  BLUE boxes = Power field")
    print("\nAre the boxes around the correct text?")

    return 0


if __name__ == "__main__":
    exit(main())