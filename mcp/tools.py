TOOL_REGISTRY = {}
import json
import re

def mcp_tool(name, description):
    """Register function as MCP-style tool"""

    def decorator(fn):

        TOOL_REGISTRY[name] = {
            "function": fn,
            "description": description
        }

        return fn

    return decorator

import sqlparse


@mcp_tool(
    name="check_sql_syntax",
    description="Validate SQL syntax"
)
def check_sql_syntax(query):

    try:

        parsed = sqlparse.parse(query)

        if not parsed:
            return {
                "valid": False,
                "error": "Invalid SQL syntax"
            }

        return {
            "valid": True
        }

    except Exception:

        return {
            "valid": False,
            "error": "Parsing failed"
        }
@mcp_tool(
    name="analyze_query",
    description="Analyze SQL query performance patterns"
)
def analyze_query(query):

    if "SELECT *" in query:
        return {
            "problem": "Full table scan detected",
            "impact": "High latency risk"
        }

    if "JOIN" in query:
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
def detect_anomaly(query):

    if "50 seconds" in query:
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
def suggest_optimization(query):

    suggestions = []

    if "SELECT *" in query:
        suggestions.append(
        "Specify required columns instead of SELECT *"
    )

    if "JOIN" in query:
        suggestions.append(
            "Add index on JOIN columns"
        )

    if "ORDER BY" in query:
        suggestions.append(
            "Index ORDER BY column"
        )

    if "WHERE" not in query:
        suggestions.append(
            "Add WHERE clause to reduce scan"
        )
    if "JSON" in query:
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

