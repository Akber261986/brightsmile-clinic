import pytest

from app.engine import match_intent
from app.knowledge import FILLING_PRICE_RESPONSE


def intent_of(text):
    return match_intent(text).intent


def reply_of(text):
    return match_intent(text).reply


def test_greeting():
    assert intent_of("hi") == "greeting"
    assert intent_of("hello") == "greeting"
    assert intent_of("good morning") == "greeting"


def test_greeting_prefix_does_not_override_real_question():
    assert intent_of("hi, how much is a dental cleaning?") == "price_dental_cleaning"


def test_opening_hours():
    assert intent_of("what are your opening hours?") == "hours"
    assert intent_of("are you open on sunday?") == "hours"
    assert intent_of("what time are you open?") == "hours"


def test_prices():
    assert reply_of("how much is dental cleaning?") == "Dental cleaning costs $80."
    assert reply_of("what does an examination cost?") == "Dental examination costs $50."
    assert reply_of("cost of teeth whitening?") == "Teeth whitening costs $250."
    assert reply_of("how much is emergency consultation?") == "An emergency consultation costs $100."


def test_filling_price_never_gives_exact_price():
    reply = reply_of("how much does a filling cost?")
    assert reply == FILLING_PRICE_RESPONSE
    assert "$120" in reply or "120" in reply
    assert "may vary" in reply.lower()


def test_filling_price_canned_in_all_forms():
    for question in ("filling price?", "how much for a filling?", "tell me about fillings", "what do you charge for a dental filling"):
        reply = reply_of(question)
        assert reply == FILLING_PRICE_RESPONSE, question


def test_services_list():
    assert intent_of("what services do you offer?") == "services"
    assert "Dental cleaning" in reply_of("what services do you offer?")


def test_insurance():
    assert intent_of("do you accept insurance?") == "insurance"
    assert "most major dental insurance plans" in reply_of("do you accept insurance?")


def test_emergency():
    assert intent_of("do you offer emergency appointments?") == "emergency"
    assert "subject to availability" in reply_of("do you offer emergency appointments?")


def test_location():
    assert intent_of("where are you located?") == "location"
    assert "125 Main Street" in reply_of("where are you located?")


def test_appointment_needed():
    assert intent_of("do I need an appointment?") == "appointment_needed"
    assert "recommended" in reply_of("do I need an appointment?")


def test_booking():
    assert intent_of("how can I book an appointment?") == "booking"
    assert match_intent("how can I book an appointment?").start_booking is True
    assert intent_of("I want to schedule an appointment") == "booking"


def test_cancel():
    assert intent_of("can I cancel my appointment?") == "cancel"
    assert "contact reception" in reply_of("can I cancel my appointment?")


def test_book_a_cleaning_is_booking_not_price():
    assert intent_of("I want to book a cleaning") == "booking"


def test_medical_advice_refused_and_handoff():
    result = match_intent("my tooth hurts, what should I do?")
    assert result.intent == "medical_advice"
    assert result.handoff is True
    assert "can't provide medical advice" in result.reply


@pytest.mark.parametrize(
    "question",
    [
        "do you prescribe medicine?",
        "my gums are bleeding",
        "is a root canal painful?",
        "should I worry about my swollen gum?",
        "do you give medical advice?",
    ],
)
def test_medical_keywords(question):
    assert match_intent(question).intent == "medical_advice"


def test_human_handoff():
    result = match_intent("I want to talk to a human")
    assert result.handoff is True
    assert "reception@brightsmileclinic.com" in result.reply


def test_fallback_offers_human():
    result = match_intent("do you have parking?")
    assert result.intent == "fallback"
    assert result.handoff is True