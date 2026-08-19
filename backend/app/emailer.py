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