
import json
from pathlib import Path

import pandas as pd
from docx import Document
from pypdf import PdfReader


# Read a value from a document
def field(text, label):

    for line in text.splitlines():

        if line.startswith(label + ":"):
            return line.split(":", 1)[1].strip()

    return ""


# Convert feedback into the same format
def make_record(row, source):

    return {
        "id": str(row.get("id", "")),
        "source_type": source,
        "feedback_date": str(row.get("date", ""))[:10],
        "text": str(
            row.get("text") or row.get("request_text") or ""
        ),
        "rating": row.get("rating") or None,
        "customer_id": row.get("customer_id") or None,
        "incident_id": row.get("incident_id") or None,
        "issue_hint": row.get("issue_hint") or None,
        "metadata": dict(row)
    }


# Load customer feedback based on file type
def load_document(file_path):

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":

        rows = pd.read_csv(path).fillna("").to_dict("records")
        source = "app_review"

    elif extension == ".json":

        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        rows = data["tickets"] if isinstance(data, dict) else data
        source = "support_ticket"

    elif extension == ".xlsx":

        rows = pd.read_excel(path).fillna("").to_dict("records")
        source = "feature_request"

    elif extension == ".docx":

        word = Document(path)

        text = "\n".join(
            paragraph.text
            for paragraph in word.paragraphs
        )

        rows = [{
            "id": field(text, "Interview ID") or path.stem,
            "date": field(text, "Date"),
            "text": text,
            "issue_hint": field(text, "Issue category"),
            "customer_id": field(text, "Customer ID"),
            "incident_id": field(text, "Incident ID")
        }]

        source = "interview"

    elif extension == ".pdf":

        rows = []

        for number, page in enumerate(
            PdfReader(path).pages,
            start=1
        ):

            text = page.extract_text() or ""

            if not text.strip():
                continue

            rows.append({
                "id": field(text, "Survey ID") or f"{path.stem}-{number}",
                "date": field(text, "Date"),
                "text": text,
                "issue_hint": field(text, "Issue category"),
                "customer_id": field(text, "Customer ID"),
                "incident_id": field(text, "Incident ID"),
                "page": number
            })

        source = "survey"

    else:
        raise ValueError("Unsupported file format")

    return [
        make_record(row, source)
        for row in rows
    ]


# Load every supported file in the data folder
def load_folder(folder):

    records = []

    for path in sorted(Path(folder).rglob("*")):

        if path.suffix.lower() in {
            ".csv", ".json", ".xlsx", ".docx", ".pdf"
        }:

            records.extend(load_document(path))

    return records
