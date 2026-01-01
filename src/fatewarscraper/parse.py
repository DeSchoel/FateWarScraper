"""Parse OCR text into structured alliance member data using EasyOCR text detection."""

import re
import difflib
from dataclasses import dataclass
from operator import truediv
from typing import Optional
from PIL import Image


@dataclass
class MemberRecord:
    """Structured alliance member data.

    Attributes:
        rank: Member rank/position in alliance
        name: Member name
        power: Member power
        read_rank: Rank read from OCR (may differ from actual rank)
        power_rank: Actual rank based on power sorting
        rank_mismatch: True if read_rank != power_rank
        raw_line: Original OCR line
        is_valid: Whether parsing was successful
    """
    rank: Optional[int] = None  # This will be power_rank
    name: str = ""
    power: Optional[int] = None
    read_rank: Optional[int] = None  # What OCR read
    power_rank: Optional[int] = None  # Calculated from power
    rank_mismatch: bool = False
    raw_line: str = ""
    is_valid: bool = True


def clean_number_string(text: str) -> str:
    """Remove common OCR noise and formatting from numbers."""
    # First apply common character mappings
    cleaned = text.replace('O', '0').replace('o', '0')
    cleaned = cleaned.replace('I', '1').replace('l', '1')
    cleaned = cleaned.replace('S', '5').replace('s', '5')
    cleaned = cleaned.replace('G', '6')
    cleaned = cleaned.replace('B', '8')
    cleaned = cleaned.replace('Q', '0')
    cleaned = cleaned.replace('C', '0')
    cleaned = cleaned.replace('(', '0').replace(')', '0')
    
    # Strip everything that is not a digit
    cleaned = "".join(c for c in cleaned if c.isdigit())
    return cleaned


def extract_number(text: str) -> Optional[int]:
    """Extract a number from text string."""
    cleaned = clean_number_string(text)
    if cleaned:
        try:
            return int(cleaned)
        except ValueError:
            pass
    return None


def clean_name(text: str) -> str:
    """Clean name text - keep alphanumeric and international characters.

    Supports ALL major writing systems:
    - English (Latin alphabet)
    - Korean (Hangul)
    - Japanese (Hiragana, Katakana, Kanji)
    - Chinese (Simplified and Traditional)
    - Russian (Cyrillic)
    - Arabic
    - Vietnamese (Latin with diacritics)
    - Thai
    - And more...

    Args:
        text: Raw name text from OCR

    Returns:
        Cleaned name
    """
    # Keep: letters, numbers, underscore, hyphen
    # Remove: punctuation, symbols, emojis
    # \w matches Unicode word characters (letters, digits from any language)
    pattern = r'[^\w\-]'
    cleaned = re.sub(pattern, '', text, flags=re.UNICODE)
    return cleaned.strip()


def detect_text_rows_with_easyocr(img: Image.Image) -> list[tuple[int, int]]:
    """Use EasyOCR to detect where text is, then group into rows."""
    from fatewarscraper.ocr import get_reader
    import numpy as np

    # Use a compatible set of languages for detection
    reader = get_reader()

    img_array = np.array(img)

    detections = reader.readtext(img_array)

    if not detections:
        return []

    y_positions = []
    for bbox, text, conf in detections:
        if conf < 0.35:
            continue
        ys = [point[1] for point in bbox]
        top_y = min(ys)
        bottom_y = max(ys)
        y_positions.append((top_y, bottom_y))

    if not y_positions:
        return []

    y_positions.sort(key=lambda x: x[0])

    rows = []
    current_row_top = y_positions[0][0]
    current_row_bottom = y_positions[0][1]

    for top_y, bottom_y in y_positions[1:]:
        if top_y <= current_row_bottom + 10:
            current_row_bottom = max(current_row_bottom, bottom_y)
        else:
            rows.append((int(current_row_top), int(current_row_bottom)))
            current_row_top = top_y
            current_row_bottom = bottom_y

    rows.append((int(current_row_top), int(current_row_bottom)))

    return rows


def extract_member_from_row(img: Image.Image, row_top: int, row_bottom: int) -> MemberRecord:
    """Extract member data from a detected row using fixed x-coordinates."""
    from fatewarscraper.ocr import extract_text_single_line, extract_text_for_name
    from fatewarscraper.preprocess import preprocess_for_ocr

    row_h = row_bottom - row_top
    # Add more padding for very short rows (likely at the edges of crops)
    if row_h < 20:
        padding = 10
    else:
        padding = max(4, int(row_h * 0.15))
    
    row_top = max(0, row_top - padding)
    row_bottom = min(img.height, row_bottom + padding)

    # Coordinates are for the original 1280x720 window
    # EasyOCR works better on processed crops
    rank_crop = img.crop((0, row_top, 80, row_bottom))
    name_crop = img.crop((150, row_top, 400, row_bottom))
    power_crop = img.crop((730, row_top, 950, row_bottom))

    # Apply preprocessing to field crops
    # Rank is very small (1-2 digits), using 4x upscale helps significantly
    # Power is longer (7-8 digits), 3x is a good balance
    rank_crop = preprocess_for_ocr(rank_crop, upscale=4)
    name_crop = preprocess_for_ocr(name_crop, upscale=2)
    power_crop = preprocess_for_ocr(power_crop, upscale=3)

    # Use standard English reader for numbers
    rank_text = extract_text_single_line(rank_crop, languages=['en'])
    # Use specialized multi-language logic for names
    name_text = extract_text_for_name(name_crop)
    # Use standard English reader for numbers
    power_text = extract_text_single_line(power_crop, languages=['en'])

    read_rank = extract_number(rank_text) if rank_text else None
    name = clean_name(name_text)
    power = extract_number(power_text) if power_text else None

    # Noise filtering
    # 1. Names should be at least 2 characters (game names usually are)
    # 2. If it's a single character name, it's likely noise unless power is high
    is_valid = bool(name) and (read_rank is not None or power is not None)
    
    if is_valid and len(name) < 2:
        # Reject single-character names unless they have a very plausible power
        if power is None or power < 1000:
            is_valid = False

    return MemberRecord(
        read_rank=read_rank,
        name=name,
        power=power,
        raw_line=f"Read Rank: {rank_text} | Name: {name_text} | Power: {power_text}",
        is_valid=is_valid
    )


def parse_image_by_rows(img: Image.Image, **kwargs) -> list[MemberRecord]:
    """Parse image using EasyOCR text detection to find rows."""
    rows = detect_text_rows_with_easyocr(img)

    print(f"  Detected {len(rows)} rows via EasyOCR", end="")
    if rows:
        print(f" (first at y={rows[0][0]}, last at y={rows[-1][1]})")
    else:
        print()

    records = []
    for i, (row_top, row_bottom) in enumerate(rows):
        try:
            record = extract_member_from_row(img, row_top, row_bottom)
            if record.is_valid:
                records.append(record)
        except Exception as e:
            print(f"  Warning: Failed to parse row {i} (y={row_top}-{row_bottom}): {e}")
            continue

    return records


def parse_podium_image(img: Image.Image) -> list[MemberRecord]:
    """Parse the podium image with top 3 members using FIXED coordinates."""
    from fatewarscraper.ocr import extract_text_single_line, extract_text_for_name
    from fatewarscraper.preprocess import preprocess_for_ocr

    records = []

    podium_coords = [
        (1, (343, 12, 619, 41), (436, 72, 619, 99)),
        (2, (23, 12, 299, 41), (116, 72, 299, 99)),
        (3, (663, 12, 939, 41), (755, 72, 939, 99)),
    ]

    for rank, name_coords, power_coords in podium_coords:
        try:
            name_crop = img.crop(name_coords)
            power_crop = img.crop(power_coords)

            # Preprocess podium crops
            name_crop = preprocess_for_ocr(name_crop)
            power_crop = preprocess_for_ocr(power_crop)

            name_text = extract_text_for_name(name_crop)
            power_text = extract_text_single_line(power_crop, languages=['en'])

            name = clean_name(name_text)
            power = extract_number(power_text) if power_text else None

            if name:
                records.append(MemberRecord(
                    read_rank=rank,  # Podium ranks are correct
                    name=name,
                    power=power,
                    raw_line=f"Read Rank: {rank} | Name: {name_text} | Power: {power_text}",
                    is_valid=True
                ))
        except Exception as e:
            print(f"  Warning: Failed to parse rank {rank} from podium: {e}")
            continue

    return records


def is_similar_name(name1: str, name2: str, threshold: float = 0.85) -> bool:
    """Check if two names are similar using SequenceMatcher."""
    if not name1 or not name2:
        return False
    # Case-insensitive comparison
    name1 = name1.lower()
    name2 = name2.lower()
    if name1 == name2:
        return True
    
    similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
    return similarity >= threshold


def deduplicate_records(records: list[MemberRecord]) -> list[MemberRecord]:
    """Remove duplicate member records based on fuzzy name, power, and rank matching.
    
    Rules for merging:
    1. Same name (case-insensitive) AND same power -> merge
    2. Similar name AND same power -> merge
    3. Same name AND similar power (within 1%) -> merge
    4. Same read_rank AND (similar name OR similar power) -> merge
    """
    if not records:
        return []

    # Sort by name length descending to prefer longer names when merging similar ones
    # or keep the one with higher confidence (though we don't have confidence here)
    sorted_recs = sorted(records, key=lambda x: len(x.name), reverse=True)
    
    unique_records: list[MemberRecord] = []

    for new_rec in sorted_recs:
        if not new_rec.name or not new_rec.is_valid:
            continue
            
        found_duplicate = False
        for i, existing_rec in enumerate(unique_records):
            # Check for name similarity
            names_similar = is_similar_name(new_rec.name, existing_rec.name)
            
            # Check for power similarity
            powers_similar = False
            if new_rec.power is not None and existing_rec.power is not None:
                if new_rec.power == existing_rec.power:
                    powers_similar = True
                else:
                    # Within 1% power difference
                    diff = abs(new_rec.power - existing_rec.power)
                    if diff / max(new_rec.power, existing_rec.power) < 0.01:
                        powers_similar = True
            
            # Check for rank identity
            ranks_identical = (new_rec.read_rank is not None and 
                              existing_rec.read_rank is not None and 
                              new_rec.read_rank == existing_rec.read_rank)

            # Merging logic
            name_exact_ignore_case = new_rec.name.lower() == existing_rec.name.lower()
            
            # Base conditions for merging
            should_merge = False
            if name_exact_ignore_case:
                should_merge = True
            elif names_similar and powers_similar:
                should_merge = True
            elif ranks_identical:
                # Same rank is a VERY strong signal.
                # Merge if names are somewhat similar OR power is somewhat similar
                if names_similar or powers_similar:
                    should_merge = True
                elif is_similar_name(new_rec.name, existing_rec.name, threshold=0.5):
                    # Lower threshold for same rank
                    should_merge = True
                elif len(new_rec.name) < 3 or len(existing_rec.name) < 3:
                    # Likely a cutoff name at the same rank
                    should_merge = True
            elif names_similar and (powers_similar or (new_rec.power is None or existing_rec.power is None)):
                # Similar name and (similar power or one missing power)
                should_merge = True

            if should_merge:
                found_duplicate = True
                # Merge: prefer the record with more data
                if existing_rec.read_rank is None and new_rec.read_rank is not None:
                    unique_records[i].read_rank = new_rec.read_rank
                
                # If both have power, prefer the higher one (usually more complete OCR)
                if new_rec.power is not None:
                    if unique_records[i].power is None or new_rec.power > unique_records[i].power:
                        unique_records[i].power = new_rec.power
                        unique_records[i].raw_line = new_rec.raw_line
                
                # Name selection: 
                # If one name is a substring of another, keep the longer one.
                # BUT if names are just similar, and we have a power winner, maybe keep that name?
                # For now, if the new record has significantly higher power, take its name too.
                if new_rec.power is not None and existing_rec.power is not None:
                    if new_rec.power > existing_rec.power * 1.05: # 5% more power
                         unique_records[i].name = new_rec.name
                         unique_records[i].raw_line = new_rec.raw_line
                elif names_similar and not name_exact_ignore_case:
                    # Fallback to length if powers are similar
                    if len(new_rec.name) > len(existing_rec.name):
                         unique_records[i].name = new_rec.name
                         unique_records[i].raw_line = new_rec.raw_line
                
                break
        
        if not found_duplicate:
            unique_records.append(new_rec)

    return unique_records


def assign_power_ranks_and_detect_mismatches(records: list[MemberRecord]) -> list[MemberRecord]:
    """Assign ranks based on power and detect mismatches with read ranks.

    Process:
    1. Sort by power (highest to lowest)
    2. Assign power_rank (1, 2, 3, ...)
    3. Compare power_rank with read_rank
    4. Mark mismatches

    Args:
        records: List of member records

    Returns:
        Same records with power_rank assigned and rank field set
    """
    # Sort by power (highest first)
    sorted_records = sorted(
        records,
        key=lambda r: r.power if r.power is not None else 0,
        reverse=True
    )

    # Assign power-based ranks
    for i, record in enumerate(sorted_records, start=1):
        record.power_rank = i
        record.rank = i  # Main rank field is power-based

        # Check for mismatch
        if record.read_rank is not None and record.read_rank != record.power_rank:
            record.rank_mismatch = True

    return sorted_records


def sort_records(records: list[MemberRecord]) -> list[MemberRecord]:
    """Sort by power and assign power-based ranks with mismatch detection."""
    return assign_power_ranks_and_detect_mismatches(records)