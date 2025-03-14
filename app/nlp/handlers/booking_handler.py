import re
from datetime import datetime, timedelta
from typing import Dict
from app.db.database import get_booking_by_id, delete_booking
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.utils.intent_recognizer import IntentRecognizer
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.constants import (
    MESSAGES,
    CANCEL_TERMS,
    DEFAULT_SPECIALTY,
    PROCESSOR_MESSAGES,
    BOOKING_ID_PATTERN
)
from app.nlp.handlers.base_handler import BaseHandler


class BookingHandler(BaseHandler):
    def handle_booking_request(self, text: str, user_context: Dict) -> str:
        if IntentRecognizer.is_list_bookings_request(text):
            UserContextManager.reset_context(user_context)
            from app.nlp.handlers.booking_list_handler import BookingListHandler
            booking_list_handler = BookingListHandler()
            return booking_list_handler.handle_list_bookings_request_instance(
                user_context)
        if IntentRecognizer.is_cancellation_request(text):
            UserContextManager.reset_context(user_context)
            from app.nlp.handlers.cancellation_handler import CancellationHandler
            cancellation_handler = CancellationHandler()
            return cancellation_handler.handle_cancellation_request(text, user_context)
        if IntentRecognizer.is_update_request(text):
            UserContextManager.reset_context(user_context)
            from app.nlp.handlers.update_handler import UpdateHandler
            update_handler = UpdateHandler()
            return update_handler.handle_update_request(text, user_context)
        specialty = BookingDataExtractor.extract_specialty(text)
        if specialty:
            UserContextManager.set_temp_specialty(user_context, specialty)
            parser = DateTimeParser()
            datetime_result = parser.parse_date_time(text)
            if datetime_result[0]:
                booking_datetime, datetime_description = datetime_result
                UserContextManager.update_date_context(user_context, booking_datetime.date())
                UserContextManager.update_time_context(user_context, booking_datetime)
                from app.nlp.processors.technician_service import TechnicianService
                time_str = booking_datetime.strftime("%I:%M %p")
                conflict_message = TechnicianService.check_and_handle_conflict(
                    user_context, booking_datetime, time_str)
                if conflict_message:
                    return conflict_message
                return TechnicianService.setup_technician_selection(
                    user_context, booking_datetime, specialty)
            UserContextManager.set_awaiting_date(user_context)
            date_result = parser.parse_date(text)
            if date_result[0]:
                booking_date, date_description = date_result
                UserContextManager.update_date_context(user_context, booking_date)
                UserContextManager.set_awaiting_time(user_context)
                return MESSAGES["TIME_PROMPT"].format(specialty=specialty)
            return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
        UserContextManager.set_awaiting_specialty(user_context)
        return MESSAGES["SPECIALTY_PROMPT"]

    def handle_booking_id_inquiry(self, user_context: Dict) -> str:
        last_booking_id = user_context.get("last_booking_id")
        if last_booking_id:
            booking = get_booking_by_id(last_booking_id)
            if booking:
                from app.nlp.constants import DATE_TIME_FORMATS
                booking_time = booking.booking_time.strftime(
                    DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
                return f"Your most recent booking (ID: {last_booking_id}) is with {booking.technician_name} ({booking.specialty}) on {booking_time}."
        return "I don't have any recent booking information. Would you like to make a new booking or check your existing bookings?"

    def handle_cancellation_with_id(self, text: str, user_context: Dict) -> str:
        if any(term in text.lower()
               for term in CANCEL_TERMS) and not text.lower().startswith("cancel"):
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
            return MESSAGES["PROCESS_CANCELLED"]
        try:
            booking_id = int(text.strip())
        except ValueError:
            booking_id = BookingDataExtractor.extract_booking_id(text)
            if booking_id is None:
                return PROCESSOR_MESSAGES["PROVIDE_VALID_BOOKING_ID"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
        delete_booking(booking_id)
        from app.nlp.constants import DATE_TIME_FORMATS
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        return PROCESSOR_MESSAGES["BOOKING_CANCELLED"].format(
            technician_name=booking.technician_name, booking_time=booking_time)

    def handle_update_with_id(self, text: str, user_context: Dict) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            return MESSAGES["PROCESS_CANCELLED"]
        try:
            booking_id = int(text.strip())
        except ValueError:
            booking_id = BookingDataExtractor.extract_booking_id(text)
            if booking_id is None:
                return PROCESSOR_MESSAGES["PROVIDE_VALID_BOOKING_ID"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        UserContextManager.setup_for_booking_update_with_specialty(
            user_context, booking_id, booking.specialty)
        from app.nlp.constants import DATE_TIME_FORMATS
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        return PROCESSOR_MESSAGES["UPDATE_BOOKING_PROMPT"].format(
            technician_name=booking.technician_name,
            specialty=booking.specialty,
            booking_time=booking_time
        )

    def _handle_booking_update_request(self, text: str, user_context: Dict) -> str:
        booking_id_match = re.search(BOOKING_ID_PATTERN, text, re.IGNORECASE)
        if not booking_id_match:
            return MESSAGES["PROVIDE_BOOKING_ID_UPDATE"]
        booking_id = int(booking_id_match.group(1))
        UserContextManager.setup_for_booking_update(user_context, booking_id)
        return MESSAGES["UPDATE_BOOKING_PROMPT"].format(booking_id=booking_id)

    def _create_default_context(self) -> Dict:
        return UserContextManager.create_default_context()
