from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_map(question, modules):
    q_emb = model.encode(question, convert_to_tensor=True)

    scores = {}
    for module in modules:
        m_emb = model.encode(module["description"], convert_to_tensor=True)
        similarity = util.cos_sim(q_emb, m_emb).item()
        scores[module["module_name"]] = similarity

    return scores
