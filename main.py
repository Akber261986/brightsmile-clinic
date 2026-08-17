"""BrightSmile Dental Clinic chatbot agent - FastAPI entry point.

Run locally with:  uv run uvicorn main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import router

app = FastAPI(title="BrightSmile Chatbot Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.mount("/widget", StaticFiles(directory="widget"), name="widget")
app.mount("/demo", StaticFiles(directory="frontend", html=True), name="demo")