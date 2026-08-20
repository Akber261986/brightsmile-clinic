"""API routes: chat matching and appointment submission."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from . import knowledge
from .config import get_settings
from .emailer import send_appointment_email, send_patient_status_email
from .engine import match_intent
from .llm import fallback_reply, generate_reply
from .schemas import (
    AppointmentDecisionResponse,
    AppointmentOut,
    AppointmentRejectRequest,
    AppointmentRequest,
    AppointmentResponse,
    ChatRequest,
    ChatResponse,
)
from .supabase_db import get_appointment, insert_appointment, list_appointments, update_appointment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "name": knowledge.CLINIC_NAME,
        "engine": "llm" if settings.llm_configured else "rule-based",
    }


@router.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    settings = get_settings()
    if settings.llm_configured:
        reply = await generate_reply(req.message)
        if reply:
            return ChatResponse(
                intent="llm",
                reply=reply.reply,
                handoff=reply.handoff,
                start_booking=reply.start_booking,
            )
        logger.warning("LLM unavailable, falling back to rule-based engine")
        reply = fallback_reply()
        return ChatResponse(intent="llm_fallback", reply=reply.reply, handoff=reply.handoff, start_booking=reply.start_booking)

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


@router.get("/api/appointments", response_model=list[AppointmentOut])
def get_appointments() -> list[AppointmentOut]:
    rows, error = list_appointments()
    if error:
        logger.error("Failed to list appointments: %s", error)
        raise HTTPException(status_code=500, detail="Could not load appointment requests.")
    return rows or []


def _require_pending(appointment_id: int) -> dict:
    row, error = get_appointment(appointment_id)
    if error:
        logger.error("Failed to load appointment %s: %s", appointment_id, error)
        raise HTTPException(status_code=500, detail="Could not load the appointment request.")
    if row is None:
        raise HTTPException(status_code=404, detail="Appointment request not found.")
    if row.get("status") != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"This request is already {row.get('status')}.",
        )
    return row


@router.post("/api/appointments/{appointment_id}/approve", response_model=AppointmentDecisionResponse)
def approve_appointment(appointment_id: int) -> AppointmentDecisionResponse:
    _require_pending(appointment_id)
    rows, error = update_appointment(appointment_id, {"status": "approved"})
    if error:
        logger.error("Failed to approve appointment %s: %s", appointment_id, error)
        raise HTTPException(status_code=500, detail="Could not approve the appointment.")
    if not rows:
        raise HTTPException(status_code=404, detail="Appointment request not found.")

    updated = rows[0]
    send_patient_status_email(updated, approved=True)
    return AppointmentDecisionResponse(
        ok=True,
        message="Appointment approved and confirmation emailed to the patient.",
        appointment=updated,
    )


@router.post("/api/appointments/{appointment_id}/reject", response_model=AppointmentDecisionResponse)
def reject_appointment(appointment_id: int, req: AppointmentRejectRequest) -> AppointmentDecisionResponse:
    _require_pending(appointment_id)
    note = req.message.strip()
    rows, error = update_appointment(
        appointment_id,
        {"status": "rejected", "receptionist_message": note},
    )
    if error:
        logger.error("Failed to reject appointment %s: %s", appointment_id, error)
        raise HTTPException(status_code=500, detail="Could not reject the appointment.")
    if not rows:
        raise HTTPException(status_code=404, detail="Appointment request not found.")

    updated = rows[0]
    send_patient_status_email(updated, approved=False, message=note)
    return AppointmentDecisionResponse(
        ok=True,
        message="Appointment rejected and email sent to the patient.",
        appointment=updated,
    )