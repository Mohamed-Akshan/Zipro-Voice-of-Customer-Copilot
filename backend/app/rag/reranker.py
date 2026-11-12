from functools import lru_cache

from langchain_cohere import CohereRerank

from app.core.config import settings


@lru_cache(maxsize=1)
def get_reranker():
    # Reuse the Cohere client across requests.
    return CohereRerank(
        cohere_api_key=settings.COHERE_API_KEY,
        model=settings.COHERE_MODEL,
        top_n=6
    )


def rerank_feedback(question, documents):
    # Reorder the candidate passages; do not alter their original source IDs.
    if not documents:
        return []

    if not settings.COHERE_API_KEY:
        return documents[:6]

    return list(get_reranker().compress_documents(
        documents=documents,
        query=question
    ))
