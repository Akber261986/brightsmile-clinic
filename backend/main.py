"""BrightSmile Dental Clinic chatbot agent - FastAPI entry point.

Run locally with:  uv run uvicorn main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.llm import warmup
from app.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    if settings.llm_configured:
        warmup()
    yield


app = FastAPI(title="BrightSmile Chatbot Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)