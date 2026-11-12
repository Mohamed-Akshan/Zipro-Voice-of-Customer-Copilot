
import json

from langchain_core.messages import AIMessage
from sqlalchemy import select

from app.core.guardrails import redact_personal_data
from app.database.database import SessionLocal
from app.database.models import Feedback, FeedbackIssue, Issue


# Verify customer quotations and produce the final answer
def verify_evidence(state):

    retrieved_ids = {
        item["source_id"]
        for item in state.get("evidence", [])
    }

    metrics = state.get("metrics", {})
    verified = []

    with SessionLocal() as session:

        for proposal in state["draft"].get("proposals", [])[:3]:

            issue = proposal["issue"]

            # Only allow issues supported by SQL analytics
            if metrics and issue not in metrics:
                continue

            citations = []
            seen_sources = set()

            for citation in proposal.get("citations", []):

                source_id = citation["source_id"]
                quote = citation["quote"].strip()

                if not quote or source_id not in retrieved_ids:
                    continue

                if source_id in seen_sources:
                    continue

                record = session.get(Feedback, source_id)

                if not record:
                    continue

                # The quote must match the original record
                original_text = redact_personal_data(record.text)

                if quote not in original_text:
                    continue

                # Check the record belongs to this issue
                linked = session.scalar(
                    select(Issue.id)
                    .join(
                        FeedbackIssue,
                        FeedbackIssue.issue_id == Issue.id
                    )
                    .where(
                        FeedbackIssue.feedback_id == source_id,
                        Issue.name == issue
                    )
                )

                if linked is None:
                    continue

                citations.append({
                    "source_id": source_id,
                    "quote": quote,
                    "source_type": record.source_type,
                    "date": str(record.feedback_date)
                })

                seen_sources.add(source_id)

                if len(citations) == 2:
                    break

            # Keep only proposals supported by original feedback
            if not citations:
                continue

            verified.append({
                "issue": issue,
                "finding": proposal["finding"],
                "action": proposal["action"],
                "rationale": proposal["rationale"],
                "success_metrics": proposal["success_metrics"][:3],
                "sources": citations,
                "metrics": metrics.get(issue),
                "caveat": proposal.get("caveat", "")
            })

    if verified:

        # Build a natural introduction from verified findings
        first = verified[0]
        count = (
            first["metrics"].get("mentions")
            if first["metrics"]
            else None
        )

        if len(verified) == 1:

            summary = (
                f"Based on Zipro's customer feedback, "
                f"{first['issue'].lower()} is an issue worth addressing. "
            )

            if count is not None:
                summary += (
                    f"It appears in {count} feedback records. "
                )

            summary += (
                "The customer experiences below help explain "
                "the problem and inform the recommended next step."
            )

        else:

            issues = ", ".join(
                item["issue"]
                for item in verified
            )

            summary = (
                "Looking across Zipro's customer feedback, "
                f"several concerns stand out: {issues}. "
                "The following analysis explains the customer "
                "experiences behind these issues and what "
                "the product team could do next."
            )

        answer = {
            "status": "evidence_found",
            "summary": summary,
            "proposals": verified,
            "verification": (
                "Source IDs and quotations checked against "
                "original PostgreSQL feedback. "
                "Recommendations are proposed actions, not proven outcomes."
            )
        }

    else:

        answer = {
            "status": "insufficient_evidence",
            "message": (
                "I couldn't find enough verified customer "
                "evidence to support a confident recommendation."
            ),
            "sources": []
        }

    return {
        "answer": answer,
        "messages": [
            AIMessage(content=json.dumps(answer, default=str))
        ],
        "retry_count": 0
    }
