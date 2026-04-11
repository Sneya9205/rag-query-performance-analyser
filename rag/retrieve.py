from tracemalloc import start

import faiss
import json
import numpy as np
import time
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("rag/case_index.faiss")

# Load stored texts
with open("rag/case_texts.json", "r") as f:
    texts = json.load(f)

def normalize_case(case):
    return {
        "case_id": case.get("case_id", ""),
        "description": case.get("description", ""),
        "query": case.get("query", ""),
        "latency": case.get("latency", ""),
        "context": case.get("context", ""),
        "root_cause": case.get("root_cause", ""),
        "suggestion": case.get("suggestion", ""),
        "tags": case.get("tags", []),
    }
def retrieve_case(query, k=1):
    # Convert query to embedding
    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding)

    # Search similar cases
    distances, indices = index.search(query_embedding, k)

    score = float(distances[0][0])

    results = []
    print("Retrieved Cases:\n")
    for i in indices[0]:
        print(texts[i])
        results.append(texts[i])

    result={
        "cases": results,
        "score": score
        }
    return result