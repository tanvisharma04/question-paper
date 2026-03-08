import pytesseract
from PIL import Image

def image_to_text(image_path, lang="eng"):
    page_texts = []

    for idx, img_path in enumerate(image_path):
        img = Image.open(img_path)

        text = pytesseract.image_to_string(img,lang=lang,config="--oem 3 --psm 6")

        page_texts.append({
            "page": idx + 1,
            "text": text
        })

    return page_texts
