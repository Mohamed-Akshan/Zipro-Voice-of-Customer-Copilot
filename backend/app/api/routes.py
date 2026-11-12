
import json
import logging
import tempfile

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Request,
    UploadFile
)
from langchain_core.messages import HumanMessage
from starlette.concurrency import run_in_threadpool

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    DashboardResponse,
    HistoryResponse,
    SourceResponse,
    UploadResponse
)
from app.core.config import settings
from app.core.guardrails import check_upload
from app.core.tracing import get_callbacks
from app.database.database import SessionLocal
from app.database.models import Feedback, UploadedFile
from app.ingestion.ingest import store_feedback, index_feedback
from app.rag.loaders import load_document
from app.rag.retrieval import retriever
from app.services.analytics import dashboard_stats


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# Check backend health
@router.get("/health")
def health():

    return {
        "status": "ok",
        "app": settings.APP_NAME
    }


# Get customer feedback dashboard statistics
@router.get("/dashboard", response_model=DashboardResponse)
def dashboard():

    return dashboard_stats()


# Open original customer feedback
@router.get("/sources/{source_id}", response_model=SourceResponse)
def source_detail(source_id: str):

    with SessionLocal() as session:

        record = session.get(Feedback, source_id)

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Source not found"
            )

        return {
            "id": record.id,
            "source_type": record.source_type,
            "feedback_date": str(record.feedback_date),
            "text": record.text,
            "rating": record.rating
        }


# Run the three-agent AI workflow
@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request):

    try:
        thread_id = (
            str(UUID(body.thread_id))
            if body.thread_id
            else str(uuid4())
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid thread ID"
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        },
        "callbacks": get_callbacks()
    }

    try:
        result = await request.app.state.graph.ainvoke(
            {
                "messages": [
                    HumanMessage(content=body.question)
                ],
                "question": body.question,
                "thread_id": thread_id,
                "retry_count": 0,
                "evidence": [],
                "metrics": {},
                "draft": {},
                "answer": {}
            },
            config=config
        )

    except Exception as error:

        logger.exception("Zipro chat failed")

        raise HTTPException(
            status_code=503,
            detail="AI service unavailable; check server logs"
        ) from error

    return {
        "thread_id": thread_id,
        "answer": result["answer"]
    }


# Retrieve conversation history
@router.get("/history/{thread_id}", response_model=HistoryResponse)
async def history(thread_id: UUID, request: Request):

    config = {
        "configurable": {
            "thread_id": str(thread_id)
        }
    }

    saved = await request.app.state.graph.aget_state(config)

    messages = []

    for message in saved.values.get("messages", []):

        if message.type not in {"human", "ai"}:
            continue

        content = message.content

        if message.type == "ai":

            try:
                content = json.loads(content)

            except (ValueError, TypeError):
                content = {
                    "status": "history",
                    "message": str(content)
                }

        messages.append({
            "role": message.type,
            "content": content
        })

    return {"messages": messages}


# Load and index newly uploaded customer feedback
def process_upload(path, upload_id):

    records = load_document(path)

    if not records or len(records) > 1000:
        raise ValueError(
            "File must contain 1 to 1,000 feedback records"
        )

    for record in records:
        record["id"] = (
            f"UP-{upload_id[:8]}-{record['id']}"
        )

    store_feedback(records, upload_id=upload_id)

    chunks = index_feedback(records)

    # Refresh retrieval after adding new feedback
    retriever.hybrid = None

    return len(records), chunks


# Upload new feedback without an admin token
@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):

    contents = await file.read(
        settings.MAX_UPLOAD_MB * 1024 * 1024 + 1
    )

    try:
        check_upload(
            file.filename or "",
            len(contents)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    upload_id = str(uuid4())

    extension = Path(
        file.filename or ""
    ).suffix.lower()

    with tempfile.TemporaryDirectory() as folder:

        path = Path(folder) / f"{upload_id}{extension}"
        path.write_bytes(contents)

        try:
            count, chunks = await run_in_threadpool(
                process_upload,
                path,
                upload_id
            )

        except Exception as error:

            logger.exception("Zipro upload failed")

            raise HTTPException(
                status_code=400,
                detail="Upload indexing failed; see server logs"
            ) from error

    with SessionLocal.begin() as session:

        session.add(
            UploadedFile(
                id=upload_id,
                filename=file.filename,
                status="indexed",
                record_count=count
            )
        )

    return {
        "status": "indexed",
        "records": count,
        "chunks": chunks,
        "filename": file.filename
    }
