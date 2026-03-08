import spacy
from keybert import KeyBERT

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

def extract_course_topics(text):

    semantic_keywords = kw_model.extract_keywords(text, 
                                                 keyphrase_ngram_range=(1, 3), 
                                                 stop_words='english', 
                                                 use_mmr=True, 
                                                 diversity=0.7)
    

    doc = nlp(text)
    noun_phrases = [chunk.text.lower().strip() for chunk in doc.noun_chunks 
                    if len(chunk.text.split()) <= 4] 


    combined_topics = set([kw[0] for kw in semantic_keywords] + noun_phrases)
    
    return sorted(list(combined_topics))


module_text = ""

topics = extract_course_topics(module_text)

print(f"Extracted {len(topics)} potential topics for mapping:")
for t in topics:
    print(f"- {t}")
