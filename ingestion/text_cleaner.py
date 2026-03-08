import re

def clean_text(pages):
    cleaned_pages = []

    for page in pages:
        text = page["text"]

        # 1. Normalize horizontal whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n+", "\n", text)

        # 2. Fix OCR artifacts 
        # Removes characters that are likely noise but keeps standard punctuation
        # Keeps: A-Z, a-z, 0-9, and punctuation like . , ? ( ) [ ] : / -
        text = re.sub(r"[^a-zA-Z0-9\s.,?():\[\]/ \-]", "", text)

        # 3. Handle common OCR spacing issues
        text = text.replace(" ,", ",").replace(" .", ".")
        
        # 4. Standardize Module/Question headers for easier Regex splitting later
        # Example: Change "Module-1" or "Module_1" to "Module 1"
        text = re.sub(r"(Module|Unit|Chapter)[\s\-_]*(\d+)", r"\1 \2", text, flags=re.IGNORECASE)

        # 5. Trim
        text = text.strip()

        cleaned_pages.append({
            "page": page["page"],
            "clean_text": text
        })

    return cleaned_pages

