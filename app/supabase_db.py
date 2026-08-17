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