from rag.retrieve import retrieve_case
from llm.generate import generate_response

query = "Why is SELECT * slow?"

retrieved = retrieve_case(query)[0]

response = generate_response(query, retrieved)

print("\nLLM Repsponse:\n")
print(response)