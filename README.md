<!-- Readme -->
<p align="center">
  <h1 align="center">🔍 WebScout — Deep Research Assistant</h1>
  <p align="center">
    <strong>An AI-powered research agent that plans, searches, filters, and synthesizes answers from the web.</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.115-green.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/LLM-Groq%20Llama--3.3-orange.svg" alt="LLM">
  </p>
</p>

<p align="center"> •
  <a href="https://medium.com/@wahanesankalp29/from-web-search-to-llm-powered-search-agents-6a0ef663fded"><strong>Medium Article</strong></a> •
</p>

---

## 🚀 What is WebScout?

**WebScout** is a Python-based research assistant that autonomously answers complex questions by:

1. **Planning** — Breaking vague queries into specific, searchable sub-questions
2. **Searching** — Fetching real-time data from the web via Tavily API
3. **Filtering** — Using LLM batch processing to identify relevant sources
4. **Synthesizing** — Generating a coherent, well-structured report with citations

### The Problem It Solves

Traditional LLMs suffer from **hallucination** — they confidently generate plausible-sounding but incorrect information. WebScout solves this by **grounding responses in real-time web data**, ensuring every answer is backed by verifiable sources.

---

## 🧠 Approach & Design Decisions

This section explains the architectural choices made during development.

### 1. Sequential Search (Intentional)

I chose a **sequential pipeline** (Plan → Search → Filter → Report) over parallel execution. While parallelization could improve raw speed, the sequential approach offers:

- **Debuggability:** Each stage's output can be inspected independently
- **Accuracy:** Later stages depend on earlier ones; sequential flow ensures data integrity
- **Simplicity:** Easier to reason about, extend, and maintain

For a production system, parallelizing the search phase would be a natural next step.

### 2. The "N+1" Optimization — Batch Filtering

The original implementation called the LLM **once per search result** to check relevance. With 15 results, that's 15 API calls — a classic N+1 problem.

**Solution:** I refactored `filter_results` to use **Batch Processing**:

```python
# Before: N calls
for result in results:
    response = llm.call("Is this relevant?")  # 15 calls

# After: 1 call
all_summaries = build_summary(results)
response = llm.call("Which indices are relevant?")  # 1 call
# Returns: {"relevant_indices": [0, 2, 5]}
```

**Result:** ~80% reduction in filtering latency.

### 3. Separation of Concerns

The codebase is split into two core files:

| File | Responsibility |
|------|----------------|
| `main.py` | FastAPI server, API routes, request handling |
| `agent.py` | Core logic: `plan_research`, `execute_search`, `filter_results`, `generate_report` |

This separation allows the agent logic to be tested independently and potentially reused in CLI tools or other interfaces.

### 4. Stateless Design

The current implementation is **stateless by design**. Each request is independent, with no persistent memory across sessions. This keeps deployment lightweight — no database required.

For production, session history could be added via:
- In-memory cache (Redis)
- Lightweight database (SQLite)
- Vector store for semantic memory (e.g., ChromaDB, Pinecone)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11+, FastAPI |
| **LLM** | Groq (Llama-3.3-70b-versatile) |
| **Search** | Tavily API |
| **Frontend** | React + Vite + TailwindCSS |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ (for frontend)
- Groq API Key ([Get one here](https://console.groq.com))
- Tavily API Key ([Get one here](https://tavily.com))

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/IronwallxR5/WebScout.git
cd WebScout/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys:
# GROQ_API_KEY=your_groq_key
# TAVILY_API_KEY=your_tavily_key

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

---

## 🔌 API Reference

### POST `/api/research`

Submit a research query.

**Request:**
```json
{
  "query": "What are the latest developments in quantum computing?"
}
```

**Response:**
```json
{
  "status": "success",
  "plan": [
    "quantum computing breakthroughs 2024",
    "major quantum computing companies progress",
    "quantum computing applications healthcare finance"
  ],
  "report": "## Quantum Computing Developments\n\n..."
}
```

---

## 📁 Project Structure

```
WebScout/
├── backend/
│   ├── main.py          # FastAPI server & routes
│   ├── agent.py         # Core agent logic (4 functions)
│   ├── requirements.txt # Python dependencies
│   └── .env             # API keys (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx      # Main React component
│   │   └── index.css    # Tailwind styles
│   └── package.json
└── README.md
```

---

