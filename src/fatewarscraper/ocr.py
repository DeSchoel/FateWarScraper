from PIL import Image
import pytesseract

# Set this path if `tesseract --version` does NOT work in your terminal:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def image_to_text(img: Image.Image) -> str:
    # Simple OCR first; we will tune later
    return pytesseract.image_to_string(img, config="--psm 6")
