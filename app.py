import streamlit as st
import os
import tempfile
import re
import json

from ingestion.pdf_parser import pdf_to_images
from ingestion.ocr_engine import image_to_text
from ingestion.text_cleaner import clean_text
from mapping.hybrid_mapper import hybrid_map
from analysis.weightage_stats import calculate_weightage

from config import DEFAULT_MODULES

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

def process_pdf(pdf_path, img_dir, poppler_path, current_module_config):
    with st.spinner("Converting PDF to images..."):
        images = pdf_to_images(pdf_path, img_dir, poppler_path=poppler_path)
    
    with st.spinner("Running OCR on images..."):
        page_texts = image_to_text(images)
    
    with st.spinner("Cleaning extracted text..."):
        cleaned_pages = clean_text(page_texts)

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

    with st.spinner("Mapping questions to modules..."):
        mapped_questions = []
        for q in questions:
            result = hybrid_map(q["text"], current_module_config)
            mapped_questions.append({
                "question_text": q["text"],
                "module_scores": result["scores"],
                "marks": q["marks"]
            })
            
    weightage = calculate_weightage(mapped_questions, current_module_config)
    
    return mapped_questions, weightage

st.set_page_config(page_title="PDF Question Analyzer", layout="wide")

st.title("PDF Question Analyzer")
st.markdown("Upload a question paper PDF to extract questions, map them to modules, and calculate weightage.")

# Make sure image directory exists
IMG_DIR = "data/images"
os.makedirs(IMG_DIR, exist_ok=True)

# Poppler path configuration
poppler_path = st.sidebar.text_input("Poppler Path", value=r"C:\poppler\Release-25.12.0-0\poppler-25.12.0\Library\bin")

st.sidebar.subheader("Custom Modules")
st.sidebar.markdown("By default, a hardcoded Python syllabus is used. Upload a JSON file or paste text below to use a custom syllabus.")

input_method = st.sidebar.radio("Input Method", ["JSON File", "Text Input"])
active_module_config = DEFAULT_MODULES

if input_method == "JSON File":
    uploaded_json = st.sidebar.file_uploader("Upload Modules JSON (Optional)", type=["json"])
    if uploaded_json is not None:
        try:
            active_module_config = json.load(uploaded_json)
            st.sidebar.success("Loaded custom modules successfully!")
        except Exception as e:
            st.sidebar.error(f"Error loading JSON file: {e}")
else:
    text_input = st.sidebar.text_area("Paste Modules Text", help="Format: Module Name: topic1, topic2, topic3", height=200)
    if text_input:
        parsed_modules = []
        lines = text_input.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                mod_name, topics = line.split(':', 1)
                topics_list = [t.strip() for t in topics.split(',') if t.strip()]
                parsed_modules.append({
                    "module_name": mod_name.strip(),
                    "content": topics_list,
                    "description": ""
                })
        if parsed_modules:
            active_module_config = parsed_modules
            st.sidebar.success("Parsed text modules successfully!")

uploaded_files = st.file_uploader("Upload Question Paper PDFs (Min 3 required)", type=["pdf"], accept_multiple_files=True)

if st.button("Analyze Documents"):
    if len(uploaded_files) < 3:
        st.warning("Please upload at least 3 PDF files.")
    else:
        all_mapped_questions = []
        # Support default modules and newly parsed modules
        overall_weightage = {}
        for mod in active_module_config:
            overall_weightage[mod["module_name"]] = 0
            
        for uploaded_file in uploaded_files:
            st.write(f"### Processing {uploaded_file.name}")
            # Save uploaded file to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(uploaded_file.getvalue())
                tmp_pdf_path = tmp_pdf.name
                
            try:
                mapped_questions, weightage = process_pdf(tmp_pdf_path, IMG_DIR, poppler_path, active_module_config)
                
                all_mapped_questions.extend(mapped_questions)
                
                for mod_name, marks in weightage.items():
                    if mod_name in overall_weightage:
                        overall_weightage[mod_name] += marks
                    else:
                        overall_weightage[mod_name] = marks
                        
            except Exception as e:
                st.error(f"An error occurred while processing {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)
                    
        st.success("Processing complete!")
        st.header("Aggregated Results")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Overall Module-wise Weightage")
            for mod_name, marks in overall_weightage.items():
                st.metric(label=mod_name, value=f"{marks} marks")
                
        with col2:
            st.subheader("All Mapped Questions")
            for i, q in enumerate(all_mapped_questions):
                with st.expander(f"{q['marks']} Marks - {q['question_text'][:50]}..."):
                    st.write("**Full Question:**", q['question_text'])
                    st.write("**Assigned Marks:**", q['marks'])
                    st.write("**Module Scores:**", q['module_scores'])
