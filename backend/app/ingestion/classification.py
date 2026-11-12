from app.core.llm import get_llm
from app.database.schemas import IssueLabels


# Use the same issue names as the bundled dataset and dashboard.
ISSUE_CATEGORIES = (
    "Accessibility issue", "Account restriction", "App crashes",
    "Change destination difficulty", "Customer support delay",
    "Driver behavior", "Driver cancellation", "Driver no-show",
    "Duplicate charge", "Failed card payment", "Family booking request",
    "History or receipt error", "Inaccurate pickup ETA",
    "Incorrect pickup pin", "Long driver matching", "Lost item follow-up",
    "Map not updating", "Multiple stops request", "No vehicles available",
    "Notification delay", "OTP login failure", "Pickup area confusion",
    "Poor low-signal behavior", "Promo code failure", "Refund delay",
    "Rider cancellation trouble", "SOS accessibility", "Safety reporting",
    "Scheduled ride reliability", "Unexpected fare increase",
    "Unfair cancellation fee", "Unhelpful support response",
    "Vehicle cleanliness", "Wallet balance mismatch", "Wrong route"
)


def classify_feedback(text):
    # Multiple issue categories may apply to the same feedback record.
    prompt = f"""Classify fictional Zipro ride-hailing customer feedback.
    Choose up to four categories, exactly as spelled below:
    {', '.join(ISSUE_CATEGORIES)}

    Assign only issues explicitly supported by the customer text.
    If none match, return an empty list. Do not make up new labels.

    Feedback:
    {text[:3500]}
    """

    result = get_llm(IssueLabels).invoke(prompt)
    return [name for name in result.issues if name in ISSUE_CATEGORIES]
