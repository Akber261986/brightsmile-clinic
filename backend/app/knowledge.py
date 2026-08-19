"""BrightSmile Dental Clinic knowledge base.

All answer text is taken verbatim (or minimally adapted) from the approved
clinic documentation. The chatbot must never invent facts beyond this file.
"""

CLINIC_NAME = "BrightSmile Dental Clinic"

OPENING_HOURS = {
    "monday_friday": "9:00 AM - 6:00 PM",
    "saturday": "10:00 AM - 2:00 PM",
    "sunday": "Closed",
}

SERVICES = {
    "dental_cleaning": {
        "label": "Dental cleaning",
        "price": "$80",
        "keywords": ["clean", "cleaning", "polish"],
    },
    "dental_examination": {
        "label": "Dental examination",
        "price": "$50",
        "keywords": ["exam", "examination", "checkup", "check-up", "check up"],
    },
    "teeth_whitening": {
        "label": "Teeth whitening",
        "price": "$250",
        "keywords": ["whiten", "whitening", "bleach"],
    },
    "dental_filling": {
        "label": "Dental filling",
        "price": "starting at $120",
        "keywords": ["filling", "fill"],
    },
    "emergency_consultation": {
        "label": "Emergency consultation",
        "price": "$100",
        "keywords": ["emergency consultation", "emergency consult"],
    },
}

FILLING_PRICE_RESPONSE = (
    "Dental fillings start at $120. The final cost may vary depending on the "
    "treatment required. Please contact our clinic for an exact estimate."
)

APPOINTMENT_CONFIRMATION = (
    "Your appointment request has been received and sent to our reception team. "
    "Your appointment is not confirmed yet. Our receptionist will contact you "
    "to confirm availability."
)

HUMAN_EMAIL = "reception@brightsmileclinic.com"
HUMAN_PHONE = "+1 555-0182"

RESPONSES = {
    "greeting": (
        "Hello! Welcome to BrightSmile Dental Clinic. I can help you with our "
        "services, prices, opening hours, and appointment requests. "
        "How can I help you today?"
    ),
    "hours": (
        "Our opening hours are:\n"
        "Monday - Friday: 9:00 AM - 6:00 PM\n"
        "Saturday: 10:00 AM - 2:00 PM\n"
        "Sunday: Closed"
    ),
    "services": (
        "We offer the following services:\n"
        "Dental cleaning - $80\n"
        "Dental examination - $50\n"
        "Teeth whitening - $250\n"
        "Dental filling - starting at $120\n"
        "Emergency consultation - $100\n\n"
        "Please note final costs may vary for some treatments. "
        "Contact our clinic for an exact estimate."
    ),
    "insurance": (
        "Yes. We accept most major dental insurance plans. Patients should "
        "contact reception to confirm whether their specific plan is accepted."
    ),
    "emergency": (
        "Yes. Emergency consultations are available during clinic hours, "
        "subject to availability."
    ),
    "location": (
        "BrightSmile Dental Clinic, 125 Main Street, Springfield."
    ),
    "appointment_needed": (
        "Appointments are recommended. Walk-ins may be accepted depending on "
        "availability."
    ),
    "booking": (
        "I can collect an appointment request for you. A receptionist will "
        "review the request and contact you to confirm the appointment. "
        "Would you like to book now?"
    ),
    "cancel": (
        "Please contact reception as soon as possible if you need to cancel "
        "or reschedule."
    ),
    "medical_refusal": (
        "I'm sorry, but I can't provide medical advice, diagnosis, or "
        "treatment recommendations. For any medical concern, please speak "
        "with our team directly.\n\n"
        "Email: reception@brightsmileclinic.com\n"
        "Phone: +1 555-0182"
    ),
    "human": (
        "You can reach our reception team directly:\n"
        "Email: reception@brightsmileclinic.com\n"
        "Phone: +1 555-0182\n\n"
        "We will be happy to help you."
    ),
    "fallback": (
        "I'm sorry, I don't have information about that. Our reception team "
        "can assist you:\n"
        "Email: reception@brightsmileclinic.com\n"
        "Phone: +1 555-0182"
    ),
}