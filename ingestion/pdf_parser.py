import pytesseract
import os
from pdf2image import convert_from_path

# Path to poppler's bin folder
poppler_path = r"C:\poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin"

def pdf_to_images(pdf_path, output_dir, dpi=300, poppler_path=None):
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(pdf_path,dpi=dpi,poppler_path=poppler_path)

    image_paths = []
    for i, img in enumerate(images):
        path = os.path.join(output_dir, f"page_{i+1}.png")
        img.save(path, "PNG")
        image_paths.append(path)

    return image_paths


