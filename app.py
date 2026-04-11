from flask import Flask, request, jsonify
import time
from rag.retrieve import retrieve_case
from llm.generate import generate_response
from logger import log_event
from mcp.tools import execute_tool

app = Flask(__name__)

from mcp.tools import TOOL_REGISTRY
from rag.cache import cache_process_query
@app.route("/api/v1/tools")
def list_tools():

    return jsonify({
        "tools":
            list(TOOL_REGISTRY.keys())
    })
@app.route("/ask", methods=["POST"])
def ask():
    start=time.time()
    data = request.json

    user_query = data.get("query")
    
    if not user_query:
        return jsonify({
            "error": "No query provided"
        }), 400
    log_event(f"Query received: {user_query}")

    sql_result =  execute_tool(
        "analyze_sql_performance",
        {"query": user_query}
    )


    if sql_result["type"] == "sql_error":
        return jsonify(sql_result)

    retrieved = cache_process_query(user_query)
    retrieved_query =retrieved["cases"][0]
    # Generate LLM response
    response = generate_response(
        user_query,
        retrieved_query
    )   
    
    latency = time.time() - start

    return jsonify({
        "query": user_query,
        "response": response,
        "score": retrieved["score"],
        "latency": latency
    })

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