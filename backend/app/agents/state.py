from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class VoiceOfCustomerState(TypedDict, total=False):
    # Conversation messages are appended automatically by LangGraph.
    messages: Annotated[list[AnyMessage], add_messages]

    # Input and follow-up context.
    question: str
    resolved_question: str
    current_issue: str
    thread_id: str

    # Evidence and analysis for the current turn.
    evidence: list[dict]
    metrics: dict
    retry_count: int
    search_quality: str

    # Product decision and verified response.
    draft: dict
    answer: dict
