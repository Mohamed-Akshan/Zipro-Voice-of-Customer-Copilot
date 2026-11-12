from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2500)
    thread_id: str | None = None


class CitationResponse(BaseModel):
    source_id: str
    quote: str
    source_type: str
    date: str


class ProposalResponse(BaseModel):
    issue: str
    finding: str
    action: str
    rationale: str
    success_metrics: list[str]
    sources: list[CitationResponse]
    metrics: dict[str, Any] | None = None
    caveat: str = ""


class AnswerResponse(BaseModel):
    status: Literal["evidence_found", "insufficient_evidence", "out_of_domain", "error"]
    message: str | None = None
    summary: str | None = None
    proposals: list[ProposalResponse] = Field(default_factory=list)
    sources: list[CitationResponse] = Field(default_factory=list)
    verification: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    answer: AnswerResponse


class UploadResponse(BaseModel):
    status: str
    records: int
    chunks: int
    filename: str


class HistoryMessage(BaseModel):
    role: Literal["human", "ai"]
    content: Any


class HistoryResponse(BaseModel):
    messages: list[HistoryMessage]


class DashboardItem(BaseModel):
    name: str
    count: int
    severity: str | None = None


class TrendItem(BaseModel):
    month: str
    count: int


class DashboardResponse(BaseModel):
    total: int
    sources: list[DashboardItem]
    issues: list[DashboardItem]
    trends: list[TrendItem]
    issue_count: int


class SourceResponse(BaseModel):
    id: str
    source_type: str
    feedback_date: str
    text: str
    rating: int | None = None
