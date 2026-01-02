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
        kills: Member kills
        weekly_contribution: Member weekly contribution
        construction: Member construction
        tribe_assistance: Member tribe assistance
        gold_donation: Member gold donation
        read_rank: Rank read from OCR (may differ from actual rank)
        power_rank: Actual rank based on power sorting
        rank_mismatch: True if read_rank != power_rank
        raw_line: Original OCR line
        is_valid: Whether parsing was successful
    """
    rank: Optional[int] = None  # This will be power_rank or similar
    name: str = ""
    power: Optional[int] = None
    kills: Optional[int] = None
    weekly_contribution: Optional[int] = None
    construction: Optional[int] = None
    tribe_assistance: Optional[int] = None
    # gold_donation: Optional[int] = None  # Disabled per user request
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
    # Special handling for common OCR errors in large numbers
    
    # Remove dots and commas if they look like separators
    temp = text
    # Replace dots/commas that are followed by 3 digits
    temp = re.sub(r'[\.,](\d{3})(?!\d)', r'\1', temp)
    temp = re.sub(r'[\.,](\d{3})', r'\1', temp)

    # 1. Handle spaces or punctuation that might split a number or prepend noise
    # We want to catch things like "9 1,392,524" or "Rank 5 21,114,977"
    # where the first part is likely a misread rank or noise.
    parts = re.split(r'[\s\-:;]+', temp)
    if len(parts) > 1:
        new_parts = []
        for i, p in enumerate(parts):
            p_clean = clean_number_string(p)
            if not p_clean:
                continue
            
            # Heuristic: if the first part is very short (1-2 digits) 
            # and the second part is long (4+ digits), the first part is likely noise/rank.
            if i == 0 and len(p_clean) <= 2:
                # Check if there is a substantial next part
                next_part = ""
                for next_p in parts[i+1:]:
                    next_part = clean_number_string(next_p)
                    if next_part: break
                
                if len(next_part) >= 4:
                    # Skip the first short part as it's likely noise/rank
                    continue
            
            # Existing heuristic for single digit misread commas inside the number
            if len(p_clean) == 1 and len(new_parts) > 0 and len("".join(new_parts)) >= 3:
                # Potential misread comma. Skip it.
                continue
                
            new_parts.append(p_clean)
        
        cleaned = "".join(new_parts)
    else:
        cleaned = clean_number_string(temp)

    if cleaned:
        try:
            val = int(cleaned)
            return val
        except ValueError:
            pass
    return None


def get_display_width(s: str) -> int:
    """Calculate the display width of a string, accounting for wide characters."""
    import unicodedata
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('W', 'F'):
            width += 2
        else:
            width += 1
    return width


def pad_for_display(s: str, width: int) -> str:
    """Pad a string to a specific display width."""
    if s is None:
        s = ""
    current_width = get_display_width(s)
    padding = max(0, width - current_width)
    return s + " " * padding


def generate_text_report(records: list[MemberRecord], include_raw: bool = True) -> str:
    """Generate a formatted text report from member records."""
    # has_gold = any(rec.gold_donation is not None for rec in records)
    
    # Define columns: (Label, Width, Attribute)
    cols = [
        ("Rank", 5, "power_rank"),
        ("Name", 20, "name"),
        ("Power", 12, "power"),
        ("Kills", 12, "kills"),
        ("Weekly", 10, "weekly_contribution"),
        ("Const.", 10, "construction"),
        ("Asst.", 10, "tribe_assistance")
    ]
    # if has_gold:
    #     cols.append(("Gold", 10, "gold_donation"))
    
    # Header
    header_parts = [pad_for_display(label, width) for label, width, _ in cols]
    header = " | ".join(header_parts)
    if include_raw:
        header += " | Raw Line"
    
    lines = [header]
    
    # Separator line based on display width
    total_width = sum(width for _, width, _ in cols) + (len(cols) - 1) * 3
    if include_raw:
        total_width += 13 # " | Raw Line"
    lines.append("-" * total_width)
    
    for rec in records:
        row_parts = []
        for label, width, attr in cols:
            val = getattr(rec, attr)
            if val is None:
                val_str = "?" if attr == "power_rank" else "0"
            elif isinstance(val, int):
                # Use comma formatting for all numbers except rank
                val_str = f"{val:,}" if attr != "power_rank" else str(val)
            else:
                val_str = str(val)
            
            row_parts.append(pad_for_display(val_str, width))
        
        row = " | ".join(row_parts)
        if include_raw:
            row += f" | {rec.raw_line}"
        lines.append(row)
        
    return "\n".join(lines)


def clean_name(text: str) -> str:
    """Clean name text - keep alphanumeric and international characters.

    Args:
        text: Raw name text from OCR

    Returns:
        Cleaned name
    """
    # Keep: letters, numbers, underscore, hyphen
    # \w matches Unicode word characters (letters, digits from any language)
    pattern = r'[^\w\-]'
    cleaned = re.sub(pattern, '', text, flags=re.UNICODE)
    cleaned = cleaned.strip()

    # Noise filtering:
    # 1. If name is strictly numeric, it's likely a misread of a nearby number field
    if cleaned.isdigit():
        return ""
        
    # 2. Reject names that contain substrings from filenames (OCR hallucinations)
    # This often happens if the OCR catches text from a watermark or similar
    lower_cleaned = cleaned.lower()
    if "smallcheese" in lower_cleaned or "regular" == lower_cleaned or "podium" == lower_cleaned:
        return ""
        
    return cleaned


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
        if top_y <= current_row_bottom + 5:
            current_row_bottom = max(current_row_bottom, bottom_y)
        else:
            rows.append((int(current_row_top), int(current_row_bottom)))
            current_row_top = top_y
            current_row_bottom = bottom_y

    rows.append((int(current_row_top), int(current_row_bottom)))

    return rows


def extract_member_from_row(img: Image.Image, row_top: int, row_bottom: int, metric_name: str = "power") -> MemberRecord:
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
    rank_crop = img.crop((0, row_top, 100, row_bottom))
    name_crop = img.crop((150, row_top, 420, row_bottom))
    value_crop = img.crop((680, row_top, 1000, row_bottom))

    # Apply preprocessing to field crops
    # Rank is very small (1-2 digits), using 4x upscale helps significantly
    # Value is longer (7-8 digits), 3x is a good balance
    rank_crop = preprocess_for_ocr(rank_crop, upscale=4)
    name_crop = preprocess_for_ocr(name_crop, upscale=2)
    value_crop = preprocess_for_ocr(value_crop, upscale=3)

    # Use standard English reader for numbers
    rank_text = extract_text_single_line(rank_crop, languages=['en'])
    # Use specialized multi-language logic for names
    name_text = extract_text_for_name(name_crop)
    # Use standard English reader for numbers
    value_text = extract_text_single_line(value_crop, languages=['en'])

    read_rank = extract_number(rank_text) if rank_text else None
    name = clean_name(name_text)
    value = extract_number(value_text) if value_text else None

    # Noise filtering
    # 1. Names should be at least 2 characters (game names usually are)
    # 2. If it's a single character name, it's likely noise unless value is high
    is_valid = bool(name) and (read_rank is not None or value is not None)
    
    # Strict noise filtering for rank
    if read_rank is not None:
        # If OCR read something like "2c" or "L9", it might have been misread.
        # The user requested to exclude any entries with letters in their rank.
        if re.search(r'[a-zA-Z]', rank_text):
            is_valid = False
        
        # Also check for too much other noise
        rank_clean = "".join(c for c in rank_text if c.isdigit() or c.isspace())
        if len(rank_clean.strip()) < len(rank_text.strip()) - 1:
            # Too many non-digit characters in rank (e.g. "2!#")
            is_valid = False

    if is_valid and len(name) < 2:
        # Reject single-character names unless they have a very plausible value
        if value is None or value < 1000:
            is_valid = False

    # Filter out common UI noise at the bottom of lists
    if is_valid and value is not None and value < 100:
        # Very low power/kills/etc are usually noise from footer
        if read_rank is not None and read_rank > 50:
             is_valid = False

    # Create record with the specified metric
    record = MemberRecord(
        read_rank=read_rank,
        name=name,
        raw_line=f"Read Rank: {rank_text} | Name: {name_text} | {metric_name.capitalize()}: {value_text}",
        is_valid=is_valid
    )
    setattr(record, metric_name, value)
    return record


def parse_image_by_rows(img: Image.Image, metric_name: str = "power", **kwargs) -> list[MemberRecord]:
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
            record = extract_member_from_row(img, row_top, row_bottom, metric_name=metric_name)
            if record.is_valid:
                records.append(record)
        except Exception as e:
            print(f"  Warning: Failed to parse row {i} (y={row_top}-{row_bottom}): {e}")
            continue

    return records


def parse_podium_image(img: Image.Image, metric_name: str = "power") -> list[MemberRecord]:
    """Parse the podium image with top 3 members using FIXED coordinates."""
    from fatewarscraper.ocr import extract_text_single_line, extract_text_for_name
    from fatewarscraper.preprocess import preprocess_for_ocr

    records = []

    podium_coords = [
        (1, (343, 12, 619, 41), (436, 72, 619, 99)),
        (2, (23, 12, 299, 41), (116, 72, 299, 99)),
        (3, (663, 12, 939, 41), (755, 72, 939, 99)),
    ]

    for rank, name_coords, value_coords in podium_coords:
        try:
            name_crop = img.crop(name_coords)
            value_crop = img.crop(value_coords)

            # Preprocess podium crops
            name_crop = preprocess_for_ocr(name_crop)
            value_crop = preprocess_for_ocr(value_crop)

            name_text = extract_text_for_name(name_crop)
            value_text = extract_text_single_line(value_crop, languages=['en'])

            name = clean_name(name_text)
            value = extract_number(value_text) if value_text else None

            if name:
                record = MemberRecord(
                    read_rank=rank,  # Podium ranks are correct
                    name=name,
                    raw_line=f"Read Rank: {rank} | Name: {name_text} | {metric_name.capitalize()}: {value_text}",
                    is_valid=True
                )
                setattr(record, metric_name, value)
                records.append(record)
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

    # Sort by whether it has power (prefer records with power data as anchor)
    # Then by name length
    sorted_recs = sorted(records, key=lambda x: (x.power is not None, len(x.name)), reverse=True)
    
    unique_records: list[MemberRecord] = []

    for new_rec in sorted_recs:
        if not new_rec.name or not new_rec.is_valid:
            continue
            
        found_duplicate = False
        for i, existing_rec in enumerate(unique_records):
            # Check for name similarity
            # We use a slightly more lenient threshold for same power
            names_similar = is_similar_name(new_rec.name, existing_rec.name)
            
            # Check for power similarity
            powers_similar = False
            powers_nearly_identical = False
            if new_rec.power is not None and existing_rec.power is not None:
                if new_rec.power == existing_rec.power:
                    powers_similar = True
                    powers_nearly_identical = True
                else:
                    # Within 1% power difference for base similarity
                    diff = abs(new_rec.power - existing_rec.power)
                    ratio = diff / max(new_rec.power, existing_rec.power)
                    if ratio < 0.01:
                        powers_similar = True
                    # Within 0.1% power difference (very likely the same person)
                    if ratio < 0.001:
                        powers_nearly_identical = True
            
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
            elif powers_nearly_identical and is_similar_name(new_rec.name, existing_rec.name, threshold=0.7):
                # If powers are almost identical, be much more lenient with names
                should_merge = True
            elif ranks_identical:
                # Same rank is a VERY strong signal.
                if names_similar or powers_similar or is_similar_name(new_rec.name, existing_rec.name, threshold=0.6):
                    should_merge = True
                elif len(new_rec.name) < 3 or len(existing_rec.name) < 3:
                    should_merge = True
            elif names_similar and (powers_similar or (new_rec.power is None or existing_rec.power is None)):
                # Similar name and (similar power or one missing power)
                should_merge = True
            elif powers_similar and is_similar_name(new_rec.name, existing_rec.name, threshold=0.7):
                # More lenient name matching if power is exactly the same
                should_merge = True
            elif is_similar_name(new_rec.name, existing_rec.name, threshold=0.5) and (new_rec.power is None or existing_rec.power is None) and (new_rec.read_rank is None or existing_rec.read_rank is None):
                # Catch partial names (like ゆ一 vs ゆ一一) when power/rank is missing in one
                should_merge = True

            if should_merge:
                found_duplicate = True
                # Merge: prefer the record with more data
                if existing_rec.read_rank is None and new_rec.read_rank is not None:
                    unique_records[i].read_rank = new_rec.read_rank
                
                # Merge all metric fields
                for field in ['power', 'kills', 'weekly_contribution', 'construction', 'tribe_assistance']:
                    # gold_donation field is disabled
                    new_val = getattr(new_rec, field)
                    existing_val = getattr(existing_rec, field)
                    if new_val is not None:
                        if existing_val is None:
                            setattr(unique_records[i], field, new_val)
                        elif field == 'power':
                            # Heuristic to handle 10x OCR misreads (hallucinated digits)
                            # If new value is ~10x larger than existing, and existing rank > 10,
                            # it's likely that the new value is a misread.
                            # Conversely, if new value is ~1/10th of existing, and existing rank < 10,
                            # the existing might be the misread (but usually larger is misread).
                            
                            is_new_much_larger = new_val > existing_val * 5
                            is_existing_much_larger = existing_val > new_val * 5
                            
                            # Prefer the one that's more plausible if we have ranks
                            rank = new_rec.read_rank or existing_rec.read_rank
                            
                            if is_new_much_larger:
                                # Only accept much larger power if rank is very low (top players)
                                if rank is not None and rank <= 3:
                                    setattr(unique_records[i], field, new_val)
                                # otherwise, stick with smaller value
                            elif is_existing_much_larger:
                                # If existing is much larger but rank is high, it's likely wrong
                                if rank is not None and rank > 3:
                                    setattr(unique_records[i], field, new_val)
                                # otherwise keep existing (larger)
                            else:
                                # Values are comparable, take the larger one (likely more complete capture)
                                if new_val > existing_val:
                                    setattr(unique_records[i], field, new_val)
                        else:
                            if new_val > existing_val:
                                setattr(unique_records[i], field, new_val)
                
                # Name selection:
                # Priority 1: Keep the name from the scan that provided the POWER metric.
                # Priority 2: Keep the longer name if values are similar.
                
                # If existing has power and new doesn't, keep existing name.
                # If new has power and existing doesn't, take new name.
                if new_rec.power is not None and existing_rec.power is None:
                    unique_records[i].name = new_rec.name
                    unique_records[i].raw_line = new_rec.raw_line
                elif existing_rec.power is not None and new_rec.power is None:
                    # Keep existing name
                    pass
                else:
                    # Both have or both lack power: prefer longer/more complete name
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
    1. Filter out records with 0 power (OCR artifacts)
    2. Sort by power (highest to lowest)
    3. Assign power_rank (1, 2, 3, ...)
    4. Compare power_rank with read_rank
    5. Mark mismatches

    Args:
        records: List of member records

    Returns:
        Same records with power_rank assigned and rank field set
    """
    # Filter out records with 0 power or missing power
    # In this game, every real player in the alliance list has some power.
    # 0 power entries are almost always OCR artifacts or partial row reads.
    filtered_records = [r for r in records if r.power and r.power > 0]

    # Sort by power (highest first)
    sorted_records = sorted(
        filtered_records,
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