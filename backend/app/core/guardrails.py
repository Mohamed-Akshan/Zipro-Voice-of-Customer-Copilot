import re
from pathlib import Path

from app.core.config import settings


ALLOWED_EXTENSIONS = {".csv", ".json", ".pdf", ".docx", ".xlsx"}


def check_upload(filename, size):
    # Check extensions and size before parsing untrusted uploads.
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Upload CSV, JSON, PDF, DOCX or XLSX only")

    if size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"File must be under {settings.MAX_UPLOAD_MB} MB")


def simple_domain_check(question):
    # Block obvious unrelated requests; allow short conversational follow-ups.
    if len(question.strip()) > 2500:
        return False

    off_topic = [
        r"\b(write|compose) (me )?(a )?(poem|song|story)\b",
        r"\bweather (in|today|tomorrow)\b",
        r"\bsolve (this )?(equation|math problem)\b",
        r"\b(explain|teach) python inheritance\b",
    ]

    return not any(re.search(pattern, question.lower()) for pattern in off_topic)


def redact_personal_data(text):
    # Hide common email addresses and phone numbers before LLM requests.
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"(?<!\d)(?:\+94|0)7\d[ -]?\d{3}[ -]?\d{4}(?!\d)", "[PHONE]", text)
    return text
