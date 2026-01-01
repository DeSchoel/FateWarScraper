# Fate War Alliance Member Scraper

Extract comprehensive alliance member data from the Fate War game UI using screen capture and multi-language OCR.

## Features

- **Multi-Category Tracking**: Automatically scrapes Power, Kills, Weekly Contribution, Construction, Tribe Assistance, and Gold Donation.
- **Automated Navigation**: Uses OCR to find and click category buttons within the game window.
- **Auto-Scrolling**: Automatically scrolls through the entire member list for each category.
- **International Language Support**: Specialized OCR for English, Korean, Japanese, Chinese (Simplified), Russian, and Vietnamese.
- **Fuzzy Deduplication**: Intelligently merges records from different scans, even with minor OCR noise or name variations.
- **Window Capture**: Captures only the game window (no full-screen screenshot required).
- **Clean Output**: Exports to CSV and a styled, shareable HTML table.

## Requirements

- Python 3.12+
- Windows 10/11
- NVIDIA GPU with CUDA (recommended for fast OCR)

## Installation

```bash
# Clone or download this repository
cd FateWarScraper

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the project in editable mode
pip install -e .
```

## Usage

1. Start the Fate War game.
2. Open the alliance member list ranking screen.
3. Run the scraper:

```bash
# Standard scan (excludes Gold Donation)
python -m fatewarscraper

# Complete scan (includes Gold Donation)
python -m fatewarscraper --gold
```

The scraper will:
1. Find the "Fate War" window.
2. Iterate through all categories (Individual Might, Killing Machine, etc.).
3. For each category:
   - Click the tab.
   - Scroll and capture the entire list.
4. Process all images using EasyOCR.
5. Merge data into a single record per member.
6. Sort by Power (highest to lowest).
7. Export to `outputs/`.

## Output Files

- `outputs/members_YYYY-MM-DD_HH-MM-SS.csv`: Structured data for Excel/Google Sheets.
- `outputs/members_YYYY-MM-DD_HH-MM-SS.html`: A beautiful, shareable HTML table.
- `outputs/parsed_members.txt`: A debug log showing raw OCR readings.
- `outputs/*.png`: Cropped debug images for verification.

## Project Structure

```
FateWarScraper/
├── src/fatewarscraper/
│   ├── __init__.py         # Package metadata
│   ├── __main__.py         # Entry point
│   ├── cli.py              # Main orchestration
│   ├── capture.py          # Window capture
│   ├── preprocess.py       # Image preprocessing
│   ├── ocr.py              # OCR extraction
│   ├── navigation.py       # UI interaction & navigation
│   ├── parse.py            # Data parsing
│   └── export.py           # CSV/HTML export
├── outputs/                # Generated files (gitignored)
├── pyproject.toml          # Project metadata
└── README.md
```

## Legal Notice

This tool performs passive screen reading only. It does NOT:
- Modify game memory
- Inject code into the game process
- Intercept network packets
- Violate the game's terms of service (screen reading is generally permitted)

Always check your game's terms of service before using automation tools.