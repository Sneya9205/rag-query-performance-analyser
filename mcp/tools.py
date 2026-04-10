TOOL_REGISTRY = {}

def mcp_tool(name, description):
    """Register function as MCP-style tool"""

    def decorator(fn):

        TOOL_REGISTRY[name] = {
            "function": fn,
            "description": description
        }

        return fn

    return decorator


@mcp_tool(
    name="analyze_query",
    description="Analyze SQL query performance patterns"
)
def analyze_query(query_text):

    if "SELECT *" in query_text:
        return {
            "problem": "Full table scan detected",
            "impact": "High latency risk"
        }

    if "JOIN" in query_text:
        return {
            "problem": "Complex JOIN detected",
            "impact": "Medium latency risk"
        }

    return {
        "problem": "General performance issue",
        "impact": "Unknown"
    }


@mcp_tool(
    name="detect_anomaly",
    description="Detect latency anomalies"
)
def detect_anomaly(case_text):

    if "50 seconds" in case_text:
        return {
            "is_anomaly": True,
            "reason": "Latency spike detected"
        }

    return {
        "is_anomaly": False
    }


@mcp_tool(
    name="suggest_optimization",
    description="Suggest SQL optimizations"
)
def suggest_optimization(case_text):

    suggestions = []

    if "SELECT *" in case_text:
        suggestions.append(
            "Avoid SELECT *; fetch required columns"
        )

    if "JSON" in case_text:
        suggestions.append(
            "Add index on JSON field"
        )

    if not suggestions:
        suggestions.append(
            "Review execution plan"
        )

    return {
        "suggestions": suggestions
    }
def execute_tool(tool_name, args):

    tool = TOOL_REGISTRY.get(tool_name)

    if not tool:
        return {
            "error": "Tool not found"
        }

    fn = tool["function"]

    return fn(**args) 