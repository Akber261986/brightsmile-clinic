"""Boundary tests for the LLM system prompt (guardrails)."""

from app import knowledge
from app.prompts import build_system_prompt

PROMPT = build_system_prompt().lower()


def test_prompt_contains_clinic_identity():
    assert knowledge.CLINIC_NAME.lower() in PROMPT


def test_prompt_contains_pricing_rule():
    assert "never state an exact total price" in PROMPT
    assert "$120" in PROMPT
    assert "may vary" in PROMPT


def test_prompt_contains_medical_boundary():
    assert "never give medical advice" in PROMPT
    assert "handoff" in PROMPT


def test_prompt_contains_booking_instructions():
    assert "start_booking" in PROMPT


def test_prompt_contains_human_contact():
    assert knowledge.HUMAN_EMAIL.lower() in PROMPT
    assert knowledge.HUMAN_PHONE in PROMPT


def test_prompt_contains_all_services():
    for service in knowledge.SERVICES.values():
        assert service["label"].lower() in PROMPT


def test_prompt_contains_opening_hours():
    assert "9:00 am" in PROMPT
    assert "10:00 am" in PROMPT
    assert "sunday" in PROMPT