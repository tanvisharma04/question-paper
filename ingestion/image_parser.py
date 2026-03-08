import os
from PIL import Image
import pytesseract


def load_image(image_path):
    """
    Loads a single image safely.
    """
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        raise RuntimeError(f"Failed to load image {image_path}: {e}")


def extract_text_from_image(image_path, lang="eng"):
    """
    Performs OCR on a single image.
    """
    img = load_image(image_path)
    text = pytesseract.image_to_string(img, lang=lang)
    return text


def extract_text_from_images(image_dir, lang="eng"):
    """
    Performs OCR on all images in a directory.
    Images are processed in sorted order (page_1, page_2, ...).
    """
    full_text = []

    for file in sorted(os.listdir(image_dir)):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".tiff")):
            path = os.path.join(image_dir, file)
            text = extract_text_from_image(path, lang)
            full_text.append(text)

    return "\n".join(full_text)

