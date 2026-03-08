from mapping.rule_mapper import rule_map
from mapping.semantic_mapper import semantic_map

def hybrid_map(question, modules):
    rule_scores = rule_map(question, modules)
    semantic_scores = semantic_map(question, modules)

    final_scores = {}

    for m in modules:
        name = m["module_name"]
        r = rule_scores.get(name, 0)
        s = semantic_scores.get(name, 0)

        final_scores[name] = (0.6 * r) + (0.4 * s)

    return {
        "scores": final_scores
    }
