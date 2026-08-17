"""Rule-based intent engine for the BrightSmile clinic chatbot.

Matches a free-text message against the approved knowledge base using
keyword rules, ordered by priority (first match wins). Responses come
exclusively from app.knowledge.
"""

from __future__ import annotations

import re

from . import knowledge

PRICE_WORDS = ("price", "prices", "cost", "costs", "charge", "charges", "much", "paid", "fee")

GREETING_WORDS = ("hi", "hello", "hey", "hiya", "howdy")
GREETING_PHRASES = ("good morning", "good afternoon", "good evening")

MEDICAL_WORDS = (
    "toothache",
    "tooth hurt",
    "teeth hurt",
    "tooth pain",
    "pain",
    "painful",
    "bleeding",
    "swollen",
    "swelling",
    "abscess",
    "sore",
    "aching",
    "ache",
    "inflamed",
    "root canal",
    "gum disease",
    "gingivitis",
    "prescribe",
    "prescription",
    "medication",
    "medicine",
    "diagnose",
    "diagnosis",
    "infected",
    "infection",
    "is it serious",
    "is this normal",
    "what should i do",
    "should i worry",
    "medical advice",
    "treatment advice",
    "how to treat",
    "does it need antibiotics",
    "numb",
)

CANCEL_WORDS = ("cancel", "canceled", "cancelled", "cancellation", "reschedule", "rescheduling")

HUMAN_WORDS = (
    "talk to a human",
    "talk to someone",
    "talk to a person",
    "speak to someone",
    "speak to a human",
    "speak to a person",
    "speak to an agent",
    "real person",
    "human agent",
    "receptionist",
    "contact reception",
    "email reception",
    "call reception",
    "reach reception",
    "i need to speak",
    "i want to speak",
    "someone at the clinic",
    "actual human",
)

LOCATION_WORDS = ("location", "located", "where are you", "address", "find you", "are you based")

BOOK_WORDS = (
    "book an appointment",
    "book a appointment",
    "book appointment",
    "booking",
    "book now",
    "make an appointment",
    "make a appointment",
    "schedule an appointment",
    "schedule a appointment",
    "request an appointment",
    "request a appointment",
    "want to book",
    "need to book",
)

HOURS_WORDS = (
    "opening hours",
    "open today",
    "are you open",
    "what time do you open",
    "when do you open",
    "when are you open",
    "what time are you open",
    "when are you available",
    "are you open on",
    "open on sunday",
    "open on saturday",
    "weekend hours",
    "opening time",
    "closing time",
    "closed on",
)

APPT_NEEDED_PHRASES = (
    "need an appointment",
    "need appointment",
    "appointment required",
    "is an appointment required",
    "do i need an appointment",
    "do i need appointment",
    "walk in",
    "walk-in",
    "without an appointment",
    "without appointment",
)


class IntentResult:
    def __init__(self, intent: str, reply: str, handoff: bool = False, start_booking: bool = False):
        self.intent = intent
        self.reply = reply
        self.handoff = handoff
        self.start_booking = start_booking

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "reply": self.reply,
            "handoff": self.handoff,
            "start_booking": self.start_booking,
        }


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    return any(word in text for word in words)


def _smart(patterns: tuple[str, ...], text: str) -> bool:
    """Case-insensitive word-boundary search for one or more phrases."""
    return any(re.search(rf"\b{re.escape(p)}\b", text) for p in patterns)


def _price_response(service: str) -> str:
    if service == "dental_filling":
        return knowledge.FILLING_PRICE_RESPONSE
    info = knowledge.SERVICES[service]
    if service == "emergency_consultation":
        return f"An emergency consultation costs {info['price']}."
    return f"{info['label']} costs {info['price']}."


def _service_for_keyword(text: str) -> str | None:
    """Return the service key whose keyword appears in text, else None."""
    for service_key, info in knowledge.SERVICES.items():
        if _has_any(text, info["keywords"]):
            return service_key
    return None


def _match_prices(text: str) -> IntentResult | None:
    if not _has_any(text, PRICE_WORDS):
        return None
    service_key = _service_for_keyword(text)
    if service_key:
        return IntentResult(f"price_{service_key}", _price_response(service_key))
    return None


def match_intent(message: str) -> IntentResult:
    text = message.lower().strip()

    greeting_hit = _smart(GREETING_WORDS, text) or _has_any(text, GREETING_PHRASES)
    if greeting_hit and len(text.split()) <= 4:
        return IntentResult("greeting", knowledge.RESPONSES["greeting"])

    if _has_any(text, MEDICAL_WORDS):
        return IntentResult("medical_advice", knowledge.RESPONSES["medical_refusal"], handoff=True)

    price = _match_prices(text)
    if price:
        return price

    if "emergency" in text:
        return IntentResult("emergency", knowledge.RESPONSES["emergency"])

    if "insurance" in text:
        return IntentResult("insurance", knowledge.RESPONSES["insurance"])

    if _has_any(text, ("what services", "do you offer", "what do you do", "services", "treatments", "price list")):
        return IntentResult("services", knowledge.RESPONSES["services"])

    if _has_any(text, CANCEL_WORDS):
        return IntentResult("cancel", knowledge.RESPONSES["cancel"])

    if _has_any(text, HUMAN_WORDS):
        return IntentResult("human", knowledge.RESPONSES["human"], handoff=True)

    if _has_any(text, APPT_NEEDED_PHRASES):
        return IntentResult("appointment_needed", knowledge.RESPONSES["appointment_needed"])

    if _has_any(text, BOOK_WORDS) or _smart(("book",), text):
        return IntentResult("booking", knowledge.RESPONSES["booking"], start_booking=True)

    if _has_any(text, LOCATION_WORDS) or ("where" in text and "you" in text):
        return IntentResult("location", knowledge.RESPONSES["location"])

    if _has_any(text, HOURS_WORDS) or "open" in text or "closed" in text:
        return IntentResult("hours", knowledge.RESPONSES["hours"])

    service_key = _service_for_keyword(text)
    if service_key:
        return IntentResult(f"service_{service_key}", _price_response(service_key))

    return IntentResult("fallback", knowledge.RESPONSES["fallback"], handoff=True)