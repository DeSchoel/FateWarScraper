from pathlib import Path

from .capture import capture_window
from .ocr import image_to_text
from .export import write_csv, write_html


def run(out_dir: Path = Path("outputs")) -> None:
    print("Capturing Fate War window...")
    img = capture_window("Fate War")  # adjust if the window title differs

    out_dir.mkdir(parents=True, exist_ok=True)

    debug_path = out_dir / "debug_full.png"
    img.save(debug_path)
    print(f"Saved screenshot: {debug_path.resolve()}")

    print("Running OCR...")
    text = image_to_text(img)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    csv_path = write_csv(lines, out_dir)
    html_path = write_html(lines, out_dir)

    print(f"Wrote CSV:  {csv_path.resolve()}")
    print(f"Wrote HTML: {html_path.resolve()}")
    print("Done.")
