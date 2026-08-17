from fastapi.testclient import TestClient

import main
import app.routes
import app.supabase_db
import app.emailer

client = TestClient(main.app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["name"] == "BrightSmile Dental Clinic"


def test_chat_returns_intent():
    res = client.post("/api/chat", json={"message": "what are your opening hours?"})
    assert res.status_code == 200
    body = res.json()
    assert body["intent"] == "hours"
    assert "9:00 AM" in body["reply"]


def test_chat_filling_rule():
    res = client.post("/api/chat", json={"message": "how much is a filling?"})
    assert res.status_code == 200
    assert "start at $120" in res.json()["reply"]


def test_chat_rejects_medical():
    res = client.post("/api/chat", json={"message": "my tooth hurts"})
    body = res.json()
    assert body["intent"] == "medical_advice"
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