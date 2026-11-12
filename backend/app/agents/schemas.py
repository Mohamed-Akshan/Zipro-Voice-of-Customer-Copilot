
from pydantic import BaseModel, Field


class SourceQuote(BaseModel):
    source_id: str
    quote: str


class ProductProposal(BaseModel):
    issue: str

    finding: str = Field(
        description="Explain the customer problem naturally, using complete sentences."
    )

    action: str = Field(
        description="Explain what Zipro should do and how it would work."
    )

    rationale: str = Field(
        description="Explain why the action could help, using evidence and reasoning."
    )

    success_metrics: list[str] = Field(
        description="Two or three measurable success indicators."
    )

    citations: list[SourceQuote] = Field(
        default_factory=list
    )

    caveat: str = Field(
        default="",
        description="Explain important uncertainties or implementation risks."
    )


class DecisionDraft(BaseModel):
    executive_summary: str
    proposals: list[ProductProposal]


class DomainDecision(BaseModel):
    allowed: bool
