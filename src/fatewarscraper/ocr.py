"""OCR functionality using EasyOCR."""

import easyocr
from PIL import Image
from pathlib import Path
import numpy as np


# Global readers (initialized on demand)
_readers = {}


def get_reader(languages=None, use_gpu=True) -> easyocr.Reader:
    """Get or create EasyOCR reader instance for specific languages.

    Args:
        languages: List of language codes (default: ['en'])
        use_gpu: Whether to use GPU acceleration (default: True)

    Returns:
        EasyOCR Reader instance
    """
    if languages is None:
        languages = ['en']
    
    # Sort to ensure consistent key
    lang_key = tuple(sorted(languages))
    
    global _readers
    if lang_key not in _readers:
        gpu_status = "GPU (CUDA)" if use_gpu else "CPU"
        print(f"Initializing EasyOCR with {gpu_status} and languages {list(languages)}...")
        _readers[lang_key] = easyocr.Reader(list(languages), gpu=use_gpu)
    
    return _readers[lang_key]


def extract_text(img: Image.Image, languages=None) -> str:
    """Extract text from image using EasyOCR.

    Args:
        img: PIL Image to perform OCR on
        languages: Optional list of languages

    Returns:
        Extracted text as string
    """
    try:
        reader = get_reader(languages)
        img_array = np.array(img)
        results = reader.readtext(img_array)
        results.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
        text_parts = [text for (bbox, text, conf) in results]
        return ' '.join(text_parts).strip()
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e


def extract_text_single_line(img: Image.Image, languages=None) -> str:
    """Extract text from single-line image using EasyOCR.

    Args:
        img: PIL Image containing single line of text
        languages: Optional list of languages

    Returns:
        Extracted text as string
    """
    reader = get_reader(languages)
    img_array = np.array(img)

    # Get results with details to allow sorting by X coordinate
    results = reader.readtext(img_array, detail=1)

    if not results:
        return ""

    # Sort strictly by left-most X coordinate
    results.sort(key=lambda x: x[0][0][0])

    text_parts = [text for (bbox, text, conf) in results]
    
    # Filter out very low confidence noise
    if len(text_parts) > 1:
        text_parts = [text for (bbox, text, conf) in results if conf > 0.1]

    return ' '.join(text_parts).strip()


def extract_text_for_name(img: Image.Image) -> str:
    """Specialized extraction for names that might be in multiple languages.
    
    Tries multiple reader combinations to handle EasyOCR's strict compatibility limits.
    Returns the result with the highest confidence or most characters.
    """
    candidates = []
    
    # Language groups to try
    # EasyOCR has compatibility limits:
    # - ch_sim is only compatible with en
    # - ja is only compatible with en
    # - ko is only compatible with en
    # - vi is compatible with en
    # - ru is compatible with en
    lang_sets = [
        ['en', 'vi'],
        ['en', 'ko'],
        ['en', 'ja'],
        ['en', 'ch_sim'],
        ['en', 'ru']
    ]

    for langs in lang_sets:
        try:
            reader = get_reader(langs)
            img_array = np.array(img)
            # Get detailed results to check confidence and character types
            results = reader.readtext(img_array, detail=1)
            
            if not results:
                continue
                
            # Sort by X
            results.sort(key=lambda x: x[0][0][0])
            
            text = ' '.join([res[1] for res in results if res[2] > 0.1]).strip()
            conf = sum([res[2] for res in results]) / len(results) if results else 0
            
            if text:
                # Give a boost to non-Latin results
                # Simple heuristic: if any character is outside Latin-1, it's likely a better match
                # if we're looking for international names.
                has_non_latin = any(ord(c) > 255 for c in text)
                score = len(text) * (1.5 if has_non_latin else 1.0) * conf
                candidates.append((text, score, has_non_latin))
        except Exception:
            continue

    if not candidates:
        return ""

    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def extract_lines(img: Image.Image) -> list[str]:
    """Extract text lines from image.

    Args:
        img: PIL Image to perform OCR on

    Returns:
        List of text lines
    """
    text = extract_text(img)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return lines


def configure_tesseract(tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe") -> None:
    """Dummy function for backward compatibility.

    Since we're using EasyOCR now, this does nothing.
    Kept for compatibility with existing code.
    """
    pass  # No configuration needed for EasyOCR