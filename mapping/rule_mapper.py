def rule_map(question, modules):
    question = question.lower()
    scores = {}

    for module in modules:
        score = 0
        for kw in module["content"]:
            if kw.lower() in question:
                score += 1

        scores[module["module_name"]] = score

    return scores
