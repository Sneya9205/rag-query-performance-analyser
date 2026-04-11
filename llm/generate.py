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
        model="phi3",
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
        Available tools:

        1. analyze_query(query)
        2. detect_anomaly(query)
        3. suggest_optimization(query)
        """

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
        return {
            "type": "llm_response",
            "result": parsed
        }

    except json.JSONDecodeError:
        return {
            "type": "error",
            "raw_output": output
        }