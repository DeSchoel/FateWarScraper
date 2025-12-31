from __future__ import annotations
from pathlib import Path
from datetime import datetime
import csv


def write_csv(lines: list[str], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"alliance_raw_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["RawText"])
        for line in lines:
            w.writerow([line])
    return path


def write_html(lines: list[str], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"alliance_raw_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
    rows = "\n".join(f"<tr><td>{escape_html(line)}</td></tr>" for line in lines)
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Alliance OCR</title></head>
<body>
<table border="1">
{rows}
</table>
</body></html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def escape_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))
