from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore

from app.core.config import settings
from app.database.database import fetch_all
from app.ingestion.ingest import get_embeddings


def build_hybrid_retriever():
    # Use exactly the same chunk identifiers in keyword and vector search.
    rows = fetch_all("SELECT id, feedback_id, text FROM feedback_chunks ORDER BY id")

    if not rows:
        return None

    documents = [
        Document(
            page_content=row["text"],
            metadata={
                "chunk_id": row["id"],
                "source_id": row["feedback_id"]
            }
        )
        for row in rows
    ]

    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 10

    vector_store = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX,
        embedding=get_embeddings(),
        pinecone_api_key=settings.PINECONE_API_KEY
    )

    semantic = vector_store.as_retriever(search_kwargs={"k": 10})

    return EnsembleRetriever(
        retrievers=[semantic, bm25],
        weights=[0.6, 0.4],
        id_key="chunk_id"
    )
