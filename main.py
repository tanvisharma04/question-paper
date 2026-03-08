from ingestion.pdf_parser import pdf_to_images
from ingestion.ocr_engine import image_to_text
from ingestion.text_cleaner import clean_text
from mapping.hybrid_mapper import hybrid_map
from analysis.weightage_stats import calculate_weightage
from config import DEFAULT_MODULES
import re

module = DEFAULT_MODULES



PDF_PATH = "data/raw/PP(5th)Dec2023.pdf"
IMG_DIR = "data/images"

images = pdf_to_images(PDF_PATH, IMG_DIR, poppler_path=r"C:\poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin")

page_texts = image_to_text(images)

for page in page_texts:
    print(page["page"])

print("Text Cleaned")

cleaned_pages = clean_text(page_texts)

for page in cleaned_pages:
    print(f"PAGE {page['page']}")
    print(page["clean_text"][:300])

def assign_marks(text):
    text = text.lower()

    # Section A (a) to (j)
    if re.match(r"^\s*[a-j]\)", text):
        return 2

    # Section B (Q2-Q6)
    if re.match(r"^\s*[2-6]\.", text):
        return 5

    # Section C (Q7-Q9)
    if re.match(r"^\s*[7-9]\.", text):
        return 10

    return 0


questions = []
for page in cleaned_pages:
    lines = page["clean_text"].split("\n")

    for line in lines:
        line = line.strip()

        if re.search(r"^\s*[a-j]\)|^\s*[2-9]\.", line):
            questions.append({
                "text": line,
                "marks": assign_marks(line)
            })


print("\n--- Question -> Module Mapping ---\n")

mapped_questions = []
for q in questions:
    result = hybrid_map(q["text"], module)

    mapped_questions.append({
    "question_text": q["text"],
    "module_scores": result["scores"],
    "marks": q["marks"]
    })


    print(f"\nQ: {q['text']}")
    print(f"\n-> Module Scores: {result['scores']}")
    print("-" * 50)

print("\n--- DEBUG QUESTIONS ---")
for q in mapped_questions:
    print(q["marks"], q["question_text"][:60])


weightage = calculate_weightage(mapped_questions, module)

print("\n--- Module-wise Weightage ---\n")
for mod_name, marks in weightage.items():
    print(f"\n{mod_name}: {marks} marks")

