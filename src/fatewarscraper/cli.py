import time
from pathlib import Path
from PIL import Image

from .capture import capture_window, capture_with_scroll
from .navigation import select_category
from .preprocess import crop_member_list_first, crop_member_list_scrolled
from .parse import (
    parse_podium_image, 
    parse_image_by_rows, 
    deduplicate_records, 
    sort_records
)
from .export import write_member_csv, write_member_html, write_member_json, update_history_json


def run(out_dir: Path = Path("outputs"), window_title: str = "Fate War", include_gold: bool = False) -> None:
    """Run the full multi-category alliance member scraper."""
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Define categories and their internal metric names
    categories = [
        ("Individual Might", "power"),
        ("Killing Machine", "kills"),
        ("Weekly Contribution", "weekly_contribution"),
        ("Construction Master", "construction"),
        ("Tribe Assistance", "tribe_assistance"),
    ]
    
    # Gold tracking is disabled per user request
    # if include_gold:
    #     categories.append(("Gold Donation", "gold_donation"))
    
    all_extracted_records = []
    
    print(f"Starting Fate War Scraper on window '{window_title}'")
    print("=" * 60)
    
    for display_name, metric_name in categories:
        print(f"\n>>> Processing Category: {display_name}")
        
        # Cleanup old crops for this metric to avoid confusion
        for p in out_dir.glob(f"crop_{metric_name}_*.png"):
            try: p.unlink()
            except: pass
        
        # 1. Navigate to category
        success = select_category(window_title, display_name)
        if not success:
            print(f"Skipping {display_name} due to navigation failure.")
            continue
            
        # Wait for UI transition
        time.sleep(1.0)
        
        # 2. Capture all screenshots via scrolling
        captures = capture_with_scroll(window_title, max_scrolls=30)
        
        # 3. Process captures for this metric
        category_records = []
        for i, full_img in enumerate(captures):
            print(f"  Parsing screenshot {i+1}/{len(captures)} for {metric_name}...", end=" ")
            
            try:
                if i == 0:
                    # First screenshot has podium + regular rows
                    podium, regular = crop_member_list_first(full_img)
                    
                    # Save crops for debugging/verification
                    podium.save(out_dir / f"crop_{metric_name}_podium.png")
                    regular.save(out_dir / f"crop_{metric_name}_000.png")
                    
                    # Parse
                    category_records.extend(parse_podium_image(podium, metric_name=metric_name))
                    category_records.extend(parse_image_by_rows(regular, metric_name=metric_name))
                elif i == 1:
                    # Skip the first scrolled image (001) as it often overlaps significantly
                    # with the initial regular crop (000) and podium.
                    print(f"Skipping (redundant podium overlap)")
                    continue
                else:
                    # Subsequent screenshots are just lists
                    cropped = crop_member_list_scrolled(full_img)
                    cropped.save(out_dir / f"crop_{metric_name}_{i:03d}.png")
                    
                    category_records.extend(parse_image_by_rows(cropped, metric_name=metric_name))
                
                print(f"OK")
            except Exception as e:
                print(f"FAILED: {e}")
        
        print(f"  Extracted {len(category_records)} records for {display_name}")
        all_extracted_records.extend(category_records)
    
    if not all_extracted_records:
        print("\nError: No records were extracted. Check window title and visibility.")
        return

    # 4. Deduplicate and merge all metrics
    print("\nMerging all categories and deduplicating...")
    unique_records = deduplicate_records(all_extracted_records)
    print(f"✓ {len(unique_records)} unique members identified")

    # 5. Sort by POWER (requested by user) and assign ranks
    print("\nFinalizing sorting by Power...")
    sorted_records = sort_records(unique_records)
    
    # 6. Export results
    csv_path = write_member_csv(sorted_records, out_dir)
    html_path = write_member_html(sorted_records, out_dir)
    json_path = write_member_json(sorted_records, out_dir)
    history_path = update_history_json(sorted_records, out_dir)
    
    # Also create 'static' versions for hosting (always latest)
    write_member_html(sorted_records, out_dir, filename="index.html")
    write_member_json(sorted_records, out_dir, filename="members.json")
    
    # Save a clean text summary for debug
    txt_path = out_dir / "parsed_members.txt"
    from .parse import generate_text_report
    
    report_content = generate_text_report(sorted_records)
    txt_path.write_text(report_content, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print(f"SUCCESS: Scraping complete!")
    print(f"Wrote CSV:  {csv_path.resolve()}")
    print(f"Wrote HTML: {html_path.resolve()}")
    print(f"Wrote Log:  {txt_path.resolve()}")
    print("=" * 60)
