def calculate_weightage(mapped_questions, modules):

    # initialize module marks
    weightage = {m["module_name"]: 0 for m in modules}

    for q in mapped_questions:

        scores = q["module_scores"]
        marks = q["marks"]

        if not scores:
            continue

        # find module with highest score
        best_module = max(scores, key=scores.get)

        # if similarity is extremely low, ignore
        if scores[best_module] <= 0:
            continue

        weightage[best_module] += marks

    return weightage