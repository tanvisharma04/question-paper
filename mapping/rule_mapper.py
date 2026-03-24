import re

def rule_map(question, modules):
    question = question.lower()
    # extract words from question
    q_words = set(re.findall(r'\b[a-z]{3,}\b', question))
    
    # basic stop words to ignore
    stop_words = {"the", "and", "for", "with", "are", "this", "that", "from", "how", "what", "explain", "discuss", "describe", "between"}
    
    scores = {}

    for module in modules:
        score = 0
        # extract words from module content
        m_words = set(re.findall(r'\b[a-z]{3,}\b', module["content"].lower()))
        
        for kw in m_words:
            if kw not in stop_words and kw in q_words:
                score += 1

        scores[module["module_name"]] = score

    return scores
