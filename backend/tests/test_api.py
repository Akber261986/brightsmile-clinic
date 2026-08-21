from fastapi.testclient import TestClient

import main
import app.routes
from app.config import Settings
from app.llm import AssistantReply

client = TestClient(main.app)


def _force_rule_based(monkeypatch):
    empty = Settings(gemini_api_key="", openai_api_key="")
    monkeypatch.setattr(app.routes, "get_settings", lambda *a, **k: empty)


def _fake_llm(reply="LLM answer", handoff=False, start_booking=False):
    async def fake(message: str) -> AssistantReply:
        return AssistantReply(reply=reply, handoff=handoff, start_booking=start_booking)

    return fake


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["name"] == "BrightSmile Dental Clinic"


def test_chat_uses_llm_when_configured(monkeypatch):
    monkeypatch.setattr(app.routes, "generate_reply", _fake_llm(reply="Hello there!", start_booking=True))
    res = client.post("/api/chat", json={"message": "hello"})
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "llm"
    assert body["reply"] == "Hello there!"
    assert body["start_booking"] is True


def test_chat_falls_back_to_rule_based(monkeypatch):
    _force_rule_based(monkeypatch)
    res = client.post("/api/chat", json={"message": "what are your opening hours?"})
    body = res.json()
    assert body["intent"] == "hours"
    assert "9:00 AM" in body["reply"]


def test_chat_filling_rule_rule_based(monkeypatch):
    _force_rule_based(monkeypatch)
    res = client.post("/api/chat", json={"message": "how much is a filling?"})
    assert "start at $120" in res.json()["reply"]


def test_chat_rejects_medical_rule_based(monkeypatch):
    _force_rule_based(monkeypatch)
    res = client.post("/api/chat", json={"message": "my tooth hurts"})
    body = res.json()
    assert body["intent"] == "medical_advice"
    assert body["handoff"] is True


def test_chat_llm_failure_uses_fallback(monkeypatch):
    async def broken(message: str):
        return None

    monkeypatch.setattr(app.routes, "generate_reply", broken)
    res = client.post("/api/chat", json={"message": "hello"})
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "llm_fallback"
    assert body["handoff"] is True


def test_appointment_submission(monkeypatch):
    inserted = {}

    def fake_insert(payload):
        inserted.update(payload)
        return [{"id": 1}], None

    monkeypatch.setattr(app.routes, "insert_appointment", fake_insert)
    monkeypatch.setattr(app.routes, "send_appointment_email", lambda payload: False)

    res = client.post(
        "/api/appointments",
        json={
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+1 555-1234",
            "preferred_date": "August 20",
            "preferred_time": "3:00 PM",
            "reason": "Dental cleaning",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert "not confirmed yet" in body["message"]
    assert inserted["name"] == "John Smith"
    assert inserted["status"] == "pending"


def test_list_appointments(monkeypatch):
    rows = [
        {
            "id": 2,
            "name": "Ada",
            "email": "ada@example.com",
            "phone": "555",
            "preferred_date": "Aug 21",
            "preferred_time": "10:00 AM",
            "reason": None,
            "status": "pending",
            "receptionist_message": None,
            "created_at": "2026-08-21T00:00:00Z",
        }
    ]
    monkeypatch.setattr(app.routes, "list_appointments", lambda: (rows, None))
    res = client.get("/api/appointments")
    assert res.status_code == 200
    assert res.json()[0]["name"] == "Ada"


def test_approve_appointment(monkeypatch):
    pending = {
        "id": 1,
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "+1 555-1234",
        "preferred_date": "August 20",
        "preferred_time": "3:00 PM",
        "reason": "Cleaning",
        "status": "pending",
        "receptionist_message": None,
        "created_at": "2026-08-21T00:00:00Z",
    }
    approved = {**pending, "status": "approved"}
    emailed = {}

    monkeypatch.setattr(app.routes, "get_appointment", lambda _id: (pending, None))
    monkeypatch.setattr(app.routes, "update_appointment", lambda _id, data: ([{**approved, **data}], None))
    monkeypatch.setattr(
        app.routes,
        "send_patient_status_email",
        lambda data, approved, message=None: emailed.update({"approved": approved, "email": data["email"]}) or (True, None),
    )

    res = client.post("/api/appointments/1/approve")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["appointment"]["status"] == "approved"
    assert body["email_sent"] is True
    assert emailed["approved"] is True
    assert emailed["email"] == "john@example.com"


def test_reject_appointment(monkeypatch):
    pending = {
        "id": 1,
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "+1 555-1234",
        "preferred_date": "August 20",
        "preferred_time": "3:00 PM",
        "reason": "Cleaning",
        "status": "pending",
        "receptionist_message": None,
        "created_at": "2026-08-21T00:00:00Z",
    }
    emailed = {}

    def fake_update(_id, data):
        return [{**pending, **data}], None

    monkeypatch.setattr(app.routes, "get_appointment", lambda _id: (pending, None))
    monkeypatch.setattr(app.routes, "update_appointment", fake_update)
    monkeypatch.setattr(
        app.routes,
        "send_patient_status_email",
        lambda data, approved, message=None: emailed.update(
            {"approved": approved, "message": message, "email": data["email"]}
        )
        or (True, None),
    )

    res = client.post("/api/appointments/1/reject", json={"message": "No slots that day."})
    assert res.status_code == 200
    body = res.json()
    assert body["appointment"]["status"] == "rejected"
    assert body["appointment"]["receptionist_message"] == "No slots that day."
    assert emailed["approved"] is False
    assert emailed["message"] == "No slots that day."


def test_reject_requires_message(monkeypatch):
    res = client.post("/api/appointments/1/reject", json={"message": ""})
    assert res.status_code == 422


def test_approve_already_decided(monkeypatch):
    decided = {
        "id": 1,
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "+1 555-1234",
        "preferred_date": "August 20",
        "preferred_time": "3:00 PM",
        "reason": "Cleaning",
        "status": "approved",
        "receptionist_message": None,
        "created_at": "2026-08-21T00:00:00Z",
    }
    monkeypatch.setattr(app.routes, "get_appointment", lambda _id: (decided, None))
    res = client.post("/api/appointments/1/approve")
    assert res.status_code == 409


def test_appointment_validation():
    res = client.post(
        "/api/appointments",
        json={
            "name": "John Smith",
            "email": "not-an-email",
            "phone": "+1 555-1234",
            "preferred_date": "August 20",
            "preferred_time": "3:00 PM",
            "reason": "Dental cleaning",
        },
    )
    assert res.status_code == 422