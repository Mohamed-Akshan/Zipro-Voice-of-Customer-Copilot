from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings


def create_index():
    # Create one AWS serverless dense-vector index on first setup.
    if not settings.PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is missing")

    client = Pinecone(api_key=settings.PINECONE_API_KEY)

    if not client.has_index(settings.PINECONE_INDEX):
        client.create_index(
            name=settings.PINECONE_INDEX,
            dimension=settings.EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.PINECONE_CLOUD,
                region=settings.PINECONE_REGION
            )
        )

    index_info = client.describe_index(settings.PINECONE_INDEX)

    if index_info.dimension != settings.EMBEDDING_DIMENSION:
        raise ValueError("Pinecone index dimension differs from EMBEDDING_DIMENSION")

    print(f"Pinecone index ready: {settings.PINECONE_INDEX}")


if __name__ == "__main__":
    create_index()
