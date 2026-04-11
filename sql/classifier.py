
def classify_query(query):
    q = query.lower()

    if "json_extract" in q:
        return "json_filter"

    if "join" in q:
        return "join_heavy"

    if "group by" in q or "count" in q:
        return "aggregation"

    if "select *" in q:
        return "full_scan"

    if "where" not in q:
        return "no_filter"

    return "performance_analysis"
