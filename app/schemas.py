"""Pydantic request/response models for the chatbot API."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    intent: str
    reply: str
    handoff: bool = False
    start_booking: bool = False


class AppointmentRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=50)
    preferred_date: str = Field(min_length=1, max_length=100)
    preferred_time: str = Field(min_length=1, max_length=100)
    reason: Optional[str] = Field(default=None, max_length=500)


class AppointmentResponse(BaseModel):
    ok: bool
    message: str
    id: Optional[int] = None
    