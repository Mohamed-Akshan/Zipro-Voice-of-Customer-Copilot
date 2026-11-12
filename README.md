# zipro. — Voice of Customer Copilot

**Fictional ride-hailing product intelligence · 1,700 synthetic feedback records · two React pages**

Zipro turns reviews, tickets, interviews, surveys and feature requests into evidence-backed insights and proposed product decisions. This is a **synthetic portfolio case study**, not a service representing any real company.

## Project features

- **Customer Intelligence Dashboard:** SQL-backed source counts, top issues and monthly trends, plus file upload.
- **AI Product Copilot:** multi-turn questions and recommendations with clickable source quotations and original feedback drawer.
- **Three separate LangGraph agents:** `investigation_agent.py`, `product_decision_agent.py` and `evidence_verification_agent.py`.
- **Dynamic analysis:** Gemini interprets the question into validated analytics parameters. SQLAlchemy counts *distinct feedback records*; the LLM never executes arbitrary generated SQL.
- **Hybrid corrective RAG:** Pinecone semantic search + PostgreSQL BM25 + weighted ensemble + optional Cohere reranking, one corrective rewrite when evidence is insufficient.
- **Issue tagging:** supplied synthetic records retain their authored issue categories. **New unlabeled feedback** is tagged by Gemini multi-label classification; *KMeans was removed*.
- **Evidence validation:** citations require the exact original source ID and an exact quote, and cited records must belong to the referenced issue category.
- **LLMs:** Gemini primary (`gemini-3.8-flash`), Groq fallback (`openai/gpt-oss-120b`). Gemini embedding vectors are 768-dimensional.
- **Storage:** PostgreSQL via SQLAlchemy `SessionLocal` and `DeclarativeBase`, Pinecone for embeddings, separate LangGraph PostgreSQL checkpoints.
- **Safe ingestion:** 5 chunks per batch, 10 seconds between batches, up to 3 attempts with 65-second pauses on rate limits. Configurable from `.env`. Stable chunk IDs allow safe re-upserts.

## 1. Set up PostgreSQL and credentials

Create an empty PostgreSQL database called `zipro` (pgAdmin or Neon). **No pgvector extension is needed.**

Copy `backend/.env.example` to `backend/.env`. Fill in at least:

```ini
DATABASE_URL=postgresql://postgres:password@localhost:5432/zipro
GEMINI_API_KEY=
PINECONE_API_KEY=
GROQ_API_KEY=
COHERE_API_KEY=
```

`GROQ_API_KEY` is optional fallback; Cohere is optional reranking. **Gemini API key is required for Gemini embeddings** even if Groq handles chat.

Do not commit your `.env` file to GitHub.

## 2. Run the backend (Windows PowerShell)

Requires Python 3.11+.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python pinecone.py
python -m scripts.setup_database
python -m app.ingestion.ingest

uvicorn app.main:app --reload
```

`python pinecone.py` creates or validates the 768-dimensional Pinecone serverless index. `setup_database` creates six app tables and initializes LangGraph checkpoint tables. `python -m app.ingestion.ingest` loads 1,700 bundled synthetic records; its batch upload may take a substantial amount of time depending on quota and delays. **Run initial ingestion outside a hosted HTTP request.**

The database is queried using `SessionLocal` and SQLAlchemy models. The LangGraph checkpointer manages its own tables and connection interface; it is intentionally not modeled using SQLAlchemy.

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for FastAPI documentation.

## 3. Run the frontend

Open another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend communicates with FastAPI at `/api`, proxied locally by Vite. It has two pages: Dashboard and AI Product Copilot.

## 4. Example questions

- “How many app reviews were submitted in October?” (SQL count)
- “What are our top customer problems?” (SQL top issue counts + citations)
- “Why do drivers cancel bookings?” (retrieved feedback + hypotheses)
- “Compare September and October refund complaints.” (period comparison)
- “Show me the original reviews supporting this recommendation.” (citations)
- “Explain the first issue further.” (same `thread_id` maintains context)

SQL-derived **feedback counts are not customer counts, trips, financial losses, or proven causal effects**. A question requiring unavailable data must be answered with an explicit limitation rather than an invented fact. LLM-selected dates and issue names are validated before SQLAlchemy builds queries.

## 5. Supported documents and uploading

`app/rag/loaders.py` loads CSV, JSON, DOCX, PDF and XLSX files in a small `if/elif` function while preserving one **source record ID per feedback item**. Some specialized handling is necessary so that rows in CSV/XLSX/JSON and survey pages in PDFs are individually citable.

New files are uploaded through the dashboard. Maximum 8 MB and 1,000 feedback records per file. In production (`APP_ENV=production`) uploads require `X-Upload-Token` matching `UPLOAD_ADMIN_TOKEN`.

Uploaded feedback without issue categories is classified by Gemini into a controlled list of issue categories. Existing bundled synthetic issue labels are reused instead of making 1,700 extra LLM calls. The `ingestion/classification.py` module is only for categorization; it is **not** clustering or model training.

**Upload limitations:** indexing happens during the request (off the event loop using a worker thread). It can exceed serverless request timeouts; a job queue is recommended before a real public deployment. Filenames/extensions and size are checked, but this example is not a complete malware scanner or full tenant security boundary.

## 6. Final backend organization

```text
backend/
├── app/
│   ├── agents/
│   │   ├── investigation_agent.py
│   │   ├── product_decision_agent.py
│   │   ├── evidence_verification_agent.py
│   │   ├── domain_guard.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── schemas.py
│   ├── rag/
│   │   ├── loaders.py
│   │   ├── hybrid.py
│   │   ├── reranker.py
│   │   ├── retrieval.py
│   │   └── corrective.py
│   ├── database/
│   │   ├── database.py          # SQLAlchemy engine and SessionLocal
│   │   ├── models.py            # Six application ORM tables
│   │   ├── schemas.py           # Validated issue and analytics plans
│   │   └── pinecone.py          # Vector index setup
│   ├── ingestion/
│   │   ├── ingest.py            # Resumable small-batch indexing
│   │   └── classification.py    # Multi-label Gemini classification
│   ├── services/
│   │   └── analytics.py         # Safe SQLAlchemy counts and comparisons
│   ├── prompts/
│   │   ├── domain.py
│   │   ├── investigation.py
│   │   ├── analytics.py
│   │   └── decision.py
│   ├── core/
│   │   ├── config.py
│   │   ├── llm.py
│   │   ├── guardrails.py
│   │   └── tracing.py
│   ├── api/
│   │   ├── routes.py           # FastAPI routes (separate from main.py)
│   │   └── schemas.py          # Typed request and response objects
│   └── main.py                 # Short FastAPI entry point
├── data/                       # 50 source files + dataset notes
├── scripts/setup_database.py
├── evals/                      # Golden questions + evaluation script
├── tests/
├── pinecone.py                 # Run with python pinecone.py
├── requirements.txt
├── .env.example
└── vercel.json                # Optional backend Vercel routing

frontend/
├── src/pages/Dashboard.jsx
├── src/pages/Copilot.jsx
├── src/components/StatCard.jsx
├── src/App.jsx
├── src/api.js
├── src/index.css
└── package.json
```

**Removed:** `ingestion/clustering.py` (no KMeans), and the redundant `scripts/ingest_data.py` runner. There is no standalone dataset generator in the delivered application.

## 7. Tests and limitations

```powershell
cd backend
pytest -q
python -m evals.evaluate  # Requires a running backend and live API keys
```

Syntax, document parsing, dataset checks, and deterministic unit tests were run locally. **An end-to-end run against PostgreSQL, Pinecone, Gemini, Groq, and Cohere was not possible without live connections and credentials.** The React production build was also not verified in this environment. Do not equate passing offline tests with a fully production-tested system.

The current verifier checks exact source IDs, quotes, and issue associations, but it **cannot guarantee that every generated interpretation is logically entailed**. Product actions are suggestions, not causal proofs. Multi-user production deployment requires authenticated, tenant-isolated threads and database access. Long-running ingestion needs a background worker rather than a serverless HTTP request.

## 8. Deployment

There is an optional `backend/vercel.json` routing file because Vercel deployment was requested; it is **not** a document manifest. Deploy the backend and frontend separately, with `FRONTEND_URL` and `VITE_API_URL` configured correctly. Managed PostgreSQL (Neon) and Pinecone can be used. A dedicated FastAPI host is preferable for long-running agent requests and uploads.
