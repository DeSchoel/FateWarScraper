from PIL import Image
from pathlib import Path
from fatewarscraper.parse import parse_image_by_rows, parse_podium_image

output_dir = Path("outputs")
img_path = output_dir / "crop_tribe_assistance_000.png"
if img_path.exists():
    img = Image.open(img_path)
    records = parse_image_by_rows(img, metric_name="tribe_assistance")
    print(f"Results for {img_path.name}:")
    for r in records:
        print(f"  Name: {r.name} | Asst: {r.tribe_assistance} | Raw: {r.raw_line}")

podium_path = output_dir / "crop_tribe_assistance_podium.png"
if podium_path.exists():
    img = Image.open(podium_path)
    records = parse_podium_image(img, metric_name="tribe_assistance")
    print(f"\nResults for {podium_path.name}:")
    for r in records:
        print(f"  Name: {r.name} | Asst: {r.tribe_assistance} | Raw: {r.raw_line}")
