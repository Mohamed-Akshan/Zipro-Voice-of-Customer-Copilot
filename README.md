# Zipro — Voice of Customer Copilot

**An Agentic AI-powered Customer Intelligence & Product Decision Support System**

Zipro is a full-stack AI application designed to help product teams turn unstructured customer feedback into actionable, evidence-backed product insights.

Built around a fictional ride-hailing company, Zipro analyzes approximately 1,700 synthetic customer feedback records collected across app reviews, support tickets, customer interviews, surveys, and feature requests.

Instead of manually reviewing hundreds of complaints, product teams can ask natural-language questions, investigate recurring issues, compare customer experiences, and receive product improvement recommendations supported by verifiable customer evidence.

> **Project note:** Zipro is a portfolio case study built using synthetic customer feedback. It does not represent a real ride-hailing company's internal system.

---

## The Business Problem

Ride-hailing platforms receive customer feedback from multiple channels. Important problems such as driver cancellations, booking failures, refund delays, payment issues, and unreliable pickup experiences can be difficult to investigate when feedback is scattered across documents.

Traditional dashboards can show complaint counts, but they often struggle to explain:

- Why customers are dissatisfied with a particular experience.
- Which problems deserve product team attention.
- What customer evidence supports a proposed improvement.
- How multiple issues relate to the broader customer experience.
- How to measure whether a product improvement succeeds.

**Zipro bridges the gap between customer feedback analytics and evidence-based product decision-making.**

## The Solution

Zipro provides two integrated workspaces.

### 1. Customer Intelligence Dashboard

A structured analytics interface for exploring customer feedback.

**Capabilities:**
- Total feedback records and issue statistics.
- Frequently reported customer problems.
- Monthly customer feedback trends.
- SQL-backed issue analysis.
- Upload and index additional customer feedback in CSV, JSON, DOCX, PDF, or XLSX formats.

The dashboard uses PostgreSQL and SQLAlchemy to retrieve structured analytical results.

### 2. AI Product Copilot

A conversational AI assistant that investigates customer feedback and helps product teams make informed decisions.

**Capabilities:**
- Natural-language customer feedback investigation.
- Multi-turn conversations with persistent memory.
- Complaint comparisons and issue analysis.
- Evidence-backed product improvement recommendations.
- Clickable citations linked to original feedback records.
- Suggested success metrics for proposed improvements.
- Explicit handling of insufficient evidence.

For example, a product manager can ask:

**"If Zipro can prioritize only one product improvement this quarter, which customer problem deserves attention first, and why?"**

The copilot investigates relevant feedback, uses available complaint statistics, evaluates the supporting evidence, and proposes a product decision.

Recommendations are treated as hypotheses to validate, not guaranteed business outcomes.

---

## System Architecture

Zipro combines **LangGraph multi-agent orchestration, hybrid corrective RAG, structured PostgreSQL analytics, and source-level evidence verification**.

The workflow follows:

```text
Customer Question
       |
       v
FastAPI Backend
       |
       v
Domain Guardrails
       |
       v
Investigation Agent
       |
       +---- PostgreSQL Analytics
       |
       +---- Hybrid RAG Retrieval
       |         |
       |         +---- Pinecone Semantic Search
       |         +---- BM25 Keyword Search
       |         +---- Optional Cohere Reranking
       |
       +---- Corrective Retrieval
       |
       v
Product Decision Agent
       |
       v
Evidence Verification Agent
       |
       v
Evidence-Backed Response
       |
       v
React AI Product Copilot
```

### Multi-Agent Workflow

The application uses three separate business-focused LangGraph agents.

**Investigation Agent**

Investigates the user's question using customer feedback and structured analytics. It retrieves relevant evidence and identifies recurring issues, complaint patterns, and supporting customer experiences.

**Product Decision Agent**

Transforms investigation findings into product recommendations, business reasoning, and proposed success metrics. Recommendations are grounded in available evidence rather than presented as established outcomes.

**Evidence Verification Agent**

Checks the generated response against original customer feedback stored in PostgreSQL.

Verification includes:
- Validating customer feedback source IDs.
- Checking quotations against original feedback text.
- Confirming that cited records are associated with the relevant issue categories.

The workflow also includes domain guardrails and corrective retrieval paths for questions with insufficient evidence.

## Hybrid Corrective RAG

Zipro uses a hybrid retrieval approach rather than relying exclusively on vector similarity.

**Semantic Retrieval — Pinecone**

Uses 768-dimensional Gemini embeddings to find customer feedback with similar meaning, even when the user's wording differs from the original complaint.

**Keyword Retrieval — BM25**

Supports exact-term matching for issue descriptions and specific customer language.

**Hybrid Retrieval**

Combines semantic and keyword retrieval results to improve evidence discovery.

**Reranking**

Supports optional Cohere reranking to refine the relevance of retrieved results.

**Corrective Retrieval**

When the initial retrieval is insufficient, the system can reformulate the search and attempt retrieval again before producing a response.

This design aims to reduce irrelevant evidence and unsupported conclusions while keeping the system explainable.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Multi-Agent Orchestration | LangGraph |
| LLM Reasoning | OpenAI |
| Embeddings | Gemini Embedding |
| Vector Database | Pinecone |
| Relational Database | PostgreSQL, SQLAlchemy |
| Retrieval | Hybrid Search, BM25, Corrective RAG |
| Reranking | Cohere (optional) |
| Evaluation | RAGAS |
| Observability | Langfuse |
| Conversation Memory | LangGraph PostgreSQL Checkpointer |

## Customer Feedback and Ingestion

Zipro uses a multi-format synthetic customer feedback corpus covering common ride-hailing customer experience problems.

Supported input formats include **CSV, JSON, DOCX, PDF, and XLSX**.

The ingestion pipeline:

1. Loads feedback from the supported file formats.
2. Preserves identifiable feedback records and source metadata.
3. Assigns issue categories to new unlabeled feedback using LLM-based multi-label classification.
4. Splits suitable content into retrievable chunks.
5. Generates Gemini embeddings.
6. Stores embeddings in Pinecone and structured records in PostgreSQL.

The pipeline supports subsequent document uploads, allowing newly added feedback to become available for analysis and retrieval.

## Evaluation — RAGAS

Zipro includes an offline RAG evaluation notebook and a **25-question golden evaluation dataset** covering basic customer complaints, intermediate reasoning, and more advanced product questions.

Three evaluation metrics were measured:

| RAGAS Metric | Average Score |
|---|---:|
| **Faithfulness** | **0.867** |
| Context Precision | 0.777 |
| Context Recall | 0.720 |

**Observations**

- Faithfulness indicates that generated answers were generally well supported by retrieved evidence.
- Context Precision suggests retrieval usually returned useful feedback, with opportunities to improve relevance ranking.
- Context Recall indicates that some expected evidence was missed, particularly in more demanding questions.

These results are from a standalone RAG evaluation, not an end-to-end evaluation of the entire three-agent LangGraph workflow.

The golden references are based on the project's feedback scenarios and require source-by-source verification before being treated as a final benchmark.

## Observability — Langfuse

Zipro integrates Langfuse with LangGraph to provide visibility into AI workflow execution.

The observability integration captures supported LangGraph and LLM operations, enabling inspection of:

- Agent workflow traces.
- Model execution latency.
- Token usage and reported API costs.
- LLM inputs and outputs.
- Execution errors and performance bottlenecks.

Langfuse helps investigate failures and understand how AI responses are generated, complementing the offline quality evaluation performed with RAGAS.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- PostgreSQL
- Pinecone account
- OpenAI and Gemini API keys
- Optional Cohere and Langfuse credentials

### 1. Configure the backend

Create `backend/.env` using `backend/.env.example` as a reference.

Configure your database connection, model credentials, vector database, and any optional services.

**Never commit real API keys or passwords to GitHub.**

### 2. Run the backend

From the `backend` directory:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python -m scripts.setup_database
python setup_pinecone.py
python -m app.ingestion.ingest

uvicorn app.main:app --reload
```

Database setup, Pinecone index creation, and initial ingestion are initialization tasks; they do not need to be repeated on every application restart.

FastAPI documentation: `http://localhost:8000/docs`

### 3. Run the frontend

From the `frontend` directory:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`.

### 4. Run RAGAS Evaluation

Open `backend/evals/ragas.ipynb` using a Python environment with the backend requirements installed.

The notebook loads the golden dataset with pandas, retrieves customer feedback, generates answers, calculates RAGAS scores, and presents the results.

---

## Example Questions

**Customer Intelligence**
- What are the most frequently reported customer complaints?
- Why are customers frustrated with driver cancellations?
- What problems do customers experience during booking?
- Compare refund delays and payment-related complaints.

**Product Decisions**
- Which customer issue should Zipro prioritize first?
- What product improvement could reduce cancellation-related inconvenience?
- What evidence supports improving refund status visibility?
- What should the product team validate before implementing automatic driver reassignment?

**Follow-up Investigation**
- Explain the first issue in more detail.
- Show the customer feedback supporting that recommendation.
- What metrics should we track after implementing the proposed improvement?

---

## Engineering Considerations and Limitations

Zipro was developed with a production-oriented architecture, but it remains a portfolio MVP.

Important considerations include:

- Complaint counts represent feedback records, not necessarily unique customers or trips.
- Customer feedback can reveal pain points but does not independently establish root causes.
- Product recommendations require validation through experiments or operational analysis.
- Source verification checks citations and quotations but cannot guarantee every generated interpretation is logically correct.
- Public multi-user deployment would require authentication, access control, and appropriate request limits.
- Large document uploads would benefit from asynchronous background processing.
- The present RAGAS benchmark does not measure the complete multi-agent workflow.

These limitations guide future improvements rather than being treated as completed capabilities.

## Future Improvements

- End-to-end agent evaluation with curated test cases.
- Improved hybrid retrieval ranking and recall.
- Automated regression testing for RAG responses.
- Enhanced monitoring, alerting, and retrieval diagnostics.
- Background ingestion workers.
- Production authentication and access controls.

---

## Project Purpose

Zipro demonstrates the practical engineering involved in building an **evidence-grounded, multi-agent AI application for a real business problem**.

The project brings together:

**Agentic AI · Hybrid RAG · Corrective Retrieval · SQL Analytics · Evidence Verification · RAGAS Evaluation · Langfuse Observability · Full-Stack Development**

The objective is not simply to generate answers from documents, but to transform fragmented customer feedback into traceable insights that can support better product decisions.

**Disclaimer:** All customer feedback used for this portfolio case study is synthetic.