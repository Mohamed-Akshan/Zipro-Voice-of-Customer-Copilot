from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents.graph import build_graph
from app.api.routes import router
from app.core.config import settings
from app.database.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # PostgreSQL stores business data and LangGraph conversation checkpoints.
    initialize_database()

    async with AsyncPostgresSaver.from_conn_string(settings.DATABASE_URL) as saver:
        await saver.setup()
        app.state.graph = build_graph(saver)
        yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Upload-Token"]
)
