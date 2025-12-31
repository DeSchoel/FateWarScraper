# FateWarScraper — Claude Prompt Library

Use these prompts together with `CONTEXT.md`.
Always paste CONTEXT.md first, then one of the prompts below.

---

## 1️⃣ Window Capture (Game Window Only)

**Goal:** Capture only the Fate War game window.

**Prompt:**
> Using the project context, improve `capture.py` so it reliably captures only the Fate War window on Windows.  
> The game runs in windowed or borderless windowed mode.  
> Use Win32 APIs to find the window by title substring and return a PIL Image.  
> Add clear errors when the window is not found or minimized.  
> Output the full updated `capture.py`.

---

## 2️⃣ Crop Alliance Member List

**Goal:** Crop only the alliance member list area.

**Prompt:**
> Using the project context, modify `cli.py` to crop the alliance member list region from the captured game window.  
> Add a clearly named crop configuration (constants or dataclass).  
> Always write `debug_full.png` and `debug_crop.png`.  
> Output the full updated `cli.py`.

---

## 3️⃣ OCR Preprocessing Improvements

**Goal:** Improve OCR accuracy for UI text and numbers.

**Prompt:**
> Using the project context, implement `preprocess.py` to improve OCR accuracy for a game UI.  
> Focus on grayscale, contrast, and thresholding.  
> Keep it simple and readable.  
> Output the full `preprocess.py`.

---

## 4️⃣ Parse Alliance Rows (Core Logic)

**Goal:** Convert OCR text into structured data.

**Prompt:**
> Using the project context, design and implement `parse.py`.  
> Input: raw OCR text lines from the alliance member list.  
> Output: a list of dataclass records with fields like name, power, helps, raw_line, is_valid.  
> Handle OCR noise gracefully.  
> Mark invalid rows instead of crashing.  
> Output the full `parse.py`.

---

## 5️⃣ Integrate Parsing Into Pipeline

**Goal:** Wire parsing into the main flow.

**Prompt:**
> Using the project context, update `cli.py` to use `parse.py` instead of exporting raw OCR lines.  
> Keep `cli.py` minimal and orchestration-only.  
> Output the full updated `cli.py`.

---

## 6️⃣ Improve CSV Export

**Goal:** Clean, stable CSV output.

**Prompt:**
> Using the project context, refactor `export.py` so CSV output has explicit columns:  
> name, power, helps, raw_line, is_valid.  
> Ensure deterministic ordering and UTF-8 safety.  
> Output the full updated `export.py`.

---

## 7️⃣ Improve HTML Export (Mini Website)

**Goal:** Shareable, readable HTML table.

**Prompt:**
> Using the project context, enhance the HTML export to create a clean, readable table.  
> Add basic styling (no JS required).  
> Keep output as a single self-contained HTML file.  
> Output the full updated `export.py` or a new HTML module if appropriate.

---

## 8️⃣ Robustness & Validation Pass

**Goal:** Make the pipeline harder to break.

**Prompt:**
> Review the current FateWarScraper pipeline for robustness.  
> Identify fragile assumptions (OCR, window capture, parsing).  
> Propose small, targeted improvements that keep the code clean.  
> Do NOT add unnecessary dependencies.

---

## 9️⃣ Performance & UX Improvements

**Goal:** Make the tool nicer to use.

**Prompt:**
> Using the project context, suggest UX improvements for running the scraper (CLI options, config file, logging).  
> Keep it simple and Windows-friendly.  
> Provide code examples only where necessary.

---

## 🔟 Pre-Release Cleanup

**Goal:** Prepare the repo for sharing.

**Prompt:**
> Review this repository as if preparing it for public release.  
> Suggest README improvements, folder cleanup, and minor refactors.  
> Keep changes minimal and professional.

---

## How to use this file
1. Paste `CONTEXT.md`
2. Paste ONE prompt from this file
3. Paste the relevant code file(s)
4. Ask Claude to produce full updated files

This keeps answers focused and consistent.
