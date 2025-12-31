# Fate War Alliance Member Scraper

Extract alliance member ranking data from the Fate War game UI using screen capture and OCR.

## Features

- **Window Capture**: Captures only the game window (no full-screen screenshot)
- **Smart Cropping**: Configurable region extraction for the member list
- **OCR Processing**: Uses Tesseract OCR with preprocessing for accuracy
- **Robust Parsing**: Handles OCR noise and extracts Name, Power, Helps
- **Clean Output**: Exports to CSV and a shareable HTML table
- **Debug Mode**: Saves intermediate images for troubleshooting

## Requirements

- Python 3.12+
- Windows 10/11
- Tesseract OCR installed

## Installation

### 1. Install Tesseract OCR

Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### 2. Install the Project

```bash
# Clone or download this repository
cd fate-war-scraper

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install in editable mode
pip install -e .
```

## Usage

### Basic Usage

1. Start the Fate War game
2. Open the alliance member list screen
3. Run the scraper:

```bash
python -m fatewarscraper
```

The scraper will:
1. Find and capture the "Fate War" window
2. Crop to the member list region
3. Run OCR to extract text
4. Parse member data (Name, Power, Helps)
5. Export to `outputs/alliance_members.csv` and `outputs/alliance_members.html`

### Adjusting Crop Region

The default crop region may not match your screen resolution. To adjust:

1. Run the scraper once to generate `outputs/debug_full.png`
2. Open the debug image and note the pixel coordinates of the member list
3. Edit `src/fatewarscraper/config.py`:

```python
@dataclass(frozen=True)
class CropConfig:
    left: int = 50      # Left edge of member list
    top: int = 150      # Top edge
    right: int = 800    # Right edge
    bottom: int = 900   # Bottom edge
```

4. Run again and check `outputs/debug_crop.png` to verify

### Custom Window Title

If your game window has a different title:

```python
# In config.py
@dataclass(frozen=True)
class ScraperConfig:
    window_title: str = "Your Window Title"
    # ... other settings
```

## Output Files

### CSV (`outputs/alliance_members.csv`)
```csv
Name,Power,Helps,Valid,Raw Line
PlayerOne,123456,789,Yes,PlayerOne 123456 789
PlayerTwo,234567,890,Yes,PlayerTwo 234567 890
```

### HTML (`outputs/alliance_members.html`)
- Clean, shareable table
- Sortable columns (click headers)
- Responsive design
- Highlights rows with parsing issues

### Debug Files (when `debug_enabled=True`)
- `debug_full.png`: Full window capture
- `debug_crop.png`: Cropped member list region
- `debug_processed.png`: Preprocessed image (after enhancement)
- `debug_ocr.txt`: Raw OCR text output

## Configuration

All configuration is in `src/fatewarscraper/config.py`:

```python
@dataclass(frozen=True)
class ScraperConfig:
    window_title: str = "Fate War"              # Window to capture
    crop: CropConfig = CropConfig()             # Crop coordinates
    ocr: OCRConfig = OCRConfig()                # OCR settings
    output_dir: Path = Path("outputs")          # Output directory
    debug_enabled: bool = True                  # Save debug files
```

### OCR Configuration

```python
@dataclass(frozen=True)
class OCRConfig:
    tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_config: str = "--psm 6 --oem 3"   # Tesseract parameters
    language: str = "eng"                        # OCR language
```

## Troubleshooting

### "Window not found"
- Ensure Fate War is running
- Check the window title matches exactly
- Try adjusting `window_title` in config

### Poor OCR Results
1. Check `debug_crop.png` - is the member list fully visible?
2. Adjust crop coordinates in `CropConfig`
3. Check `debug_processed.png` - text should be clear black-on-white
4. Try adjusting preprocessing in `preprocess.py`:
   - `contrast_factor`: 1.5 to 3.0
   - `threshold`: 100 to 150

### "Tesseract not found"
- Verify Tesseract is installed
- Update `tesseract_cmd` path in `OCRConfig`

### Invalid Parsing
- Check `debug_ocr.txt` to see raw OCR output
- Member rows marked as invalid are still included in output with `is_valid=False`
- Adjust parsing logic in `parse.py` if needed

## Project Structure

```
fate-war-scraper/
├── src/fatewarscraper/
│   ├── __init__.py         # Package metadata
│   ├── __main__.py         # Entry point
│   ├── cli.py              # Main orchestration
│   ├── config.py           # Configuration classes
│   ├── capture.py          # Window capture
│   ├── preprocess.py       # Image preprocessing
│   ├── ocr.py              # OCR extraction
│   ├── parse.py            # Data parsing
│   └── export.py           # CSV/HTML export
├── outputs/                # Generated files (gitignored)
├── pyproject.toml          # Project metadata
└── README.md
```

## Development

### Code Style
- Type hints everywhere
- Dataclasses for structured data
- Small, focused functions
- Descriptive names and docstrings

### Testing Manually
```bash
# Run with debug enabled (default)
python -m fatewarscraper

# Check outputs
outputs/debug_full.png        # Full capture
outputs/debug_crop.png        # Cropped region
outputs/debug_processed.png   # After preprocessing
outputs/debug_ocr.txt         # Raw OCR text
outputs/alliance_members.csv  # Final CSV
outputs/alliance_members.html # Final HTML
```

## Legal Notice

This tool performs passive screen reading only. It does NOT:
- Modify game memory
- Inject code into the game process
- Intercept network packets
- Violate the game's terms of service (screen reading is generally permitted)

Always check your game's terms of service before using automation tools.