"""Optional emails via Resend.

If RESEND_API_KEY is not configured the module does nothing. With the
default onboarding@resend.dev sender, Resend only delivers to the email
on your Resend account — patient addresses need a verified domain.
"""

from __future__ import annotations

import html
import logging

import httpx

from .config import get_settings

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


def _resend_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
        message = payload.get("message") or payload.get("error") or ""
        if isinstance(message, dict):
            message = message.get("message") or str(message)
        if message:
            return str(message)
    except Exception:  # noqa: BLE001
        pass
    text = (response.text or "").strip()
    return text or f"Resend returned HTTP {response.status_code}"


def _send_resend(payload: dict) -> tuple[bool, str | None]:
    settings = get_settings()
    if not settings.email_configured:
        logger.info("RESEND_API_KEY not configured - email skipped (dormant)")
        return False, "Email is not configured (missing RESEND_API_KEY)."

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
        if response.is_error:
            detail = _resend_error_message(response)
            logger.error("Resend rejected email: %s", detail)
            return False, detail
        logger.info("Email sent to %s", payload.get("to"))
        return True, None
    except Exception as exc:  # noqa: BLE001 - never break receptionist flow
        logger.exception("Email request failed: %s", exc)
        return False, str(exc)


def send_appointment_email(data: dict) -> bool:
    """Send the appointment email. Returns True if sent, False if dormant/failed."""
    settings = get_settings()
    payload = {
        "from": settings.sender_email,
        "to": [settings.receptionist_email],
        "subject": SUBJECT,
        "text": _render_body(data),
    }
    sent, _error = _send_resend(payload)
    return sent


def send_patient_status_email(data: dict, *, approved: bool, message: str | None = None) -> tuple[bool, str | None]:
    """Email the patient when reception approves or rejects their request."""
    settings = get_settings()
    patient_email = (data.get("email") or "").strip()
    if not patient_email:
        logger.warning("Patient email missing - status email skipped")
        return False, "Patient email is missing on this appointment."

    name = html.escape(str(data.get("name") or "patient"))
    preferred_date = html.escape(str(data.get("preferred_date") or ""))
    preferred_time = html.escape(str(data.get("preferred_time") or ""))
    reason = html.escape(str(data.get("reason") or "Not provided"))
    reception = html.escape(settings.receptionist_email)

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
        html_body = (
            f"<p>Dear {name},</p>"
            "<p>Your appointment request at BrightSmile Dental Clinic has been <strong>approved</strong>.</p>"
            f"<p>Preferred date: {preferred_date}<br>Preferred time: {preferred_time}<br>Reason: {reason}</p>"
            f"<p>Please arrive a few minutes early. If you need to change the time, contact reception at {reception}.</p>"
            "<p>BrightSmile Dental Clinic</p>"
        )
    else:
        note = (message or "").strip() or "No additional details were provided."
        note_html = html.escape(note).replace("\n", "<br>")
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
        html_body = (
            f"<p>Dear {name},</p>"
            "<p>We are sorry, but we are unable to confirm your appointment request at this time.</p>"
            f"<p><strong>Message from reception:</strong><br>{note_html}</p>"
            f"<p>Preferred date: {preferred_date}<br>Preferred time: {preferred_time}</p>"
            f"<p>Please contact us at {reception} if you would like to book another time.</p>"
            "<p>BrightSmile Dental Clinic</p>"
        )

    payload = {
        "from": settings.sender_email,
        "to": [patient_email],
        "reply_to": settings.receptionist_email,
        "subject": subject,
        "text": text,
        "html": html_body,
    }
    return _send_resend(payload)
