import json

from langchain_core.messages import AIMessage

from app.core.llm import get_llm
from app.prompts.investigation import REWRITE_PROMPT


def rewrite_question(question):
    try:
        response = get_llm().invoke(REWRITE_PROMPT.format(question=question))
        return str(response.content).strip()[:400] or question
    except Exception:
        return question


def check_retrieval(state):
    if state.get("answer"):
        return "direct"

    # A valid issue-matched original is reliable; missing scores aren't proof.
    evidence = state.get("evidence", [])
    relevant = any(item.get("quality") == "issue_matched" for item in evidence)

    if not relevant and evidence:
        # Hybrid retrievers may omit scores; verification will still check IDs/quotes.
        relevant = len(evidence) >= 2

    if relevant:
        return "decision"

    return "retry" if state.get("retry_count", 0) < 1 else "insufficient"


def retry_search(state):
    return {"retry_count": state.get("retry_count", 0) + 1}


def insufficient_evidence(state):
    answer = {
        "status": "insufficient_evidence",
        "message": "Not enough verified customer evidence to answer reliably.",
        "sources": []
    }
    return {
        "answer": answer,
        "messages": [AIMessage(content=json.dumps(answer))],
        "retry_count": 0
    }
