# Fate War Alliance Member Scraper

Extract comprehensive alliance member data from the Fate War game UI using screen capture and multi-language OCR.

## Features

- **Multi-Category Tracking**: Automatically scrapes Power, Kills, Weekly Contribution, Construction, and Tribe Assistance.
- **Historical Progress Tracking**: Stores scan history and displays progress graphs for each member on the web dashboard.
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
python -m fatewarscraper
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
- `outputs/index.html`: A searchable/sortable web dashboard for the latest data.
- `outputs/members.json`: The latest raw data in JSON format.
- `outputs/parsed_members.txt`: A debug log showing raw OCR readings.
- `outputs/*.png`: Cropped debug images for verification.

## Web Hosting (Kostenlos auf GitHub Pages)

Du kannst die neuesten Allianz-Rankings ganz einfach kostenlos über GitHub Pages hosten:

### Einrichtung (Nur beim ersten Mal)

1. Sicherstellen, dass dein Projekt in ein GitHub-Repository gepusht wurde.
2. Führe das Deployment-Skript einmal aus: `.\deploy_gh_pages.ps1`
3. Gehe in deinem Repository auf GitHub zu **Settings** -> **Pages**.
4. Stelle unter **Build and deployment** die Quelle auf **Deploy from a branch** ein.
5. Wähle den `gh-pages` Branch und den `/ (root)` Ordner.
6. Klicke auf **Save**.

### Updates veröffentlichen

Führe nach einem Scan das bereitgestellte Deployment-Skript aus, um die neuesten Daten auf deine Website zu pushen:

```powershell
.\deploy_gh_pages.ps1
```

Deine Seite wird unter `https://<dein-benutzername>.github.io/<dein-repo-name>/` verfügbar sein.

## Scans planen (2x pro Woche)

Um den Fortschritt genau zu verfolgen, wird empfohlen, zweimal pro Woche einen Scan durchzuführen (z. B. Mittwoch und Sonntag).

### Windows Aufgabenplanung (Empfohlen)

1. Öffne die **Aufgabenplanung** unter Windows.
2. Klicke auf **Einfache Aufgabe erstellen**.
3. Lege einen Trigger fest (z. B. Wöchentlich, wobei Mittwoch und Sonntag ausgewählt werden).
4. Wähle als **Aktion** die Option **Programm starten**.
5. Programm/Skript: `powershell.exe`
6. Argumente hinzufügen: `-ExecutionPolicy Bypass -File "C:\pfad\zu\FateWarScraper\run_and_deploy.ps1"`

### run_and_deploy.ps1 (Helfer-Skript)

Erstelle eine Datei namens `run_and_deploy.ps1` in deinem Projektverzeichnis, um sowohl den Scan als auch das Website-Update zu automatisieren:

```powershell
# Virtuelle Umgebung aktivieren
.\venv\Scripts\Activate.ps1

# Scraper ausführen
python -m fatewarscraper

# Deployment auf GitHub Pages
.\deploy_gh_pages.ps1
```

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