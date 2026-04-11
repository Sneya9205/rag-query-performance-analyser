import ollama
import json
from mcp.tools import execute_tool
from pybreaker import CircuitBreaker
import re 
llm_breaker = CircuitBreaker(
    fail_max=3,
    reset_timeout=30
)

def call_llm(prompt):
    return llm_breaker.call(
        ollama.chat,
        model="phi3:mini",
        messages=[{"role": "user", "content": prompt}]
    )
def clean_json_output(text):

    if "```" in text:
        text = text.replace("```json", "")
        text = text.replace("```", "")

    return text.strip()
import json


def extract_tool_call(output):
    """
    Strictly extract tool_call JSON only if fully valid.
    """

    match = re.search(r"<tool_call>(.*?)</tool_call>", output, re.DOTALL)

    if not match:
        return None

    json_text = match.group(1).strip()

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return None

    # basic schema validation
    if "tool" not in data:
        return None

    return data

def generate_response(user_query, retrieved_case):

    TOOLS_DESCRIPTION = """
    Available tools and when to use them:

    1. check_sql_syntax(query)
    Use when:
    - Query may contain syntax errors
    - Query fails parsing

    2. analyze_query(query)
    Use when:
    - Query contains SELECT *
    - Query contains JOIN
    - Query scans large tables
    - Query structure suggests performance risk

    3. detect_anomaly(plan)
    Use when:
    - Execution plan contains full table scan
    - Latency risk appears unusually high

    4. suggest_optimization(query)
    Use when:
    - Query contains SELECT *
    - Query contains JSON extraction
    - Query contains ORDER BY
    - Query contains JOIN
    - Query lacks WHERE clause

    Always choose the most relevant tool.
    Return exactly one tool call.
    """
    prompt = f"""
    You are a SQL performance expert.
    {TOOLS_DESCRIPTION}
    Analyze the SQL query risk.

    QUERY:
    {user_query}

    SIMILAR CASE:
    {retrieved_case}

    Return ONLY valid JSON.

    JSON FORMAT:

    {{
    "issue": "...",
    "root_cause": "...",
    "suggestion": "...",

    "performance_risk": "low|medium|high",
    "complexity": "low|medium|high",
    "bottleneck_type": "scan|join|index|json|sort|unknown",

    "priority": "low|medium|high",
    "index_recommendation": "...",

    "risk_summary": "...",
    "confidence": 0.0
    }}
    """
    '''
    prompt = f"""
        You are a strict tool-calling system.

        {TOOLS_DESCRIPTION}

        RULES:
        - If tool is needed, output ONLY:

        <tool_call>
        {{
        "tool": "tool_name",
        "args": {{"query": "..."}}
        }}
        </tool_call>

        - No extra text allowed.
        - Otherwise return valid JSON only.

        User Query:
        {user_query}

        Retrieved Case:
        {retrieved_case}
    """
    '''
    response = call_llm(prompt)
    output = response["message"]["content"]

    # TOOL FIRST
    tool_data = extract_tool_call(output)
    
    if tool_data:
        result = execute_tool(
            tool_data["tool"],
            tool_data.get("args", {})
        )

        return {
            "type": "tool_result",
            "tool_used": tool_data["tool"],
            "result": result
        }

    # JSON FALLBACK
    cleaned = clean_json_output(output)

    try:
        parsed = json.loads(cleaned)

        parsed = {
            "issue": parsed.get("issue", ""),
            "performance_risk": parsed.get("performance_risk", ""),
            "suggestion": parsed.get("suggestion", ""),
            "optimized_query": parsed.get("optimized_query", "")
        }
        return {
            "type": "llm_response",
            "result": parsed
        }

    except json.JSONDecodeError:
        return {
            "type": "error",
            "raw_output": output
        }

def analyze_with_llm(query, plan_text):
    prompt = f"""
You are a SQL performance expert.

QUERY:
{query}

EXPLAIN QUERY PLAN:
{plan_text}

Return JSON:
{{
  "issue": "...",
  "performance_risk": "...",
  "suggestion": "...",
  "optimized_query": "..."
}}
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]