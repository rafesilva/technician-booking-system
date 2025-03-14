from datetime import datetime
from typing import Dict, Optional, Tuple
from app.db.database import get_booking_by_id, update_booking
from app.nlp.constants import MESSAGES, CANCEL_TERMS, DATE_TIME_FORMATS
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.handlers.base_handler import BaseHandler


class UpdateHandler(BaseHandler):
    def handle_update_request(self, text: str, user_context: Dict) -> str:
        booking_id = BookingDataExtractor.extract_booking_id(text)
        if booking_id is None:
            UserContextManager.set_awaiting_booking_id_for_update(user_context)
            return MESSAGES["PROVIDE_BOOKING_ID_UPDATE"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        self._setup_update_context(user_context, booking_id)
        return self._format_update_prompt(booking)

    def handle_update_time_input(self, text: str, user_context: Dict) -> str:
        if self._is_cancellation(text):
            return self.handle_cancellation(user_context)
        from app.nlp.handlers.time_handler import TimeHandler
        time_handler = TimeHandler()
        time_result = time_handler.parse_time_from_text(text, user_context)
        if not time_result.success:
            return time_result.message
        return self._process_update_time(time_result, user_context)

    def handle_update_booking_time(
            self, booking_date: datetime, time_description: str, user_context: Dict) -> str:
        booking_id = user_context.get("updating_booking_id")
        if not booking_id:
            return MESSAGES["UPDATE_START_OVER"]
        booking = get_booking_by_id(booking_id)
        if not booking:
            return MESSAGES["UPDATE_NOT_FOUND"].format(booking_id=booking_id)
        old_date = booking.booking_time.strftime(DATE_TIME_FORMATS["DATE_ONLY_FORMAT"])
        old_time = booking.booking_time.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        update_booking(booking_id, {"booking_time": booking_date})
        new_date = booking_date.strftime(DATE_TIME_FORMATS["DATE_ONLY_FORMAT"])
        new_time = booking_date.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        return f"Your booking with {booking.technician_name} has been updated from {old_date} at {old_time} to {new_date} at {new_time}."

    @classmethod
    def handle_update_request_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_update_request", text, user_context)

    @classmethod
    def handle_update_time_input_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_update_time_input", text, user_context)

    @classmethod
    def handle_update_booking_time_static(
            cls, booking_date: datetime, time_description: str, user_context: Dict) -> str:
        return cls.static_method_wrapper(
            "handle_update_booking_time", booking_date, time_description, user_context)

    def _setup_update_context(self, user_context: Dict, booking_id: int) -> None:
        UserContextManager.setup_for_booking_update(user_context, booking_id)

    def _format_update_prompt(self, booking: object) -> str:
        booking_time = self.format_datetime(booking.booking_time)
        return (f"You're updating your booking with {booking.technician_name} ({booking.specialty}) "
                f"currently scheduled for {booking_time}. What day would you like to reschedule to?")

    def _process_update_time(self, time_result, user_context: Dict) -> str:
        booking_id = user_context.get("updating_booking_id")
        booking = get_booking_by_id(booking_id)
        if not booking:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        booking_datetime = time_result.booking_time
        update_result = update_booking(booking_id, {"booking_time": booking_datetime})
        if not update_result:
            return MESSAGES["UPDATE_FAILED"]
        booking_time_display = booking_datetime.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        self.reset_context(user_context)
        return MESSAGES["UPDATE_TIME_CONFIRMATION"].format(
            booking_id=booking_id,
            technician_name=booking.technician_name,
            specialty=booking.specialty,
            booking_time=booking_time_display
        )

    def _is_cancellation(self, text: str) -> bool:
        text_lower = text.lower()
        if ("cancel" in text_lower or "cancellation" in text_lower) and (
                "booking" in text_lower or "appointment" in text_lower):
            return False
        return any(term in text_lower for term in CANCEL_TERMS)
