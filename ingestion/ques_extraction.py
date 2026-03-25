import re

WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20
}

def extract_questions(text):
    # Detect section headers
    section_pattern = r'(?:^|\n)\s*(Section\s*[-:]?\s*[A-D]|SECTION\s*[-:]?\s*[A-D])'
    
    # Question pattern
    question_pattern = r'(?:^|\n)\s*(Q\.?\s*\d+|\d+[.)]|[a-zA-Z][.)]|[ivxIVX]{1,4}[.)])\s*(.*?)(?=\n\s*(?:Q\.?\s*\d+|\d+[.)]|[a-zA-Z][.)]|[ivxIVX]{1,4}[.)]|Section\s*[-:]?\s*[A-D])|$)'

    # Find all section headers with positions
    sections = [(m.start(), m.group().strip()) for m in re.finditer(section_pattern, text, re.IGNORECASE)]

    matches = list(re.finditer(question_pattern, text, re.IGNORECASE | re.DOTALL))
    questions = []

    current_section = "Unknown"

    for i, match in enumerate(matches, start=1):
        start_pos = match.start()

        # Update section based on position
        for sec_pos, sec_name in sections:
            if start_pos >= sec_pos:
                current_section = sec_name.strip()
            else:
                break

        prefix = match.group(1).strip().lower()
        q = match.group(2).strip()

        # Filter unwanted matches
        if "tech." in q.lower() or "cyber security" in q.lower() or "instructions to candidates" in q.lower():
            continue
        if len(q) < 10:
            continue

        # Assign marks
        marks = None
        if re.match(r"^[a-j]\)", prefix):
            marks = 2
        elif re.match(r"^[2-6]\.", prefix):
            marks = 5
        elif re.match(r"^[7-9]\.", prefix):
            marks = 10

        # Filter instruction text
        instruction_pattern = r'(?i)(section-[a-z].*?contains.*?questions|attempt.*?any.*?questions|questions.*?carrying.*?marks|section-[a-z] is compulsory)'
        if re.search(instruction_pattern, q):
            continue

        q = re.sub(r'\s+', ' ', q)

        questions.append({
            "question_number": i,
            "section": current_section,
            "prefix": prefix,
            "question": q,
            "marks": marks
        })

    return questions