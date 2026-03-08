def calculate_weightage(mapped_questions, modules):
    module_totals = {m["module_name"]: 0 for m in modules}
    total_marks = 0

    for q in mapped_questions:
        total_marks += q["marks"]

        qst_total_score = sum(q["module_scores"].values())

        if qst_total_score > 0:
            for module, score in q["module_scores"].items():
                module_totals[module] += (score / qst_total_score) * q["marks"]
        else:
            if len(modules) > 0:
                for module in q["module_scores"]:
                    module_totals[module] += (1.0 / len(modules)) * q["marks"]

    # normalize
    if total_marks > 0:
        for m in module_totals:
            module_totals[m] = round((module_totals[m] / total_marks) * 100, 2)

    return module_totals
