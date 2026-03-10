from ingestion.pdf_parser import pdf_to_images
from ingestion.ocr_engine import image_to_text
from ingestion.text_cleaner import clean_text
from mapping.hybrid_mapper import hybrid_map
from analysis.weightage_stats import calculate_weightage
from config import DEFAULT_MODULES
import re

import os
import shutil
import tempfile
import streamlit as st

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

st.set_page_config(page_title="PDF Question Analyzer", layout="wide")
st.title("PDF Question Analyzer")

module = DEFAULT_MODULES

IMG_DIR = "data/images"
os.makedirs(IMG_DIR, exist_ok=True)

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

uploaded_files = st.file_uploader("Upload EXACTLY 3 Question Paper PDFs", type=["pdf"], accept_multiple_files=True)
course_module = st.text_area("Enter the text paragraph for the course module:")

if st.button("Analyze Documents"):
    if not uploaded_files or len(uploaded_files) != 3:
        st.warning("Please upload exactly 3 PDF files.")
    elif not course_module:
        st.warning("Please enter the course module text.")
    else:
        pdf_files = []
        for uploaded_file in uploaded_files:
            dest_path = os.path.join(RAW_DIR, uploaded_file.name)
            with open(dest_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            pdf_files.append(dest_path)

        all_images = []
        with st.spinner("Converting PDFs to images..."):
            for pdf_path in pdf_files:
                images = pdf_to_images(pdf_path, IMG_DIR, poppler_path=r"C:\poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin")
                all_images.extend(images)

        with st.spinner("Running OCR on images..."):
            page_texts = image_to_text(all_images)

        st.success("Text Extraction Complete")

        with st.spinner("Cleaning extracted text..."):
            cleaned_pages = clean_text(page_texts)


        questions = []
        for page in cleaned_pages:
            lines = page["clean_text"].split("\n")

            for line in lines:
                line = line.strip()

                # Basic check to skip instruction lines
                lower_line = line.lower()
                if "section" in lower_line and "contains" in lower_line:
                    continue

                if re.search(r"^\s*[a-j]\)|^\s*[2-9]\.", line):
                    questions.append({
                        "text": line,
                        "marks": assign_marks(line)
                    })


        mapped_questions = []
        with st.spinner("Mapping questions to modules..."):
            for q in questions:
                result = hybrid_map(q["text"], module)

                mapped_questions.append({
                    "question_text": q["text"],
                    "module_scores": result["scores"],
                    "marks": q["marks"]
                })



        st.header("Aggregated Results")
        weightage = calculate_weightage(mapped_questions, module)

        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Module-wise Weightage")
            for mod_name, marks in weightage.items():
                st.metric(label=mod_name, value=f"{marks} marks")
        
        with col2:
            st.subheader("Mapped Questions")
            for q in mapped_questions:
                with st.expander(f"{q['marks']} Marks - {q['question_text'][:50]}..."):
                    st.write("**Full Question:**", q['question_text'])
                    st.write("**Assigned Marks:**", q['marks'])
                    st.write("**Module Scores:**", q['module_scores'])

