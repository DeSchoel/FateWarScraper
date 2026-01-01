"""OCR functionality using EasyOCR."""

import easyocr
from PIL import Image
from pathlib import Path
import numpy as np


# Global reader instance (initialized once for performance)
_reader = None


def get_reader(languages=None, use_gpu=True) -> easyocr.Reader:
    """Get or create EasyOCR reader instance.

    Args:
        languages: List of language codes (default: ['en'])
        use_gpu: Whether to use GPU acceleration (default: True)

    Returns:
        EasyOCR Reader instance
    """
    if languages is None:
        languages = ['en']
    global _reader
    if _reader is None:
        gpu_status = "GPU (CUDA)" if use_gpu else "CPU"
        print(f"Initializing EasyOCR with {gpu_status} (this may take a moment on first run)...")
        _reader = easyocr.Reader(languages, gpu=use_gpu)
    return _reader


def extract_text(img: Image.Image) -> str:
    """Extract text from image using EasyOCR.

    Args:
        img: PIL Image to perform OCR on

    Returns:
        Extracted text as string

    Raises:
        RuntimeError: If OCR fails
    """
    try:
        reader = get_reader()

        # Convert PIL Image to numpy array
        img_array = np.array(img)

        # Run OCR
        results = reader.readtext(img_array)

        # Extract text from results
        # results is list of ([bbox], text, confidence)
        text_parts = [text for (bbox, text, conf) in results]

        return ' '.join(text_parts).strip()

    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}") from e


def extract_text_single_line(img: Image.Image) -> str:
    """Extract text from single-line image using EasyOCR.

    Optimized for single lines (like rank, name, power fields).

    Args:
        img: PIL Image containing single line of text

    Returns:
        Extracted text as string
    """
    reader = get_reader()
    img_array = np.array(img)

    # For single line, we just want the text
    results = reader.readtext(img_array, detail=0)  # detail=0 returns just text

    if results:
        return ' '.join(results).strip()
    return ""


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