"""Supabase persistence: inserts appointment requests with the secret key.

The secret key is only ever used server-side inside this module and never
exposed to the browser.
"""

from __future__ import annotations

import logging

from supabase import create_client

from .config import get_settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    settings = get_settings()
    if not settings.db_configured:
        raise RuntimeError("Supabase is not configured (SUPABASE_URL / SUPABASE_SECRET_KEY)")
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_secret_key)
    return _client


def insert_appointment(data: dict) -> tuple[list | None, str | None]:
    """Insert one appointment request. Returns (rows, error_message)."""
    try:
        client = _get_client()
        result = client.table("appointments").insert(data).execute()
        rows = result.data or []
        return rows, None
    except Exception as exc:  # noqa: BLE001 - surface a readable error to the API
        logger.exception("Appointment insert failed")
        return None, str(exc)


def list_appointments() -> tuple[list | None, str | None]:
    """Return all appointment requests, newest first."""
    try:
        client = _get_client()
        result = (
            client.table("appointments")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or [], None
    except Exception as exc:  # noqa: BLE001 - surface a readable error to the API
        logger.exception("Appointment list failed")
        return None, str(exc)


def get_appointment(appointment_id: int) -> tuple[dict | None, str | None]:
    """Fetch a single appointment by id."""
    try:
        client = _get_client()
        result = (
            client.table("appointments")
            .select("*")
            .eq("id", appointment_id)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return None, None
        return rows[0], None
    except Exception as exc:  # noqa: BLE001 - surface a readable error to the API
        logger.exception("Appointment fetch failed")
        return None, str(exc)


def update_appointment(appointment_id: int, data: dict) -> tuple[list | None, str | None]:
    """Update one appointment. Returns (rows, error_message)."""
    try:
        client = _get_client()
        result = (
            client.table("appointments")
            .update(data)
            .eq("id", appointment_id)
            .execute()
        )
        return result.data or [], None
    except Exception as exc:  # noqa: BLE001 - surface a readable error to the API
        logger.exception("Appointment update failed")
        return None, str(exc)