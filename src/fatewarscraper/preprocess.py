"""Image preprocessing for OCR."""

from PIL import Image, ImageEnhance
import numpy as np


def crop_image(img: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """Crop image to specified rectangle.

    Args:
        img: Source image
        left: Left edge of crop region
        top: Top edge of crop region
        right: Right edge of crop region
        bottom: Bottom edge of crop region

    Returns:
        Cropped PIL Image
    """
    return img.crop((left, top, right, bottom))


def preprocess_for_ocr(img: Image.Image, upscale: int = 2) -> Image.Image:
    """Preprocess image for better OCR accuracy.

    Refined Pipeline:
    1. Grayscale
    2. Rescale (upscale x) to make characters larger for OCR
    3. Sharpness & Contrast enhancement
    4. (No destructive thresholding for EasyOCR)
    """
    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')

    # Upscale - larger text is easier for OCR to segment correctly
    w, h = img.size
    img = img.resize((w * upscale, h * upscale), Image.Resampling.LANCZOS)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # Enhance sharpness
    sharpener = ImageEnhance.Sharpness(img)
    img = sharpener.enhance(2.0)

    return img


def crop_member_list_first(img: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Crop the FIRST screenshot which includes podium + regular rows.

    Based on measurements:
    - Podium (ranks 1-3): x: 235-1180, y: 360-465
    - Rank 4: x: 235-1180, y: 475-555
    - Rank 5: x: 235-1180, y: 565-645

    Returns two images: podium crop and regular rows crop

    Args:
        img: Full game window screenshot (first capture)

    Returns:
        Tuple of (podium_image, regular_rows_image)
    """
    # Podium region (ranks 1-3)
    podium = crop_image(img, left=235, top=360, right=1180, bottom=465)

    # Regular rows (ranks 4-5 in first screenshot)
    regular = crop_image(img, left=235, top=475, right=1180, bottom=645)

    return podium, regular


def crop_member_list_scrolled(img: Image.Image) -> Image.Image:
    """Crop member list from scrolled screenshots (no podium).

    After scrolling, the member rows appear at different y-coordinates.
    Based on measurements:
    - First row: y ~ 180
    - Last row: y ~ 618

    Bottom extended by ~3% to show more content at the bottom.

    Args:
        img: Full game window screenshot (after scrolling)

    Returns:
        Cropped member list image
    """
    # Crop the member list region
    # Bottom at 660 (slightly more than 649) to ensure the last row is fully captured
    return crop_image(img, left=235, top=170, right=1180, bottom=660)