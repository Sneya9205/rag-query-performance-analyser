def format_plan(plan_rows):
    return "\n".join(
        [" | ".join(str(col) for col in row) for row in plan_rows]
    )