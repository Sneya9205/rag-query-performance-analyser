import ollama
import json
from mcp.tools import execute_tool


def generate_response(user_query, retrieved_case):

    TOOLS_DESCRIPTION = """
        Available tools:

        1. analyze_query(query_text)
        2. detect_anomaly(case_text)
        3. suggest_optimization(case_text)

        If tool is needed, return:

        <tool_call>
        {
        "tool": "tool_name",
        "args": {...}
        }
        </tool_call>

        Otherwise return analysis JSON.
        """
    prompt = f"""
    You are a database performance expert.

    {TOOLS_DESCRIPTION}

    User Query:
    {user_query}

    Retrieved Case:
    {retrieved_case}

    Return JSON only.
    """
    
    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    output = response["message"]["content"]
    if "<tool_call>" in output:

        json_text = output.split(
            "<tool_call>"
        )[1].split(
            "</tool_call>"
        )[0]

        tool_data = json.loads(json_text)

        tool_result = execute_tool(
            tool_data["tool"],
            tool_data["args"]
        )

        return {
            "tool_used": tool_data["tool"],
            "tool_result": tool_result
        }

    return output

