from flask import Flask, request, jsonify

from rag.retrieve import retrieve_case
from llm.generate import generate_response

app = Flask(__name__)


@app.route("/ask", methods=["POST"])
def ask():

    data = request.json

    user_query = data.get("query")

    if not user_query:
        return jsonify({
            "error": "No query provided"
        }), 400

    # Retrieve similar case
    retrieved = retrieve_case(user_query)[0]

    # Generate LLM response
    response = generate_response(
        user_query,
        retrieved
    )

    return jsonify({
        "query": user_query,
        "response": response
    })


if __name__ == "__main__":
    app.run(debug=True)