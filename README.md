# LangGraph Agentic Playground

A collection of agentic AI experiments built with **LangGraph**, featuring a production-grade **Text-to-SQL agent** that converts natural language questions into SQL queries, executes them, and automatically visualizes results.

---

## Table of Contents

- [Project Structure](#project-structure)
- [DBQuery Agent (Text2SQL)](#dbquery-agent--text2sql)
  - [Architecture](#architecture)
  - [Workflow Pipeline](#workflow-pipeline)
  - [Components](#components)
  - [Running the Agent](#running-the-agent)
- [Experiment Modules](#experiment-modules)
- [Tech Stack](#tech-stack)
- [Setup](#setup)

---

## Project Structure

```
langGraph-agentic-playground/
│
├── DBQuery_Agent/               # Production Text2SQL agent (main project)
│   └── src/
│       ├── app.py               # Chainlit web UI
│       ├── main.py              # CLI interface
│       ├── agentic_workflow.py  # LangGraph workflow orchestrator
│       ├── state.py             # Agent state definition
│       ├── sql_generator.py     # NL → SQL generation (Gemini)
│       ├── sql_executor.py      # SQL execution on SQLite
│       ├── on_topic_classifier.py  # Query relevance filter
│       ├── sql_guardrail.py     # SQL injection prevention
│       ├── reflection_node.py   # SQL optimization (Qwen local model)
│       ├── actNode.py           # ReACT agent for tool selection
│       ├── tools.py             # Visualization tools (bar/line/text)
│       ├── query_judge.py       # LLM judge for output evaluation
│       ├── schema_description.py   # Dynamic DB schema introspection
│       ├── utils.py             # Shared LLM configs & utilities
│       └── evaluationForge.py   # Phoenix experiment evaluation
│
├── experiments/                 # Reflection pattern demo
├── chatbot_experiments/         # Basic Groq chatbot
├── states_experiments/          # LangGraph state management examples
├── human_inLoop_experiments/    # Human-in-the-loop with Command API
├── agentic_RAGs/                # (Planned) RAG experiments
├── autoBugHunter/               # (Planned) Automated bug detection
├── requirements.txt
└── README.md
```

---

## DBQuery Agent (Text2SQL)

The **DBQuery Agent** is the core of this repository. It is a multi-step agentic pipeline that takes a natural language question, generates an optimized SQL query, executes it against a SQLite database (Chinook music store), and returns results with automatic visualizations.

### Architecture

The agent is built as a **LangGraph StateGraph** — a directed graph where each node is a specialized processing step and edges define conditional routing logic. The entire pipeline is observable via Phoenix (Arize), AgentOps, and LangSmith.

```
User Query (natural language)
        │
        ▼
┌─────────────────────┐
│  Topic Classifier    │──── Off-topic? ──→ END (polite rejection)
│  (Gemini 2.0 Flash)  │
└────────┬────────────┘
         │ On-topic
         ▼
┌─────────────────────┐
│  SQL Generator       │  NL → SQL using DB schema context
│  (Gemini 2.0 Flash)  │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  SQL Guardrail       │──── DELETE/DROP detected? ──→ END (blocked)
│  (guardrails-ai)     │
└────────┬────────────┘
         │ Safe query
         ▼
┌─────────────────────┐
│  SQL Reflection      │  Optimizes query for efficiency
│  (Ollama Qwen 2.5)   │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  SQL Executor        │  Runs query on SQLite, formats results
│  (SQLAlchemy)        │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  ReACT Agent         │  Selects: bar chart / line chart / text list
│  (Gemini 2.0 Flash)  │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  Tool Execution      │  Generates visualization (Plotly/Matplotlib)
└────────┬────────────┘
         ▼
┌─────────────────────┐
│  LLM Judge           │──── Poor rating? ──→ RETRY (back to generator
│  (Gemini 2.0 Flash)  │                       or tool node)
└────────┬────────────┘
         │ Accepted
         ▼
┌─────────────────────┐
│  End Node            │  Final response to user
└─────────────────────┘
```

### Workflow Pipeline

Each step in the pipeline serves a specific purpose:

| Step | File | Purpose |
|------|------|---------|
| **Topic Classifier** | `on_topic_classifier.py` | Determines if the user's question can be answered by the database. Off-topic queries are rejected early, saving compute. |
| **SQL Generator** | `sql_generator.py` | Converts natural language into a structured SQL query using the database schema as context. Returns both the query and expected column names via Pydantic structured output. |
| **SQL Guardrail** | `sql_guardrail.py` | Security layer that blocks destructive SQL operations (DELETE, DROP) using the `guardrails-ai` library. Prevents SQL injection attacks. |
| **SQL Reflection** | `reflection_node.py` | A local Qwen 2.5 model reviews the generated SQL for logical correctness, unnecessary joins, and optimization opportunities. Rewrites the query if improvements are found. |
| **SQL Executor** | `sql_executor.py` | Executes the SQL against the SQLite database, handles type coercion, and formats results as JSON dictionaries. |
| **ReACT Agent** | `actNode.py` | Uses the Reason-Act-Observe pattern to analyze results and select the best visualization tool — bar chart for categorical data, line chart for time-series, or text listing for simple results. |
| **Tool Execution** | `tools.py` | Three visualization tools: `bar_chart_tool` (Plotly dark-themed bar charts), `line_chart_tool` (Plotly line charts), and `text_listing_tool` (formatted JSON output). |
| **LLM Judge** | `query_judge.py` | Evaluates the full pipeline output on three criteria — **Coherence**, **Relevance**, and **Correctness**. If any criterion scores "Poor", the judge triggers a retry back to the SQL generator or tool node. |

### Components

#### State Management (`state.py`)

The agent maintains a rich `AgentState` (TypedDict) that flows through every node:

- **`question`** / **`question_history`** — current and past user queries
- **`sql_query`** / **`sql_query_history`** — generated SQL and revision history
- **`sql_result`** / **`sql_result_history`** — execution results
- **`sql_query_reflection_history`** — optimization decisions from the reflection node
- **`full_reflection`** — judge scores and retry decisions
- **`guardrail_validation`** — security check results
- **`reflection_iterations`** / **`full_reflection_iter`** — loop counters to prevent infinite retries

#### Evaluation (`evaluationForge.py`)

An experiment framework built on **Phoenix by Arize** that:
1. Loads a ground truth dataset (`ground_truth_dataset.json`)
2. Runs the SQL generator on each test case
3. Measures structural similarity (Jaccard) between generated and expected queries
4. Reports results as a Phoenix experiment

#### Schema Introspection (`schema_description.py`)

Dynamically extracts and formats the database schema — tables, columns, types, and foreign key relationships — so the LLM always has accurate context when generating SQL.

### Running the Agent

**Web UI (Chainlit):**
```bash
chainlit run DBQuery_Agent/src/app.py
```
The web interface supports file uploads (bring your own SQLite database), streaming SQL display, and inline chart visualization.

**CLI:**
```bash
cd DBQuery_Agent/src
python main.py
```
Interactive REPL — type your question, get SQL + results. Type `end` or `exit` to quit.

---

## Experiment Modules

These folders contain standalone experiments exploring individual LangGraph concepts:

### `experiments/` — Reflection Pattern

A tweet generation agent that demonstrates the **generation-reflection loop**:
1. An LLM generates a tweet
2. A second LLM reflects on quality and suggests improvements
3. The cycle repeats (up to 4 iterations)

Built with `MessageGraph` for simplicity.

### `chatbot_experiments/` — Basic Chatbot

A minimal LangGraph chatbot using **Groq LLama 3.1 8B**. Demonstrates single-node graph construction with message state management and an interactive REPL loop.

### `states_experiments/` — State Management

Three progressive examples of LangGraph state handling:
- **`basic_state.py`** — Simple counter with conditional looping
- **`annotated_state.py`** — Using `Annotated` types with `operator.add` and `operator.concat` for automatic state merging
- **`advanced_state.py`** — Manual state transformations without operators

### `human_inLoop_experiments/` — Command API

Demonstrates LangGraph's `Command` API for dynamic routing — nodes decide where to go next at runtime (via `goto`) instead of relying on pre-defined edges. Shows state updates alongside routing decisions.

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Agent Framework** | LangGraph, LangChain |
| **LLM Providers** | Google Gemini 2.0 Flash, Ollama Qwen 2.5 (local), Groq LLama 3.1 |
| **Frontend** | Chainlit (web UI) |
| **Visualization** | Plotly, Matplotlib |
| **Database** | SQLite (Chinook), SQLAlchemy |
| **Security** | guardrails-ai, sqlparse, sqlglot |
| **Observability** | Phoenix (Arize), AgentOps, LangSmith |
| **Validation** | Pydantic (structured LLM outputs) |

---

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed locally (for the Qwen 2.5 reflection model)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/langGraph-agentic-playground.git
cd langGraph-agentic-playground

# Install dependencies
pip install -r requirements.txt

# Pull the local Qwen model (used for SQL reflection)
ollama pull qwen2.5:3b
```

### Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key          # optional, for experiments
OPENAI_API_KEY=your_openai_api_key      # optional
PHOENIX_API_KEY=your_phoenix_api_key    # optional, for observability
AGENTOPS_API_KEY=your_agentops_key      # optional, for tracking
```

### Quick Start

```bash
# Run the Text2SQL agent with web UI
chainlit run DBQuery_Agent/src/app.py

# Or use the CLI
cd DBQuery_Agent/src && python main.py
```

---

## License

This project is for educational and experimental purposes.
