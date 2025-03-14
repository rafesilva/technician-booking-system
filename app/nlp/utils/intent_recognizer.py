import re
from app.nlp.constants import (
    BOOKING_KEYWORDS,
    INQUIRY_KEYWORDS,
    ID_KEYWORDS,
    CANCEL_KEYWORDS,
    BOOKING_REFERENCE_KEYWORDS,
    LIST_KEYWORDS,
    BOOKING_PLURAL_KEYWORDS,
    LIST_BOOKINGS_EXACT_MATCHES,
    GREETING_KEYWORDS,
    UPDATE_KEYWORDS,
    UPDATE_COMMANDS,
    UPDATE_BOOKING_PATTERN,
    SIMPLE_DIGIT_PATTERN,
    SPECIFIC_BOOKING_INQUIRY_PATTERNS
)


class IntentRecognizer:
    @staticmethod
    def is_booking_request(text: str) -> bool:
        text = text.lower()
        return any(keyword in text for keyword in BOOKING_KEYWORDS)

    @staticmethod
    def is_booking_id_inquiry(text: str) -> bool:
        text = text.lower()
        has_inquiry = any(keyword in text for keyword in INQUIRY_KEYWORDS)
        has_id = any(keyword in text for keyword in ID_KEYWORDS)
        return (has_inquiry and has_id) or "booking id" in text

    @staticmethod
    def is_cancellation_request(text: str) -> bool:
        text = text.lower()
        has_cancel = any(keyword in text for keyword in CANCEL_KEYWORDS)
        has_booking = any(
            keyword in text for keyword in BOOKING_REFERENCE_KEYWORDS) or "id" in text
        has_id = re.search(SIMPLE_DIGIT_PATTERN, text) is not None
        return has_cancel and (has_booking or has_id)

    @staticmethod
    def is_list_bookings_request(text: str) -> bool:
        text = text.lower()
        for match in LIST_BOOKINGS_EXACT_MATCHES:
            if match in text:
                return True
        has_list = any(keyword in text for keyword in LIST_KEYWORDS)
        has_booking = any(keyword in text for keyword in BOOKING_PLURAL_KEYWORDS)
        return has_list and has_booking

    @staticmethod
    def is_greeting(text: str) -> bool:
        text = text.lower()
        return any(greeting in text for greeting in GREETING_KEYWORDS)

    @staticmethod
    def is_update_request(text: str) -> bool:
        text = text.lower()
        if re.search(UPDATE_BOOKING_PATTERN, text):
            return True
        for keyword in UPDATE_KEYWORDS:
            if keyword in text and any(
                    ref in text for ref in BOOKING_REFERENCE_KEYWORDS + ["a booking", "an appointment"]):
                return True
        has_update = any(update_command in text for update_command in UPDATE_COMMANDS)
        has_booking = any(
            keyword in text for keyword in BOOKING_REFERENCE_KEYWORDS) or "id" in text
        return has_update and (has_booking or re.search(SIMPLE_DIGIT_PATTERN, text))

    @staticmethod
    def is_specific_booking_inquiry(text: str) -> bool:
        text = text.lower()
        for pattern in SPECIFIC_BOOKING_INQUIRY_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return True
        return False
