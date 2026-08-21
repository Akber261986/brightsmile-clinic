"""Pydantic request/response models for the chatbot API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

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


class AppointmentOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    preferred_date: str
    preferred_time: str
    reason: Optional[str] = None
    status: str
    receptionist_message: Optional[str] = None
    created_at: Optional[Union[datetime, str]] = None


class AppointmentRejectRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class AppointmentDecisionResponse(BaseModel):
    ok: bool
    message: str
    appointment: AppointmentOut
    email_sent: bool = False
    email_error: Optional[str] = None
    