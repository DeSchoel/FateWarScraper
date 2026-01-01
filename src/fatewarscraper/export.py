from __future__ import annotations
from pathlib import Path
from datetime import datetime
import csv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parse import MemberRecord


def write_member_csv(records: list[MemberRecord], out_dir: Path) -> Path:
    """Write structured member records to CSV."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"members_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    
    fields = [
        "rank", "name", "power", "kills", "weekly_contribution", 
        "construction", "tribe_assistance", "gold_donation", 
        "read_rank", "is_valid"
    ]
    
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for rec in records:
            w.writerow(rec.__dict__)
            
    return path


def write_member_html(records: list[MemberRecord], out_dir: Path) -> Path:
    """Write structured member records to a shareable HTML page."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"members_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
    
    headers = [
        "Rank", "Name", "Power", "Kills", "Weekly Contrib", 
        "Construction", "Assistance", "Gold Donation"
    ]
    
    table_headers = "".join(f"<th>{h}</th>" for h in headers)
    
    rows = []
    for rec in records:
        row = f"""
        <tr>
            <td>{rec.rank or ''}</td>
            <td><strong>{escape_html(rec.name)}</strong></td>
            <td>{rec.power or 0:,}</td>
            <td>{rec.kills or 0:,}</td>
            <td>{rec.weekly_contribution or 0:,}</td>
            <td>{rec.construction or 0:,}</td>
            <td>{rec.tribe_assistance or 0:,}</td>
            <td>{rec.gold_donation or 0:,}</td>
        </tr>
        """
        rows.append(row)
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Alliance Member Tracking</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #f4f4f9; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4CAF50; color: white; sticky: top; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .summary {{ margin-bottom: 20px; padding: 15px; background: white; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Alliance Member Tracking</h1>
    <div class="summary">
        <p><strong>Total Members:</strong> {len(records)}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <table>
        <thead>
            <tr>{table_headers}</tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def write_csv(lines: list[str], out_dir: Path) -> Path:
    """Legacy raw text export."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"alliance_raw_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["RawText"])
        for line in lines:
            w.writerow([line])
    return path


def write_html(lines: list[str], out_dir: Path) -> Path:
    """Legacy raw text export."""
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
