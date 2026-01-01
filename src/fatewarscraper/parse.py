"""Parse OCR text into structured alliance member data using EasyOCR text detection."""

import re
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
    cleaned = text.replace(',', '').replace('.', '').replace(' ', '')
    cleaned = cleaned.replace('O', '0').replace('o', '0')
    cleaned = cleaned.replace('I', '1').replace('l', '1')
    return cleaned


def extract_number(text: str) -> Optional[int]:
    """Extract a number from text string."""
    cleaned = clean_number_string(text)
    match = re.search(r'\d+', cleaned)
    if match:
        try:
            return int(match.group())
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

    reader = get_reader(
        ["ja", "en"],
        True
    )

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
    from fatewarscraper.ocr import extract_text_single_line

    row_h = row_bottom - row_top
    padding = max(6, int(row_h * 0.25))  # 25% of row height, min 6px
    row_top = max(0, row_top - padding)
    row_bottom = min(img.height, row_bottom + padding)

    rank_crop = img.crop((0, row_top, 66, row_bottom))
    name_crop = img.crop((159, row_top, 363, row_bottom))
    power_crop = img.crop((763, row_top, 941, row_bottom))

    rank_text = extract_text_single_line(rank_crop)
    name_text = extract_text_single_line(name_crop)
    power_text = extract_text_single_line(power_crop)

    read_rank = extract_number(rank_text) if rank_text else None
    name = clean_name(name_text)
    power = extract_number(power_text) if power_text else None

    is_valid = bool(name) and (read_rank is not None or power is not None)

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
    from fatewarscraper.ocr import extract_text_single_line

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

            name_text = extract_text_single_line(name_crop)
            power_text = extract_text_single_line(power_crop)

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


def deduplicate_records(records: list[MemberRecord]) -> list[MemberRecord]:
    """Remove duplicate member records based on name."""
    seen_names = set()
    unique_records = []

    for record in records:
        if record.name and record.name not in seen_names:
            unique_records.append(record)
            seen_names.add(record.name)

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