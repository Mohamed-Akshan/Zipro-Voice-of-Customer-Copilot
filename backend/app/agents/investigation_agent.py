
import json
import logging

from langchain_core.messages import AIMessage

from app.core.guardrails import redact_personal_data
from app.core.llm import get_llm
from app.database.schemas import AnalysisPlan
from app.prompts.analytics import ANALYTICS_PROMPT
from app.rag.retrieval import retriever
from app.rag.corrective import rewrite_question
from app.services.analytics import analyze, available_issues, sample_sources


logger = logging.getLogger(__name__)


# Investigate customer feedback and calculate statistics
def investigate(state):

    prompt = ANALYTICS_PROMPT.format(
        issues=", ".join(available_issues()),
        previous_issue=state.get("current_issue", ""),
        question=state["question"]
    )

    # Let Gemini choose validated analytics filters
    plan = get_llm(AnalysisPlan).invoke(prompt)

    names = set(available_issues())

    plan.issues = [
        issue
        for issue in plan.issues
        if issue in names
    ]

    metrics = analyze(plan)

    # Answer simple count questions using PostgreSQL
    if plan.operation == "count":

        if plan.issues:
            summary = "; ".join(
                f"{name}: {value['mentions']} feedback records"
                for name, value in metrics.items()
                if name != "feedback_total"
            ) or "No matching issue records found."

        else:
            summary = (
                f"{metrics['feedback_total']} feedback records "
                "match the filters."
            )

        period = (
            f" Period: {plan.start_date or 'earliest'} "
            f"to {plan.end_date or 'latest'}."
        )

        source = (
            f" Source: {plan.source_type}."
            if plan.source_type
            else ""
        )

        answer = {
            "status": "evidence_found",
            "summary": summary + period + source,
            "proposals": [],
            "verification": (
                "Count calculated from distinct "
                "PostgreSQL feedback records."
            )
        }

        return {
            "answer": answer,
            "messages": [
                AIMessage(content=json.dumps(answer))
            ]
        }

    # Prepare a search query for customer evidence
    metrics.pop("feedback_total", None)

    query = state["question"]

    if plan.issues:
        query += " Issues: " + ", ".join(plan.issues)

    if state.get("retry_count", 0):
        query = rewrite_question(query)

    # Retrieve matching feedback
    try:
        documents = retriever.search(query)

    except Exception:
        logger.exception(
            "Investigation failed while retrieving evidence"
        )
        raise

    evidence = [
        {
            "source_id": document.metadata.get("source_id", ""),
            "text": redact_personal_data(document.page_content),
            "relevance_score": document.metadata.get("relevance_score")
        }
        for document in documents
    ]

    # Add original feedback records matching identified issues
    for issue in list(metrics)[:3]:

        records = sample_sources(
            issue,
            plan.start_date,
            plan.end_date
        )

        for record in records:
            evidence.append({
                "source_id": record["id"],
                "text": redact_personal_data(record["text"]),
                "quality": "issue_matched"
            })

    # Avoid duplicate source IDs
    unique = {
        item["source_id"]: item
        for item in evidence
        if item["source_id"]
    }

    return {
        "evidence": list(unique.values())[:18],
        "metrics": metrics,
        "resolved_question": query,
        "current_issue": (
            plan.issues[0]
            if plan.issues
            else state.get("current_issue", "")
        )
    }
