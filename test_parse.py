"""Test script to validate power-based ranking with mismatch detection."""

from pathlib import Path
from PIL import Image
from fatewarscraper.ocr import configure_tesseract
from fatewarscraper.parse import parse_image_by_rows, parse_podium_image, deduplicate_records, sort_records

def main():
    output_dir = Path("outputs")

    print("=" * 70)
    print("Phase 3: Power-Based Ranking with Mismatch Detection")
    print("=" * 70)

    configure_tesseract()

    all_records = []

    # Process podium first
    podium_file = output_dir / "crop_000_podium.png"
    if podium_file.exists():
        print(f"\nProcessing podium (top 3)...")
        try:
            img = Image.open(podium_file)
            records = parse_podium_image(img)
            all_records.extend(records)
            print(f"  ✓ Extracted {len(records)} members from podium")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Find all regular cropped images
    crop_files = sorted([f for f in output_dir.glob("crop_*.png")
                        if "podium" not in f.name and "regular" not in f.name])

    if crop_files:
        print(f"\nProcessing {len(crop_files)} regular member list images...")

        for crop_file in crop_files:
            print(f"  {crop_file.name}...", end=" ")

            try:
                img = Image.open(crop_file)
                records = parse_image_by_rows(img)
                all_records.extend(records)
                print(f"{len(records)} members")
            except Exception as e:
                print(f"ERROR: {e}")

    print(f"\n✓ Extracted {len(all_records)} total records")

    if len(all_records) == 0:
        print("\n✗ No records extracted!")
        return 1

    # Deduplicate
    print(f"\nRemoving duplicates...")
    unique_records = deduplicate_records(all_records)
    print(f"✓ {len(unique_records)} unique members ({len(all_records) - len(unique_records)} duplicates removed)")

    # Sort by POWER and assign power-based ranks
    print(f"\nSorting by POWER and detecting rank mismatches...")
    sorted_records = sort_records(unique_records)

    mismatches = sum(1 for r in sorted_records if r.rank_mismatch)
    print(f"✓ Found {mismatches} rank mismatches")

    # Display results
    print("\n" + "=" * 70)
    print("Member List (Sorted by POWER):")
    print("=" * 70)
    print(f"{'Rank':<6} {'Name':<20} {'Power':<15} {'Read':<6} {'Status':<10}")
    print("-" * 70)

    display_count = min(50, len(sorted_records))
    for record in sorted_records[:display_count]:
        rank_str = str(record.power_rank) if record.power_rank else "?"
        power_str = f"{record.power:,}" if record.power else "?"
        read_str = str(record.read_rank) if record.read_rank else "?"

        # Status indicator
        if record.rank_mismatch:
            status = "⚠ MISMATCH"
        elif record.read_rank is None:
            status = "No OCR"
        else:
            status = "✓ Match"

        print(f"{rank_str:<6} {record.name:<20} {power_str:<15} {read_str:<6} {status:<10}")

    if len(sorted_records) > display_count:
        print(f"... and {len(sorted_records) - display_count} more")

    # Save to file
    output_file = output_dir / "parsed_members.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Power Rank | Name | Power | Read Rank | Mismatch | Raw Line\n")
        f.write("=" * 120 + "\n")
        for record in sorted_records:
            rank_str = str(record.power_rank) if record.power_rank else "?"
            power_str = str(record.power) if record.power else "?"
            read_str = str(record.read_rank) if record.read_rank else "?"
            mismatch_str = "YES" if record.rank_mismatch else "NO"
            f.write(f"{rank_str:<11} | {record.name:<20} | {power_str:<15} | {read_str:<9} | {mismatch_str:<8} | {record.raw_line}\n")

    print(f"\n✓ Full results saved to {output_file}")

    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    print(f"  Total members: {len(sorted_records)}")
    print(f"  Rank mismatches: {mismatches}")
    print(f"  Members missing read rank: {sum(1 for r in sorted_records if r.read_rank is None)}")

    print("\n" + "=" * 70)
    print("Ranking System:")
    print("=" * 70)
    print("  ✓ Members ranked by POWER (highest to lowest)")
    print("  ✓ 'Read' column shows what OCR detected from image")
    print("  ✓ Mismatches flagged when Read Rank ≠ Power Rank")

    return 0

if __name__ == "__main__":
    exit(main())