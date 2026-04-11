import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load dataset
with open("data/cases.json", "r") as f:
    cases = json.load(f)

texts = []

# Convert each case to text
for case in cases:
    text = f"""
    Case ID: {case['case_id']}
    Description: {case['description']}
    Query: {case['query']}
    Latency: {case['latency']}
    Context: {case['context']}
    Root Cause: {case['root_cause']}
    Suggestion: {case['suggestion']}
    Tags: {", ".join(case['tags'])}
    """
    texts.append(text)

# Generate embeddings
embeddings = model.encode(texts)

# Convert to numpy
embeddings = np.array(embeddings)

# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

# Save index
faiss.write_index(index, "rag/case_index.faiss")

# Save texts
with open("rag/case_texts.json", "w") as f:
    json.dump(texts, f)

print("Embedding and FAISS index created successfully.")