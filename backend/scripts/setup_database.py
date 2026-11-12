
import asyncio
import sys

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
from app.database.database import initialize_database


# Fix asynchronous PostgreSQL connections on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )


# Create application and LangGraph checkpoint tables
async def setup():

    initialize_database()

    async with AsyncPostgresSaver.from_conn_string(
        settings.DATABASE_URL
    ) as saver:

        await saver.setup()

    print("PostgreSQL database ready!")


if __name__ == "__main__":
    asyncio.run(setup())
