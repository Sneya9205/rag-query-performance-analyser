from flask import Flask, request, jsonify,render_template
import time
from rag.retrieve import retrieve_case
from llm.generate import generate_response
from logger import log_event
from mcp.tools import execute_tool
from flask_cors import CORS
from mcp.tools import TOOL_REGISTRY
from rag.cache import cache_process_query
import json
import re
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")
def extract_from_case(case_text, field):

    if not case_text:
        return ""

    match = re.search(
        rf"{field}:\s*(.*)",
        case_text,
        re.IGNORECASE
    )

    return match.group(1).strip() if match else ""
def get_field(llm_output, similar_case, llm_key, rag_key):

    value = llm_output.get(llm_key)

    if value:
        return value

    return extract_from_case(
        similar_case,
        rag_key
    )
def build_response(query, case_type, plan, rag_result, llm_output,query_latency,latency, tool_result=None, anomaly_flag=False):

    llm_output = llm_output or {}
    rag_result = rag_result or {}

    cases = rag_result.get("cases") or []
    similar_case = cases[0] if len(cases) > 0 else None
    '''
    return {
        "query": query,
        "query_execution_latency": query_latency,
        "case_type": case_type,

        "problem": llm_output.get("problem", ""),
        "root_cause": llm_output.get("root_cause", ""),
        "suggestion": llm_output.get("suggestion", ""),

        "execution_plan": plan,

        "rag_score": rag_result.get("score"),
        

        "llm_output": llm_output,

        "tool_result": tool_result,

        "anomaly": anomaly_flag,

        "confidence": llm_output.get("confidence", "medium"),
        "latency": latency
    }'''
    problem = get_field(
        llm_output,
        similar_case,
        "issue",
        "Description"
    )

    root_cause = get_field(
        llm_output,
        similar_case,
        "performance_risk",
        "Root Cause"
    )

    suggestion = get_field(
        llm_output,
        similar_case,
        "suggestion",
        "Suggestion"
    )
    performance_risk = (
    llm_output.get("performance_risk")
    or extract_from_case(similar_case, "Latency")
    or ""
    )
    return  {
    "query": query,
    "case_type": case_type,
    "latency": latency,
    "query_execution_latency": query_latency,
    "similar_case": similar_case,
    "analysis": {
            "problem": problem,

            "root_cause": root_cause,

            "suggestion": suggestion,

            "performance_risk": performance_risk,
            "confidence": llm_output.get("confidence", "medium"),
            "performance_risk": llm_output.get("performance_risk", ""),
            "complexity": llm_output.get("complexity", ""),
            "bottleneck_type": llm_output.get("bottleneck_type", ""),
            "priority": llm_output.get("priority", ""),
            "index_recommendation": llm_output.get("index_recommendation", ""),
            "risk_summary": llm_output.get("risk_summary", "")
        },

    "sql": {
        "execution_plan": plan,
        "anomaly": anomaly_flag
    },

    "rag": {
        "score": rag_result.get("score"),
        "similar_case": rag_result.get("cases", [None])[0]
    },

    "tool": tool_result,

    "llm_raw": llm_output
    }


def clean_llm_output(output):
    if isinstance(output, dict):
        return output

    if not output:
        return {}

    # remove markdown
    output = re.sub(r"```json|```", "", output).strip()

    try:
        return json.loads(output)
    except:
        return {"raw": output}
@app.route("/api/v1/tools")
def list_tools():

    return jsonify({
        "tools":
            list(TOOL_REGISTRY.keys())
    })

@app.route("/ask", methods=["POST"])
def ask():
    start = time.time()

    data = request.json
    user_query = data.get("query")

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    log_event(f"Query received: {user_query}")

    # STEP 1: SQL analysis
    sql_start = time.time()
    sql_result = execute_tool(
        "analyze_sql_performance",
        {"query": user_query}
    )
    sql_latency = time.time() - sql_start

    if sql_result["type"] == "sql_error":
        return jsonify(sql_result)

    # STEP 2: RAG retrieval
    retrieved = cache_process_query(user_query)
    cases = retrieved.get("cases", [])
    retrieved_query = cases[0] if cases else ""

    # STEP 3: LLM generation
    llm_result = generate_response(
        user_query,
        retrieved_query
    )
    primary_llm = clean_llm_output(llm_result)

    # Clean tool LLM output
    tool_llm = clean_llm_output(
        sql_result.get("llm_output")
    )

    # Choose valid one
    if "issue" in primary_llm:
        print("Using primary LLM output")
        final_llm = primary_llm
    elif "issue" in tool_llm:
        print("Using tool LLM output")
        final_llm = tool_llm
    else:
        final_llm = {}

    # STEP 4: anomaly flag (simple example)
    anomaly_flag = "50" in str(sql_result.get("plan", ""))

    # STEP 5: final response
    latency = time.time() - start

    final = build_response(
        query=user_query,
        case_type=sql_result["type"],
        plan=sql_result.get("plan", ""),
        rag_result=retrieved,
        llm_output=final_llm,
        query_latency=sql_latency,
        latency=latency,
        tool_result=sql_result,  
        anomaly_flag=anomaly_flag
    )
    
    print("Completed processing in", latency, "seconds");
    print("Final response:", final_llm)
    return jsonify(final)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    query = data["query"]

    result = execute_tool(
        "analyze_sql_performance",
        {"query": query}
    )

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)