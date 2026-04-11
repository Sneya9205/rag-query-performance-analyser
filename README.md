#  SQL Performance Intelligence System (RAG + LLM + MCP Tools)

##  Overview

This project is an **AI-powered SQL performance analysis system** that combines:

*  **RAG (Retrieval-Augmented Generation)** using FAISS
*  **LLM reasoning (Phi-3 via Ollama)**
*  **MCP-style tool execution layer**
*  **SQL query analysis engine**
*  **Structured performance insights generator**

---

#  System Architecture

<img width="680" height="509" alt="architecture2 drawio" src="https://github.com/user-attachments/assets/d55de324-bea8-4195-8046-315ea1d0d1ce" />

##  High-Level Flow

```
User Query
   ↓
Logging Layer (request tracking)
   ↓
SQL Analysis (MCP Tools)
   ↓
Caching Layer (RAG cache check)
   ↓
RAG Retrieval (FAISS + cases.json)
   ↓
LLM Reasoning (Phi-3)
   ↓
Optional Tool Execution (MCP)
   ↓
Response Builder
   ↓
Logging Layer (latency + response tracking)
   ↓
Frontend Display
```

---

##  Core Components

### 1. SQL Analysis Layer (MCP Tools)

Responsible for deterministic SQL evaluation:

* Syntax validation (using `sqlparse`)
* Execution plan simulation / analysis
* Pattern detection:

  * Full table scan
  * Missing index
  * Complex joins
  * Subqueries

### Output Example:

```json
{
  "type": "full_scan",
  "plan": "SCAN TABLE users"
}
```

---

### 2. RAG Layer (FAISS + Dataset)

Uses semantic search to retrieve similar past cases.

#### Dataset:

`cases.json`

Each case includes:

* Query pattern
* Latency
* Root cause
* Context
* Optimization suggestion

#### Process:

1. Convert query → embedding (SentenceTransformer)
2. Search FAISS index
3. Retrieve top-k similar cases

#### Output:

```json
{
  "cases": [...],
  "score": 1.52
}
```

---

### 3. LLM Layer (Phi-3 via Ollama)

The reasoning engine that:

* Explains SQL performance issues
* Uses SQL + RAG context
* Suggests optimizations
* Optionally triggers tool calls

#### Supports:

* Direct structured JSON output
* Tool invocation via `<tool_call>` format

---

### 4. MCP Tool Layer

Acts as the **execution layer for the LLM**.

Available tools:

* `analyze_query`
* `detect_anomaly`
* `suggest_optimization`
* `check_sql_syntax`

#### Behavior:

* LLM requests tool usage
* Backend executes tool
* Result returned to system

---

### 5. Response Builder

Combines outputs from all layers:

* SQL analysis result
* RAG match
* LLM reasoning
* Tool outputs
* Latency metrics

#### Final Output Format:

```json
{
  "query": "...",
  "case_type": "full_scan",

  "problem": "...",
  "root_cause": "...",
  "suggestion": "...",

  "execution_plan": "...",

  "rag_score": 1.52,
  "similar_case": "...",

  "tool_result": {...},

  "latency": 120.5
}
```

### 6. Logging Layer (Observability)
This layer tracks system activity across the pipeline.
#### Responsibilities
•	Log incoming queries
•	Track execution flow
•	Record SQL analysis latency
•	Track LLM and tool usage
•	Store error logs
#### Example
log_event(f"Query received: {user_query}")
log_event(f"SQL analysis latency: {latency}")
#### Why It Matters
•	Helps debugging issues
•	Enables performance monitoring
•	Provides audit visibility
________________________________________
### 7. Caching Layer (Performance Optimization)
This layer avoids recomputing expensive operations.
#### Responsibilities
•	Cache repeated query processing
•	Avoid repeated embedding generation
•	Speed up FAISS retrieval
#### Implementation
```
@lru_cache(maxsize=100)
def cache_process_query(query):
```

#### Why It Matters
•	Reduces latency
•	Improves throughput
•	Prevents redundant computation
________________________________________
### 8. Latency Tracking Layer
This layer measures performance across the full pipeline.
#### Tracks
•	SQL analysis time
•	RAG retrieval time
•	LLM inference time
•	Total request time
#### Example
start = time.time()
latency = time.time() - start
Why It Matters
•	Identifies bottlenecks
•	Helps optimize system performance
________________________________________

---

#  Dataset (cases.json)

The system uses a curated dataset of SQL performance scenarios.

### Example Cases:

* Full table scans
* JSON filtering issues
* Join performance problems
* High-frequency queries
* Nested subqueries
* Aggregation bottlenecks
* Logging table queries
* Update bottlenecks
* Anomaly detection cases

Each case contains:

```json
{
  "case_id": "case_1",
  "query": "SELECT * FROM large_table",
  "latency": "very high",
  "root_cause": "Full table scan",
  "suggestion": "Add WHERE clause",
  "tags": ["full_table_scan"]
}
```

---

#  API Endpoints

## 1. Analyze Query

```http
POST /ask
```

### Input:

```json
{
  "query": "SELECT * FROM users"
}
```

### Output:

* SQL analysis
* RAG match
* LLM explanation
* Tool results
* Latency metrics

---

## 2. List Available Tools

```http
GET /api/v1/tools
```

### Output:

```json
{
  "tools": [
    "analyze_query",
    "detect_anomaly",
    "suggest_optimization"
  ]
}
```

---

## 3. SQL Analysis Only

```http
POST /analyze
```

Returns raw SQL tool output without LLM layer.

---

#  Key Features

##  Hybrid AI System

Combines:

* Rule-based SQL analysis
* Semantic search (RAG)
* Generative reasoning (LLM)

---

##  Explainable AI Output

Every response includes:

* Root cause
* Execution plan
* Suggested fix
* Confidence level

---

## Tool-Augmented LLM

LLM can dynamically call tools when needed.

---

##  Performance-Aware Design

Tracks:

* Query latency
* Retrieval time
* LLM response time
* Total system latency

---

##  Context-Aware Reasoning

LLM uses:

* SQL execution plan
* Similar historical cases
* Query patterns

---

#  Example Use Case

### Input:

```sql
SELECT * FROM customers WHERE name LIKE '%john%'
```

### System Output:

* Problem: Full scan due to wildcard
* Root Cause: Leading wildcard disables index
* Suggestion: Use full-text search index
* Similar Case: case_12 (RAG)
* Execution Plan: SCAN TABLE customers
* Confidence: High

---

#  Tech Stack

* Python 
* Flask (API layer)
* FAISS (vector search)
* SentenceTransformers (embeddings)
* Ollama (Phi-3 LLM)
* SQLParse (query validation)
* JavaScript (frontend rendering)

---

#  System Design Highlights

* Micro-layered architecture (SQL + RAG + LLM + Tools)
* Agent-style reasoning system
* Hybrid deterministic + probabilistic pipeline
* Modular tool execution (MCP-style)

---

## Question: If you were designing this system for production at scale, what would you change or improve?
## Production-Scale Improvements

If this system were deployed in a production environment, the following improvements would be introduced to improve latency, scalability, and reliability.

---

## 1. Streaming Responses (WebSockets / SSE)

Currently, the system returns responses only after full processing is complete. For longer queries involving RAG and LLM reasoning, this increases perceived latency.

### Improvements

* Implement **WebSockets** or **Server-Sent Events (SSE)**
* Stream intermediate stages such as:

  * SQL analysis results
  * RAG retrieval progress
  * LLM reasoning output

### Benefit

* Improves responsiveness
* Provides real-time visibility into processing
* Enhances user experience for long-running tasks

---

## 2. Model Latency Optimization

LLM inference is currently the slowest stage in the pipeline.

### Improvements

* Use **quantized models** to reduce inference time
* Add **response caching** using Redis
* Route simple queries to rule-based processing without invoking the LLM

### Benefit

* Reduces response latency
* Improves system throughput
* Lowers compute cost

---

## 3. Distributed Caching Layer

Repeated queries and similar SQL patterns can lead to redundant computation.

### Improvements

* Introduce **Redis** caching
* Cache:

  * Query responses
  * RAG retrieval results
  * Tool execution outputs

### Benefit

* Reduces repeated processing
* Improves response time
* Supports scaling under repeated workloads

---

## 4. Asynchronous Task Processing

Heavy processing tasks should not block incoming requests.

### Improvements

* Use a **task queue system** such as:

  * Redis Queue
  * RabbitMQ
* Process LLM reasoning using background workers

### Benefit

* Prevents request blocking
* Improves system responsiveness
* Enables higher concurrency support

---

## 5. Observability and Monitoring

Tracking system performance is essential in production environments.

### Improvements

* Add structured logging
* Monitor latency across:

  * SQL analysis
  * RAG retrieval
  * LLM inference
* Integrate monitoring tools such as Prometheus or Grafana

### Benefit

* Helps identify performance bottlenecks
* Improves debugging capability
* Supports system reliability
---
## Steps to Run the Project
1. Clone the Repository
git clone https://github.com/Sneya9205/rag-query-performance-analyser.git
cd rag-query-performance-analyser
________________________________________
2. Create Virtual Environment
Windows:
python -m venv .venv
.venv\Scripts\activate
Mac/Linux:
python3 -m venv .venv
source .venv/bin/activate
________________________________________
3. Install Dependencies
pip install -r requirements.txt
________________________________________
4. Install Ollama
Download and install Ollama from:
https://ollama.com/download
Verify installation:
ollama --version
________________________________________
5. Pull the Phi-3 Mini Model
This project uses the phi3:mini model.
Run:
ollama pull phi3:mini
This step is required only once.
________________________________________
6. Start Ollama
Run:
ollama serve
Ollama runs locally at:
http://localhost:11434
Make sure it is running before starting the backend.
________________________________________
7. Run the Backend and Frontend
Start the backend:
python app.py
The page will run at:
http://127.0.0.1:5000

Enter a SQL query in the input field and submit the request.

The system will process the query through SQL analysis, retrieval, and LLM reasoning. 
The response will be displayed after processing completes. Initial responses may take longer depending on model loading and system performance.
---
### Design Choices
•	FAISS for Retrieval
FAISS was chosen for fast vector similarity search over stored SQL cases. It provides efficient nearest-neighbor retrieval with low latency on local systems. 
•	Phi-3 Mini via Ollama
The phi3:mini model was selected to balance reasoning capability with local execution feasibility. Running locally avoids external API dependency and improves privacy. 
•	Flask Backend
Flask was used due to its simplicity and flexibility for building lightweight APIs and integrating multiple processing stages. 
•	LRU Caching for Repeated Queries
An in-memory cache (lru_cache) was used to reduce repeated computation for similar queries and improve response time. 
•	Logging and Latency Tracking
Logging was integrated to monitor execution stages and measure performance across SQL analysis, retrieval, and LLM reasoning. 
________________________________________
### Trade-offs
•	Local LLM vs Cloud Models
Using a local model reduces dependency on external APIs but increases response time compared to cloud-hosted models. 
•	In-Memory Caching vs Distributed Cache
LRU caching improves speed for repeated queries but does not scale across multiple instances like Redis would. 
•	FAISS Local Index vs Vector Database
FAISS provides fast local retrieval but lacks advanced indexing and scaling features available in production-grade vector databases. 
•	Sequential Processing vs Asynchronous Execution
The pipeline processes steps sequentially, which simplifies design but increases total response time under heavy workloads. 
________________________________________
### Improvements
•	Add Streaming Responses
Introduce WebSockets or Server-Sent Events (SSE) to stream intermediate results and reduce perceived latency. 
•	Introduce Distributed Caching
Replace in-memory caching with Redis to support multi-instance scalability. 
•	Optimize Model Performance
Use quantized models or GPU acceleration to reduce inference latency. 
•	Add Asynchronous Task Processing
Use background workers or queues to handle long-running operations. 
•	Improve Retrieval Pipeline
Add hybrid search (vector + keyword matching) to improve retrieval accuracy.


---

#  Future Improvements

* Support PostgreSQL / MySQL connectors
* Add Redis caching layer for RAG + SQL plans
* Improve tool selection using classifier model
* Add streaming LLM responses
* Build dashboard analytics UI

---

#  Summary

This system is a **hybrid AI SQL assistant** that combines:

>  Retrieval (RAG)
>  Deterministic SQL analysis
>  LLM reasoning
>  Tool execution (MCP layer)

to generate **intelligent, explainable SQL performance insights**.

---

