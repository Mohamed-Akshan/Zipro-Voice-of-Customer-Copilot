from typing import Literal

from pydantic import BaseModel, Field


class IssueLabels(BaseModel):
    # One feedback record can mention several different customer problems.
    issues: list[str] = Field(default_factory=list, max_length=4)


class AnalysisPlan(BaseModel):
    # Gemini chooses safe filters; it never generates executable SQL.
    operation: Literal["top", "count", "compare", "trend", "evidence", "recommendation"] = "top"
    issues: list[str] = Field(default_factory=list)
    source_type: Literal["app_review", "support_ticket", "interview", "survey", "feature_request"] | None = None
    start_date: str | None = None
    end_date: str | None = None
    compare_start: str | None = None
    compare_end: str | None = None
