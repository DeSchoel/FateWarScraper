# FateWarScraper — Claude Context

You are helping me build a clean, maintainable Python project. Prioritize:
- clear architecture
- small focused functions
- readable code with type hints
- robust handling of OCR noise
- minimal dependencies
- Windows compatibility

## Project purpose
Extract alliance member ranking data (Name, Power, Helps, etc.) from the Fate War (Steam) game UI by:
1) capturing ONLY the game window
2) cropping the alliance member list region
3) OCR on the cropped image
4) parsing into structured rows
5) exporting to CSV and a simple shareable HTML page

No memory reading, no packet sniffing, no game modification.

## Repository layout (src layout)
- Source code lives in: `src/fatewarscraper/`
- The package is run via: `python -m fatewarscraper`
- Outputs are written to: `outputs/` (ignored by git)

Target module responsibilities:
- `capture.py`: capture the Fate War window and return a PIL Image (no OCR here)
- `preprocess.py`: image cleanup for OCR (return ndarray or PIL Image consistently)
- `ocr.py`: OCR backend (Tesseract). Single entry function, configurable.
- `parse.py`: convert OCR text into structured data (dataclasses)
- `export.py`: write CSV + HTML (clean, safe HTML escaping)
- `cli.py`: orchestration; minimal logic, calls other modules
- `__main__.py`: entry point that calls `cli.run()`

## Coding rules
- Use Python 3.12.
- Prefer standard library first; only add dependencies when clearly justified.
- Use type hints everywhere.
- Use `dataclasses` for structured records.
- Avoid global state; configuration should be passed as parameters or a small config dataclass.
- No hacks like modifying `sys.path`. Keep the project installable with editable install.
- Keep functions short and single-purpose.
- Use descriptive names and docstrings for public functions.

## OCR & parsing constraints
- Expect OCR noise: missing spaces, misread digits, random punctuation.
- Member rows likely include: name + numbers (power/helps).
- Parsing should be resilient: best-effort extraction with validation and fallback.
- When parsing fails, keep raw line in a `raw` field and mark row as `is_valid=False`.

## Output requirements
- CSV columns should be stable and explicit (e.g., name, power, helps, raw_line, is_valid).
- HTML should be a simple table that is readable and shareable.
- Prefer deterministic outputs, avoid random ordering.

## Debugging aids
- Always produce debug images when introducing cropping:
  - `outputs/debug_full.png`
  - `outputs/debug_crop.png`
- Provide a clear way to adjust crop settings (config constants or config file).

## When you respond
- If changing code, output full file content for each file that changes.
- Keep changes minimal and explain the rationale briefly.
- If you need sample OCR output to design parsing, ask for a small sample (10–30 lines) and specify what format you want.

## Current environment assumptions
- OS: Windows 10/11
- IDE: PyCharm
- OCR engine: Tesseract installed at:
  `C:\Program Files\Tesseract-OCR\tesseract.exe` (can be configured if needed)
