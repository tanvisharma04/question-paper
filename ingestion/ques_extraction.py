import re
def extract_questions(text):

    pattern = r'(?:Q\.?\s*\d+|\b\d+[.)])\s*(.*?)(?=(?:Q\.?\s*\d+|\b\d+[.)])|$)'

    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)

    questions = []

    for i, q in enumerate(matches, start=1):

        q = q.strip()

        # remove marks
        q = re.sub(r'\(\s*\d+\s*marks?\s*\)', '', q, flags=re.I)

        # normalize spacing
        q = re.sub(r'\s+', ' ', q)

        # filter small fragments
        if len(q) < 10:
            continue

        # filter instructional text
        instruction_pattern = r'(?i)(section-[a-z].*?contains.*?questions|attempt.*?any.*?questions|questions.*?carrying.*?marks)'
        if re.search(instruction_pattern, q):
            continue

        questions.append({
            "question_number": i,
            "question": q
        })

    return questions