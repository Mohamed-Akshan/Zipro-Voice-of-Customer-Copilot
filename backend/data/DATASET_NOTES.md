# Zipro Voice of Customer — Compact synthetic evidence corpus

**Entirely synthetic.** All reviews, conversations, interview notes and survey answers are invented for a fictional ride-hailing startup. They must not be represented as genuine user testimony.

## Contents — 350 feedback records, 18 source files

| Format | Files | Independent feedback records | Load source_type |
|---|---:|---:|---|
| `app_reviews.csv` | 1 | 150 | app_review |
| `support_tickets.json` | 1 | 100 | support_ticket |
| `customer_interviews/*.docx` | 10 | 10 | interview |
| `customer_surveys/*.pdf` | 5 | 50 (one page per survey) | survey |
| `feature_requests.xlsx` | 1 | 40 | feature_request |
| **Total** | **18** | **350** | |

All five formats are supported by the existing `app/rag/loaders.py` in the previous Zipro application. Do not retain the old data files when replacing the folder or both datasets will load.

## Relationship model

- `id` — unique original source ID (REV-, TKT-, INT-, SUR-, FEAT-).
- `customer_id` — synthetic, repeated across channels where scenarios share a participant.
- `incident_id` — synthetic cross-channel incident link; the same incident may be mentioned in more than one source.
- `date` — date the feedback was received, not necessarily the date of the ride.
- `issue_hint` — controlled taxonomy label to bootstrap analytics. It is **not** a KMeans-derived label and should not be described as an independently validated model prediction.
- Original source filename is added to normalized records by the loader.

Data spans June–November 2026 and reflects invented experiences in familiar Sri Lankan locations. Some descriptions intentionally contain uncertainty, polite or positive feedback, and incomplete outcomes rather than implying every complaint was confirmed.

## Usage

1. Replace the entire existing `backend/data/` directory with this `data/` directory.
2. If moving to a clean Pinecone index and fresh PostgreSQL database, start with empty storage so dashboard counts are not inflated by previous 1,700 records. Back up old data before clearing it.
3. Run the same supported `load_folder(BASE_DIR / 'data')` ingestion flow; verify it returns 350 unique records.
4. In Pinecone, keep original source IDs on each chunk. Count **feedback records**, not chunks, for business metrics.
5. Do not infer actual business prevalence or causal effects from this small synthetic dataset.

### Note on chunk count

The number of RAG chunks is not a fixed 350: each long interview and certain tickets may split into multiple chunks. With the existing 850/100 splitter, the actual chunk total should be checked by running `make_chunks(load_folder(...))` before embedding.
