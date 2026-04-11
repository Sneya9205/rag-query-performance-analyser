from sql.planner import get_query_plan
from sql.validator import format_plan
from sql.classifier import classify_query

def sql_performance_agent(query):
    from llm.generate import analyze_with_llm
    case_type = classify_query(query)
    # STEP 1: get plan
    result = get_query_plan(query)

    if not result["valid"]:
        return {
            "type": "sql_error",
            "error": result["error"]
        }

    # STEP 2: format plan
    plan_text = format_plan(result["plan"])

    # STEP 3: LLM analysis
    llm_output = analyze_with_llm(query, plan_text)

    return {
        "type": case_type,
        "query": query,
        "plan": plan_text,
        "llm_output": llm_output
    }