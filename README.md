# FateWarScraper

A Python OCR tool that captures the Fate War (Steam) UI and extracts alliance member ranking data
(e.g., name / power / helps) from what’s visible on screen, exporting to CSV + HTML.

## What this project does
- Takes a screenshot of the game (no memory reading, no packet sniffing)
- Crops the alliance member list area (configurable)
- Runs OCR (Tesseract) to extract text
- Converts OCR output into structured data
- Exports results:
  - CSV (for Excel / Google Sheets)
  - HTML (a small shareable “website”)

## Requirements
- Windows 10/11
- Python 3.12
- Tesseract OCR installed

## Setup (quick)
1. Create and activate venv
2. Install deps
3. Install this package in editable mode

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
