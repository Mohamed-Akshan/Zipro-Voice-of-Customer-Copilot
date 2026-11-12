from datetime import date

from sqlalchemy import func, select

from app.database.database import SessionLocal
from app.database.models import Feedback, FeedbackIssue, Issue


def dashboard_stats():
    # Dashboard numbers come from complete feedback records, not RAG chunks.
    with SessionLocal() as session:
        total = session.scalar(select(func.count(Feedback.id))) or 0
        source_rows = session.execute(
            select(Feedback.source_type, func.count(Feedback.id))
            .group_by(Feedback.source_type)
            .order_by(func.count(Feedback.id).desc())
        ).all()

        issue_rows = session.execute(
            select(Issue.name, Issue.severity, func.count(FeedbackIssue.feedback_id.distinct()))
            .join(FeedbackIssue, FeedbackIssue.issue_id == Issue.id)
            .group_by(Issue.id)
            .order_by(func.count(FeedbackIssue.feedback_id.distinct()).desc())
            .limit(10)
        ).all()

        month = func.to_char(func.date_trunc("month", Feedback.feedback_date), "YYYY-MM")
        trend_rows = session.execute(
            select(month, func.count(Feedback.id))
            .group_by(month).order_by(month)
        ).all()

        issue_count = session.scalar(select(func.count(Issue.id))) or 0

    return {
        "total": total,
        "sources": [{"name": name, "count": count} for name, count in source_rows],
        "issues": [
            {"name": name, "severity": severity, "count": count}
            for name, severity, count in issue_rows
        ],
        "trends": [{"month": month, "count": count} for month, count in trend_rows],
        "issue_count": issue_count
    }


def available_issues():
    with SessionLocal() as session:
        return list(session.scalars(select(Issue.name).order_by(Issue.name)))


def _filters(query, source=None, start=None, end=None):
    if source:
        query = query.where(Feedback.source_type == source)
    if start:
        query = query.where(Feedback.feedback_date >= date.fromisoformat(start))
    if end:
        query = query.where(Feedback.feedback_date < date.fromisoformat(end))
    return query


def analyze(plan):
    # A validated LLM plan selects filters; SQLAlchemy constructs safe queries.
    start = plan.start_date
    end = plan.end_date
    issues = plan.issues[:5]
    result = {}

    with SessionLocal() as session:
        base = select(func.count(Feedback.id.distinct()))
        base = _filters(base, plan.source_type, start, end)
        result["feedback_total"] = session.scalar(base) or 0

        issue_query = (
            select(Issue.name, func.count(Feedback.id.distinct()))
            .join(FeedbackIssue, FeedbackIssue.issue_id == Issue.id)
            .join(Feedback, Feedback.id == FeedbackIssue.feedback_id)
        )
        issue_query = _filters(issue_query, plan.source_type, start, end)

        if issues:
            issue_query = issue_query.where(Issue.name.in_(issues))

        issue_query = (
            issue_query.group_by(Issue.id)
            .order_by(func.count(Feedback.id.distinct()).desc())
            .limit(5)
        )
        rows = session.execute(issue_query).all()

        for name, count in rows:
            entry = {
                "issue": name,
                "mentions": count,
                "period": f"{start or 'start'} to {end or 'latest'} (end exclusive)",
                "count_unit": "distinct feedback records"
            }

            if plan.compare_start and plan.compare_end:
                comparison = (
                    select(func.count(Feedback.id.distinct()))
                    .join(FeedbackIssue, FeedbackIssue.feedback_id == Feedback.id)
                    .join(Issue, Issue.id == FeedbackIssue.issue_id)
                    .where(Issue.name == name)
                )
                comparison = _filters(
                    comparison, plan.source_type,
                    plan.compare_start, plan.compare_end
                )
                comparison_count = session.scalar(comparison) or 0
                entry["comparison"] = [{
                    "mentions": comparison_count,
                    "period": f"{plan.compare_start} to {plan.compare_end} (end exclusive)"
                }]

            result[name] = entry

    return result


def sample_sources(issue_name, start=None, end=None, limit=3):
    # Provide exact original source text for citations and grounded explanations.
    with SessionLocal() as session:
        query = (
            select(Feedback.id, Feedback.text, Feedback.source_type)
            .join(FeedbackIssue, FeedbackIssue.feedback_id == Feedback.id)
            .join(Issue, Issue.id == FeedbackIssue.issue_id)
            .where(Issue.name == issue_name)
            .order_by(Feedback.feedback_date.desc(), Feedback.id.desc())
            .limit(limit)
        )
        query = _filters(query, start=start, end=end)
        return [dict(row._mapping) for row in session.execute(query)]
