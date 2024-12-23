import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from auto_review_tool.api import review
from auto_review_tool.core.logging_config import setup_logging
from auto_review_tool.core.redis_client import redis_client

setup_logging()
logger = logging.getLogger("auto_review_tool")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> None:
    """Application life cycle."""
    await redis_client.connect()
    yield
    await redis_client.close()


app = FastAPI(
    title="Auto review tool",
    description="API for automatic code review.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(review.router, prefix="/api", tags=["Review"])
