"""API routes: chat matching and appointment submission."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from . import knowledge
from .emailer import send_appointment_email
from .engine import match_intent
from .schemas import AppointmentRequest, AppointmentResponse, ChatRequest, ChatResponse
from .supabase_db import insert_appointment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/health")
def health() -> dict:
    return {"status": "ok", "name": knowledge.CLINIC_NAME}


@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    result = match_intent(req.message)
    return ChatResponse(
        intent=result.intent,
        reply=result.reply,
        handoff=result.handoff,
        start_booking=result.start_booking,
    )


@router.post("/api/appointments", response_model=AppointmentResponse)
def create_appointment(req: AppointmentRequest) -> AppointmentResponse:
    payload = {
        "name": req.name.strip(),
        "email": req.email,
        "phone": req.phone.strip(),
        "preferred_date": req.preferred_date.strip(),
        "preferred_time": req.preferred_time.strip(),
        "reason": (req.reason or "").strip(),
        "status": "pending",
    }

    rows, error = insert_appointment(payload)
    if error:
        logger.error("Failed to store appointment: %s", error)
        raise HTTPException(status_code=500, detail="Could not store the appointment request. Please try again or contact reception.")

    send_appointment_email(payload)

    appointment_id = rows[0].get("id") if rows else None
    return AppointmentResponse(ok=True, message=knowledge.APPOINTMENT_CONFIRMATION, id=appointment_id)