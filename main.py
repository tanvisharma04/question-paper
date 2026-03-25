from ingestion.pdf_parser import pdf_to_images
from ingestion.ocr_engine import image_to_text
from ingestion.text_cleaner import clean_text
from mapping.hybrid_mapper import hybrid_map
from mapping.module_schema import parse_modules
from analysis.weightage_stats import calculate_weightage
import re
from ingestion.text_cleaner import combine_pages
from ingestion.ques_extraction import extract_questions

import os
import streamlit as st


st.set_page_config(page_title="PDF Question Analyzer", layout="wide")
st.title("PDF Question Analyzer")

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

        modules = parse_modules(course_module)

        pdf_files = []

        for uploaded_file in uploaded_files:

            dest_path = os.path.join(RAW_DIR, uploaded_file.name)

            with open(dest_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            pdf_files.append(dest_path)

        all_images = []

        with st.spinner("Converting PDFs to images..."):

            for pdf_path in pdf_files:

                images = pdf_to_images(
                    pdf_path,
                    IMG_DIR,
                    poppler_path=r"C:\poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin"
                )

                all_images.extend(images)

        with st.spinner("Running OCR on images..."):

            page_texts = image_to_text(all_images)

        st.success("Text Extraction Complete")

        with st.spinner("Cleaning extracted text..."):

            cleaned_pages = clean_text(page_texts)

        # Combine pages to single text
        full_text = combine_pages(cleaned_pages)

        # Extract questions
        questions = extract_questions(full_text)

        st.success("Questions Extracted")

        mapped_questions = []

        with st.spinner("Mapping questions to modules..."):

            for q in questions:

                result = hybrid_map(q["question"], modules)

                mapped_questions.append({
                    "question_text": q["question"],
                    "module_scores": result["scores"],
                    "marks": q.get("marks") if q.get("marks") is not None else 5
                })


        weightage = calculate_weightage(mapped_questions, modules)

        col1, col2 = st.columns([1,1])

        with col1:

            st.subheader("Module-wise Weightage")
            
            total_marks = sum(weightage.values())

            for mod_name, marks in weightage.items():
                if total_marks > 0:
                    pct = (marks / total_marks) * 100
                    display_val = f"{pct:.1f}%"
                else:
                    display_val = f"0%"
                st.metric(label=mod_name, value=display_val)

        with col2:

            st.subheader("Mapped Questions")

            for q in mapped_questions:

                with st.expander(
                    f"{q['marks']} Marks - {q['question_text'][:50]}..."
                ):

                    st.write("Full Question:", q['question_text'])
                    st.write("Assigned Marks:", q['marks'])
                    st.write("Module Scores:", q['module_scores'])
