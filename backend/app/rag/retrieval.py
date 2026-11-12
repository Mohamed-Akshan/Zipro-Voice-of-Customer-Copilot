
import logging

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.database.database import fetch_all
from app.rag.hybrid import build_hybrid_retriever
from app.rag.reranker import rerank_feedback


logger = logging.getLogger(__name__)


# Search stored feedback using keywords
def search_keywords(question):

    rows = fetch_all(
        "SELECT id, feedback_id, text FROM feedback_chunks ORDER BY id"
    )

    if not rows:
        return []

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

    keyword_search = BM25Retriever.from_documents(documents)
    keyword_search.k = 10

    return keyword_search.invoke(question)


# Retrieve customer evidence
class FeedbackRetriever:

    def __init__(self):
        self.hybrid = None

    def search(self, question):

        if self.hybrid is None:
            self.hybrid = build_hybrid_retriever()

        if self.hybrid is None:
            return []

        try:
            documents = self.hybrid.invoke(question)

        except Exception as error:
            message = str(error).lower()

            temporary = any(word in message for word in (
                "429",
                "resource_exhausted",
                "quota",
                "timeout",
                "timed out",
                "503",
                "unavailable"
            ))

            if not temporary:
                raise

            logger.warning(
                "Semantic search unavailable; using BM25 keyword search: %s",
                error
            )

            documents = search_keywords(question)

        if not documents:
            return []

        try:
            return rerank_feedback(question, documents)

        except Exception:
            logger.exception(
                "Cohere reranking failed; using retrieved documents"
            )

            return documents[:6]


retriever = FeedbackRetriever()
