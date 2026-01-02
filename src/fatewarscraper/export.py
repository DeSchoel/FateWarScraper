from __future__ import annotations
from pathlib import Path
from datetime import datetime
import csv
import json
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


def write_member_json(records: list[MemberRecord], out_dir: Path, filename: str = None) -> Path:
    """Write structured member records to JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = f"members_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    path = out_dir / filename
    
    data = [rec.__dict__ for rec in records]
    
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
            
    return path


def update_history_json(records: list[MemberRecord], out_dir: Path) -> Path:
    """Update history.json with current scan results."""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "history.json"
    
    timestamp = datetime.now().isoformat()
    snapshot = {
        "timestamp": timestamp,
        "members": [rec.__dict__ for rec in records]
    }
    
    history = []
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except Exception:
            history = []
            
    history.append(snapshot)
    
    # Keep last 50 scans to avoid massive files (roughly 6 months at 2/week)
    if len(history) > 50:
        history = history[-50:]
        
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        
    return path


def write_member_html(records: list[MemberRecord], out_dir: Path, filename: str = None) -> Path:
    """Write structured member records to a shareable HTML page."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = f"members_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
    path = out_dir / filename
    
    headers = [
        "Rank", "Name", "Power", "Kills", "Weekly Contrib", 
        "Construction", "Assistance", "Gold Donation"
    ]
    
    table_headers = "".join(f"<th>{h}</th>" for h in headers)
    
    rows = []
    for rec in records:
        # Escape name for both HTML display and data attribute
        escaped_name = escape_html(rec.name)
        # Use an <a> tag to make it clearly clickable and improve accessibility
        name_html = f'<a href="#" class="member-link" data-name="{escaped_name}" onclick="return false;">{escaped_name}</a>'
        row = f"""
        <tr>
            <td>{rec.rank or ''}</td>
            <td class="member-name-cell">
                <strong>{name_html}</strong>
            </td>
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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Fate War Alliance Tracking</title>
    <!-- jQuery and DataTables CSS/JS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #1c1e21; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: #1877f2; color: white; padding: 20px; border-radius: 8px 8px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ margin: 0; font-size: 24px; }}
        .summary {{ background: white; padding: 15px; border-bottom: 1px solid #ddd; display: flex; gap: 20px; font-size: 14px; color: #606770; }}
        .table-container {{ background: white; padding: 20px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow-x: auto; }}
        table.dataTable {{ border-collapse: collapse !important; width: 100% !important; }}
        table.dataTable thead th {{ background-color: #f0f2f5; color: #4b4f56; border-bottom: 2px solid #ddd !important; padding: 12px; }}
        table.dataTable tbody td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        
        /* Clickable Name Styles */
        .member-link {{ 
            color: #1877f2; 
            text-decoration: underline; 
            cursor: pointer;
            font-weight: bold;
        }}
        .member-link:hover {{
            color: #166fe5;
            text-decoration: none;
        }}
        
        .footer {{ margin-top: 20px; text-align: center; font-size: 12px; color: #90949c; }}
        
        /* Modal Styles */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }}
        .modal-content {{ background-color: white; margin: 5% auto; padding: 20px; border-radius: 8px; width: 80%; max-width: 900px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }}
        .close {{ font-size: 28px; font-weight: bold; cursor: pointer; color: #606770; }}
        .close:hover {{ color: #1c1e21; }}
        #chartContainer {{ position: relative; height: 400px; width: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Fate War Alliance Tracking</h1>
        </header>
        <div class="summary">
            <div><strong>Total Members:</strong> {len(records)}</div>
            <div><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="table-container">
            <table id="membersTable" class="display">
                <thead>
                    <tr>{table_headers}</tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        <div class="footer">
            Generated by FateWarScraper
        </div>
    </div>

    <!-- Modal for Graph -->
    <div id="graphModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalMemberName">Member Progress</h2>
                <span class="close">&times;</span>
            </div>
            <div id="chartContainer">
                <canvas id="progressChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let historyData = [];
        let myChart = null;

        $(document).ready(function() {{
            // Initialize DataTable
            const table = $('#membersTable').DataTable({{
                "pageLength": 50,
                "order": [[ 0, "asc" ]],
                "responsive": true,
                "language": {{ "search": "Search Member:" }}
            }});

            // Load history.json
            fetch('history.json')
                .then(response => response.json())
                .then(data => {{
                    historyData = data;
                    console.log("History loaded:", historyData.length, "snapshots");
                }})
                .catch(err => console.error('Could not load history:', err));

            // Handle name clicks (delegated for DataTables compatibility)
            // Using a more specific selector and binding to the document or table body
            $(document).on('click', '.member-link', function(e) {{
                e.preventDefault();
                const name = $(this).attr('data-name');
                console.log("Clicked member:", name);
                if (name) {{
                    showGraph(name);
                }}
                return false;
            }});

            // Modal Close
            $('.close').click(function() {{
                $('#graphModal').hide();
            }});
            $(window).click(function(event) {{
                if (event.target == document.getElementById('graphModal')) {{
                    $('#graphModal').hide();
                }}
            }});
        }});

        function showGraph(memberName) {{
            $('#modalMemberName').text(memberName + "'s Power Progress");
            $('#graphModal').show();

            const labels = [];
            const powerData = [];

            historyData.forEach(snapshot => {{
                const member = snapshot.members.find(m => m.name === memberName);
                if (member && member.power) {{
                    const date = new Date(snapshot.timestamp).toLocaleDateString();
                    labels.push(date);
                    powerData.push(member.power);
                }}
            }});

            if (powerData.length === 0) {{
                alert('No progress data found for ' + memberName + '. Please wait for more scans to be completed.');
                return;
            }}

            if (myChart) {{
                myChart.destroy();
            }}

            const ctx = document.getElementById('progressChart').getContext('2d');
            myChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Power',
                        data: powerData,
                        borderColor: '#1877f2',
                        backgroundColor: 'rgba(24, 119, 242, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            ticks: {{
                                callback: function(value) {{
                                    return value.toLocaleString();
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return 'Power: ' + context.parsed.y.toLocaleString();
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
    </script>
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
