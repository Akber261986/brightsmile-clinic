"""Optional receptionist email via Resend.

Dormant by design: if RESEND_API_KEY is not configured the module does
nothing and the appointment is still stored in Supabase. Add the key to
.env later to activate it.
"""

from __future__ import annotations

import logging

import httpx

from .config import get_settings
from .knowledge import HUMAN_EMAIL

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"

SUBJECT = "New Appointment Request"


def _render_body(data: dict) -> str:
    return (
        "New Appointment Request\n\n"
        f"Patient: {data['name']}\n"
        f"Email: {data['email']}\n"
        f"Phone: {data['phone']}\n"
        f"Preferred Date: {data['preferred_date']}\n"
        f"Preferred Time: {data['preferred_time']}\n"
        f"Reason: {data.get('reason') or 'Not provided'}\n\n"
        "Status: Pending"
    )


def send_appointment_email(data: dict) -> bool:
    """Send the appointment email. Returns True if sent, False if dormant/failed."""
    settings = get_settings()
    if not settings.email_configured:
        logger.info("RESEND_API_KEY not configured - email skipped (dormant)")
        return False

    payload = {
        "from": settings.sender_email,
        "to": [settings.receptionist_email],
        "subject": SUBJECT,
        "text": _render_body(data),
    }
    try:
        response = httpx.post(
            RESEND_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("Appointment email sent to %s", settings.receptionist_email)
        return True
    except Exception as exc:  # noqa: BLE001 - never break appointment flow
        logger.exception("Appointment email failed: %s", exc)
        return False


def send_patient_status_email(data: dict, *, approved: bool, message: str | None = None) -> bool:
    """Email the patient when reception approves or rejects their request."""
    settings = get_settings()
    if not settings.email_configured:
        logger.info("RESEND_API_KEY not configured - patient email skipped (dormant)")
        return False

    patient_email = (data.get("email") or "").strip()
    if not patient_email:
        logger.warning("Patient email missing - status email skipped")
        return False

    if approved:
        subject = "Your appointment request has been approved"
        text = (
            f"Dear {data.get('name', 'patient')},\n\n"
            "Your appointment request at BrightSmile Dental Clinic has been approved.\n\n"
            f"Preferred date: {data.get('preferred_date')}\n"
            f"Preferred time: {data.get('preferred_time')}\n"
            f"Reason: {data.get('reason') or 'Not provided'}\n\n"
            "Please arrive a few minutes early. If you need to change the time, "
            f"contact reception at {settings.receptionist_email}.\n\n"
            "BrightSmile Dental Clinic"
        )
    else:
        note = (message or "").strip() or "No additional details were provided."
        subject = "Update on your appointment request"
        text = (
            f"Dear {data.get('name', 'patient')},\n\n"
            "We are sorry, but we are unable to confirm your appointment request "
            "at this time.\n\n"
            f"Message from reception:\n{note}\n\n"
            f"Preferred date: {data.get('preferred_date')}\n"
            f"Preferred time: {data.get('preferred_time')}\n\n"
            f"Please contact us at {settings.receptionist_email} if you would like "
            "to book another time.\n\n"
            "BrightSmile Dental Clinic"
        )

    payload = {
        "from": settings.sender_email,
        "to": [patient_email],
        "subject": subject,
        "text": text,
    }
    try:
        response = httpx.post(
            RESEND_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("Patient status email sent to %s", patient_email)
        return True
    except Exception as exc:  # noqa: BLE001 - never break receptionist flow
        logger.exception("Patient status email failed: %s", exc)
        return False