
import json
import time
from datetime import date

from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import BASE_DIR, settings
from app.database.database import SessionLocal, initialize_database
from app.database.models import (
    Feedback,
    FeedbackChunk,
    FeedbackIssue,
    Issue
)

from app.ingestion.classification import classify_feedback
from app.rag.loaders import load_folder


# Initialize the Gemini embedding model
def get_embeddings():

    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        output_dimensionality=settings.EMBEDDING_DIMENSION
    )


# Save customer feedback and its issue categories
def store_feedback(records, upload_id=None):

    for record in records:

        labels = (
            [record["issue_hint"]]
            if record.get("issue_hint")
            else classify_feedback(record["text"])
        )

        values = {
            "id": record["id"],
            "source_type": record["source_type"],
            "feedback_date": date.fromisoformat(
                record["feedback_date"]
            ),
            "text": record["text"],
            "rating": record.get("rating") or None,
            "customer_id": record.get("customer_id"),
            "incident_id": record.get("incident_id"),
            "issue_hint": labels[0] if labels else None,
            "extra": json.loads(
                json.dumps(
                    record.get("metadata", {}),
                    default=str
                )
            ),
            "uploaded_file_id": upload_id
        }

        with SessionLocal.begin() as session:

            statement = insert(Feedback).values(**values)

            session.execute(
                statement.on_conflict_do_update(
                    index_elements=[Feedback.id],
                    set_={
                        "text": statement.excluded.text,
                        "metadata": statement.excluded["metadata"]
                    }
                )
            )

            # Save issue categories without duplicates
            for label in labels:

                issue = session.query(Issue).filter_by(
                    name=label
                ).first()

                if issue is None:
                    issue = Issue(name=label)
                    session.add(issue)
                    session.flush()

                relationship = insert(FeedbackIssue).values(
                    feedback_id=record["id"],
                    issue_id=issue.id
                )

                session.execute(
                    relationship.on_conflict_do_nothing()
                )


# Split feedback into chunks with stable IDs
def make_chunks(records):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=850,
        chunk_overlap=100
    )

    chunks = []

    for record in records:

        pieces = splitter.split_text(record["text"])

        for number, content in enumerate(pieces):

            chunk_id = f"{record['id']}-{number:03d}"

            chunk = Document(
                page_content=content,
                metadata={
                    "chunk_id": chunk_id,
                    "source_id": record["id"],
                    "source_type": record["source_type"],
                    "feedback_date": record["feedback_date"]
                }
            )

            chunks.append(chunk)

    return chunks


# Retry temporary embedding or Pinecone errors
def upload_batch(vector_store, batch):

    chunk_ids = [
        chunk.metadata["chunk_id"]
        for chunk in batch
    ]

    for attempt in range(settings.INGEST_RETRIES):

        try:

            vector_store.add_documents(
                documents=batch,
                ids=chunk_ids
            )

            return

        except Exception as error:

            message = str(error).lower()

            temporary_error = any(
                term in message
                for term in [
                    "429",
                    "502",
                    "503",
                    "504",
                    "resource_exhausted",
                    "rate limit",
                    "quota",
                    "timeout",
                    "timed out",
                    "connection reset",
                    "connection aborted"
                ]
            )

            if not temporary_error:
                raise

            if attempt == settings.INGEST_RETRIES - 1:
                raise

            wait_seconds = (
                settings.INGEST_RETRY_SECONDS
                * (attempt + 1)
            )

            print(
                f"Temporary API error. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)


# Save progress only after Pinecone accepts the batch
def save_indexed_chunks(batch):

    with SessionLocal.begin() as session:

        for chunk in batch:

            chunk_id = chunk.metadata["chunk_id"]

            statement = insert(FeedbackChunk).values(
                id=chunk_id,
                feedback_id=chunk.metadata["source_id"],
                text=chunk.page_content,
                chunk_number=int(
                    chunk_id.rsplit("-", 1)[1]
                )
            )

            session.execute(
                statement.on_conflict_do_update(
                    index_elements=[FeedbackChunk.id],
                    set_={
                        "text": statement.excluded.text
                    }
                )
            )


# Upload only chunks that are not already indexed
def index_feedback(records):

    chunks = make_chunks(records)

    # Read previously completed chunk IDs
    with SessionLocal() as session:

        completed_ids = set(
            session.scalars(
                select(FeedbackChunk.id)
            ).all()
        )

    pending_chunks = [
        chunk
        for chunk in chunks
        if chunk.metadata["chunk_id"] not in completed_ids
    ]

    total_chunks = len(chunks)
    completed_count = total_chunks - len(pending_chunks)

    print(f"Total chunks: {total_chunks}")
    print(f"Already indexed: {completed_count}")
    print(f"Remaining: {len(pending_chunks)}")

    if not pending_chunks:

        print("All chunks are already indexed!")
        return total_chunks

    # Connect to Pinecone
    vector_store = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX,
        embedding=get_embeddings(),
        pinecone_api_key=settings.PINECONE_API_KEY
    )

    batch_size = settings.INGEST_BATCH_SIZE

    # Process pending chunks in batches
    for start in range(0, len(pending_chunks), batch_size):

        batch = pending_chunks[
            start:start + batch_size
        ]

        # Upload vectors to Pinecone
        upload_batch(vector_store, batch)

        # Record successful progress in PostgreSQL
        save_indexed_chunks(batch)

        completed_count += len(batch)

        print(
            f"Indexed {completed_count}/{total_chunks} chunks",
            flush=True
        )

        # Pause between batches
        if start + batch_size < len(pending_chunks):

            time.sleep(
                settings.INGEST_DELAY_SECONDS
            )

    return total_chunks


# Ingest the complete preloaded dataset
def ingest_preloaded():

    initialize_database()

    records = load_folder(
        BASE_DIR / "data"
    )

    # Find feedback already stored in PostgreSQL
    with SessionLocal() as session:

        existing_ids = set(
            session.scalars(
                select(Feedback.id)
            ).all()
        )

    new_records = [
        record
        for record in records
        if record["id"] not in existing_ids
    ]

    if new_records:

        print(
            f"Saving {len(new_records)} new feedback records..."
        )

        store_feedback(new_records)

    else:

        print(
            "All feedback records already exist in PostgreSQL."
        )

    # Resume Pinecone ingestion
    total_chunks = index_feedback(records)

    print(
        f"Finished: {len(records)} feedback records, "
        f"{total_chunks} chunks"
    )


if __name__ == "__main__":

    ingest_preloaded()
