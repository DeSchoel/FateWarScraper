"""Test script to validate power-based ranking with mismatch detection."""

from pathlib import Path
from PIL import Image
from fatewarscraper.ocr import configure_tesseract
from fatewarscraper.parse import parse_image_by_rows, parse_podium_image, deduplicate_records, sort_records
from fatewarscraper.export import write_member_csv, write_member_html

def get_metric_from_filename(filename: str) -> str:
    """Guess metric type from filename.
    Example: crop_kills_001.png -> kills
    Default: power
    """
    filename = filename.lower()
    if "kills" in filename: return "kills"
    if "weekly" in filename or "contribution" in filename: return "weekly_contribution"
    if "construction" in filename: return "construction"
    if "assistance" in filename: return "tribe_assistance"
    if "gold" in filename or "donation" in filename: return "gold_donation"
    return "power"

def main():
    output_dir = Path("outputs")

    print("=" * 70)
    print("Phase 4: Multi-Metric Member Tracking")
    print("=" * 70)

    configure_tesseract()

    all_records = []

    # Find all cropped images
    all_files = sorted(list(output_dir.glob("crop_*.png")))
    
    if not all_files:
        print("\n✗ No crop files found in outputs/!")
        return 1

    print(f"\nProcessing {len(all_files)} member list images...")

    for crop_file in all_files:
        metric = get_metric_from_filename(crop_file.name)
        print(f"  {crop_file.name} (Metric: {metric})...", end=" ")

        try:
            img = Image.open(crop_file)
            if "podium" in crop_file.name:
                records = parse_podium_image(img, metric_name=metric)
            else:
                records = parse_image_by_rows(img, metric_name=metric)
            
            all_records.extend(records)
            print(f"{len(records)} members")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\n✓ Extracted {len(all_records)} total records")

    if len(all_records) == 0:
        print("\n✗ No records extracted!")
        return 1

    # Deduplicate and merge metrics
    print(f"\nMerging records and deduplicating...")
    unique_records = deduplicate_records(all_records)
    print(f"✓ {len(unique_records)} unique members identified")

    # Sort by POWER and assign power-based ranks
    # (Power remains the primary ranking metric unless changed)
    print(f"\nSorting by POWER and calculating ranks...")
    sorted_records = sort_records(unique_records)
    
    # Identify records with confirmed vs missing read ranks
    ranked_records = [r for r in sorted_records if r.read_rank is not None]
    unranked_records = [r for r in sorted_records if r.read_rank is None]

    # Display results
    from fatewarscraper.parse import generate_text_report
    print("\n" + generate_text_report(sorted_records[:50], include_raw=False))

    if len(sorted_records) > 50:
        print(f"... and {len(sorted_records) - 50} more")
    
    # Save structured reports
    csv_path = write_member_csv(sorted_records, output_dir)
    html_path = write_member_html(sorted_records, output_dir)
    
    # Save debug txt
    output_file = output_dir / "parsed_members.txt"
    report_content = generate_text_report(sorted_records)
    output_file.write_text(report_content, encoding="utf-8-sig")

    print(f"\n✓ CSV report saved:  {csv_path}")
    print(f"✓ HTML report saved: {html_path}")
    print(f"✓ Debug log saved:   {output_file}")

    return 0

if __name__ == "__main__":
    exit(main())