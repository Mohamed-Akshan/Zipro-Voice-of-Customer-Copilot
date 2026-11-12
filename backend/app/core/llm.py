
from langchain_openai import ChatOpenAI

from app.core.config import settings


# OpenAI for chat and agent reasoning
def get_llm(schema=None):

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        max_retries=1,
        timeout=30
    )

    # Structured output for LangGraph agents
    if schema is not None:
        llm = llm.with_structured_output(
            schema,
            method="json_schema"
        )

    return llm
