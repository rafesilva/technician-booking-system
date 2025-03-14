import re
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Tuple
from app.db.database import get_all_bookings, get_booking_by_id
from app.nlp.constants import (
    MESSAGES,
    DATE_TIME_FORMATS,
    PROCESSOR_MESSAGES,
    CANCEL_TERMS,
    SPECIFIC_BOOKING_INQUIRY_PATTERNS,
    TECHNICIAN_TYPES,
    UPDATE_BOOKING_WITH_TIME_PATTERN,
    NON_OFFERED_SPECIALTIES,
    UNSUPPORTED_SPECIALTY_MESSAGE,
    GREETING_KEYWORDS
)
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.handlers.booking_handler import BookingHandler
from app.nlp.handlers.booking_list_handler import BookingListHandler
from app.nlp.handlers.datetime_handler import DateTimeHandler
from app.nlp.handlers.technician_handler import TechnicianHandler
from app.nlp.handlers.update_handler import UpdateHandler
from app.nlp.handlers.conflict_checker import BookingConflictChecker
from app.nlp.processors.booking_service import BookingService
from app.nlp.processors.datetime_service import DateTimeService
from app.nlp.processors.specialty_service import SpecialtyService
from app.nlp.processors.technician_service import TechnicianService
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.utils.intent_recognizer import IntentRecognizer


class HandlerService:
    def __init__(self):
        self.booking_service = BookingService()
        self.datetime_service = DateTimeService()
        self.specialty_service = SpecialtyService()

    def handle_greeting(self, user_context: Dict, text: str) -> str:
        return MESSAGES["GREETING"]

    def handle_booking_id_inquiry(self, user_context: Dict, text: str) -> str:
        return BookingHandler().handle_booking_id_inquiry(user_context)

    def handle_specific_booking_inquiry(self, user_context: Dict, text: str) -> str:
        booking_id = None
        for pattern in SPECIFIC_BOOKING_INQUIRY_PATTERNS:
            match = re.search(pattern, text.lower())
            if match:
                group_index = 3 if pattern != SPECIFIC_BOOKING_INQUIRY_PATTERNS[2] else 2
                booking_id = int(match.group(group_index))
                break
        if booking_id is None:
            booking_id = BookingDataExtractor.extract_booking_id(text)
            if booking_id is None:
                return PROCESSOR_MESSAGES["PROVIDE_VALID_BOOKING_ID"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        return f"Booking #{booking.id}: {booking.technician_name} ({booking.specialty}) on {booking_time}"

    def handle_list_bookings(self, user_context: Dict, text: str) -> str:
        self.reset_context(user_context)
        booking_list_handler = BookingListHandler()
        return booking_list_handler.handle_list_bookings_request(user_context)

    def handle_cancellation(self, user_context: Dict, text: str) -> str:
        self.reset_context(user_context)
        UserContextManager.set_awaiting_booking_id_for_cancel(user_context)
        return PROCESSOR_MESSAGES["PROVIDE_CANCEL_BOOKING_ID"]

    def handle_update(self, user_context: Dict, text: str) -> str:
        self.reset_context(user_context)
        booking_id = BookingDataExtractor.extract_booking_id(text)
        return self.handle_update_booking(user_context, booking_id, text)

    def handle_booking(self, user_context: Dict, text: str) -> str:
        text_lower = text.lower()
        specialty = BookingDataExtractor.extract_specialty(text_lower)
        if specialty:
            date_time_parser = DateTimeParser()
            date_time_result, date_time_desc = date_time_parser.parse_date_time(text)
            if date_time_result:
                UserContextManager.set_temp_specialty(user_context, specialty)
                UserContextManager.update_date_context(user_context, date_time_result.date())
                UserContextManager.update_time_context(user_context, date_time_result)
                conflict_message = TechnicianService.check_and_handle_conflict(
                    user_context, date_time_result, date_time_desc)
                if conflict_message:
                    return conflict_message
                return TechnicianService.setup_technician_selection(
                    user_context, date_time_result, specialty)
            date_result, date_desc = date_time_parser.parse_date(text)
            if date_result:
                UserContextManager.set_temp_specialty(user_context, specialty)
                UserContextManager.update_date_context(user_context, date_result)
                time_result, time_desc = date_time_parser.parse_time(text, date_result)
                if time_result:
                    if isinstance(time_result, tuple):
                        hour, minute = time_result
                        booking_datetime = datetime.combine(date_result, time(hour, minute))
                    else:
                        booking_datetime = time_result
                    UserContextManager.update_time_context(user_context, booking_datetime)
                    conflict_message = TechnicianService.check_and_handle_conflict(
                        user_context, booking_datetime, time_desc)
                    if conflict_message:
                        return conflict_message
                    return TechnicianService.setup_technician_selection(
                        user_context, booking_datetime, specialty)
                UserContextManager.set_awaiting_time(user_context)
                return MESSAGES["TIME_PROMPT"].format(specialty=specialty)
            UserContextManager.set_temp_specialty(user_context, specialty)
            UserContextManager.set_awaiting_date(user_context)
            return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
        for non_offered in NON_OFFERED_SPECIALTIES:
            if non_offered in text_lower:
                return UNSUPPORTED_SPECIALTY_MESSAGE
        UserContextManager.set_awaiting_specialty(user_context)
        return MESSAGES["SPECIALTY_PROMPT"]

    def handle_awaiting_date(self, user_context: Dict, text: str) -> str:
        specialty_change_msg = self.specialty_service.check_and_handle_specialty_change(
            user_context, text)
        if specialty_change_msg:
            return specialty_change_msg
        specialty = user_context.get("temp_booking_specialty", "technician")
        return self.datetime_service.handle_date_input(user_context, text, specialty)

    def handle_awaiting_time(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        if user_context.get("conflict_detected", False):
            text_lower = text.lower().strip()
            negative_responses = ["no", "n", "nope", "negative", "cancel", "nah"]
            if any(resp == text_lower for resp in negative_responses):
                UserContextManager.cancel_booking_process(user_context)
                return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        specialty_change_msg = self.specialty_service.check_and_handle_specialty_change(
            user_context, text)
        if specialty_change_msg:
            return specialty_change_msg
        specialty = user_context.get("temp_booking_specialty", "technician")
        return self.datetime_service.handle_time_input(user_context, text, specialty)

    def handle_awaiting_ampm(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        return self.datetime_service.handle_ampm_input(user_context, text)

    def handle_awaiting_technician(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        technician_handler = TechnicianHandler()
        return technician_handler.handle_technician_input(text, user_context)

    def handle_awaiting_booking_id_for_update(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            return MESSAGES["PROCESS_CANCELLED"]
        if any(greeting in text.lower() for greeting in GREETING_KEYWORDS):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            return MESSAGES["GREETING"]
        if IntentRecognizer.is_booking_request(text):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            specialty = BookingDataExtractor.extract_specialty(text)
            if specialty:
                UserContextManager.set_temp_specialty(user_context, specialty)
                UserContextManager.set_awaiting_date(user_context)
                return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
            return MESSAGES["SPECIALTY_PROMPT"]
        if IntentRecognizer.is_list_bookings_request(text):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            bookings = get_all_bookings()
            if not bookings:
                return MESSAGES["NO_BOOKINGS"]
            return self.format_booking_list(bookings)
        if IntentRecognizer.is_cancellation_request(text):
            UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, True)
            return MESSAGES["PROVIDE_BOOKING_ID_CANCEL"]
        booking_id = BookingService.extract_booking_id_from_text(text)
        if booking_id is None:
            if not re.search(r'\d+', text):
                UserContextManager.set_awaiting_booking_id_for_update(user_context, False)
                return MESSAGES["UNCLEAR_REQUEST"]
            return PROCESSOR_MESSAGES["PROVIDE_VALID_BOOKING_ID"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        UserContextManager.setup_for_booking_update_with_specialty(
            user_context, booking_id, booking.specialty)
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        return PROCESSOR_MESSAGES["UPDATE_BOOKING_PROMPT"].format(
            technician_name=booking.technician_name,
            specialty=booking.specialty,
            booking_time=booking_time
        )

    def handle_awaiting_booking_id_for_cancel(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower()
               for term in CANCEL_TERMS) and not text.lower().startswith("cancel"):
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
            return MESSAGES["PROCESS_CANCELLED"]
        if any(greeting in text.lower() for greeting in GREETING_KEYWORDS):
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
            return MESSAGES["GREETING"]
        if IntentRecognizer.is_booking_request(text):
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
            specialty = BookingDataExtractor.extract_specialty(text)
            if specialty:
                UserContextManager.set_temp_specialty(user_context, specialty)
                UserContextManager.set_awaiting_date(user_context)
                return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
            return MESSAGES["SPECIALTY_PROMPT"]
        if IntentRecognizer.is_list_bookings_request(text):
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
            bookings = get_all_bookings()
            if not bookings:
                return MESSAGES["NO_BOOKINGS"]
            return self.format_booking_list(bookings)
        booking_id = BookingService.extract_booking_id_from_text(text)
        if booking_id is None:
            if not re.search(r'\d+', text):
                UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
                return MESSAGES["UNCLEAR_REQUEST"]
            return PROCESSOR_MESSAGES["PROVIDE_VALID_BOOKING_ID"]
        success, message = BookingService.cancel_booking(booking_id)
        if not success:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        UserContextManager.set_awaiting_booking_id_for_cancel(user_context, False)
        return message

    def handle_awaiting_specialty(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        return self.specialty_service.handle_specialty_input(user_context, text)

    def handle_updating_booking(self, user_context: Dict, text: str) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            self.reset_context(user_context)
            return MESSAGES["PROCESS_CANCELLED"]
        booking_id = user_context.get("updating_booking_id")
        if not booking_id:
            self.reset_context(user_context)
            return PROCESSOR_MESSAGES["UPDATE_START_OVER"]
        booking = get_booking_by_id(booking_id)
        if not booking:
            self.reset_context(user_context)
            return PROCESSOR_MESSAGES["UPDATE_NOT_FOUND"].format(booking_id=booking_id)
        if user_context.get("awaiting_date"):
            return self.handle_awaiting_date(user_context, text)
        if user_context.get("awaiting_update_time"):
            return UpdateHandler().handle_update_time_input(text, user_context)
        if user_context.get("awaiting_ampm"):
            return self.handle_awaiting_ampm(user_context, text)
        self.reset_context(user_context)
        return PROCESSOR_MESSAGES["UPDATE_UNCLEAR_INFO"]

    def handle_update_booking_command(self, user_context: Dict, text: str) -> str:
        booking_id = BookingDataExtractor.extract_booking_id(text)
        return self.handle_update_booking(user_context, booking_id, text)

    def handle_update_booking_pattern(self, user_context: Dict, text: str) -> str:
        booking_id = BookingDataExtractor.extract_booking_id(text)
        if booking_id is None:
            return self.handle_update_booking(user_context, booking_id, text)
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        date_time_parser = DateTimeParser()
        if date_time_parser.contains_date(text) or date_time_parser.contains_time(text):
            try:
                new_date, time_description = date_time_parser.parse_date_time(
                    text, original_datetime=booking.booking_time)
                conflict = BookingConflictChecker.check_conflict(
                    new_date, exclude_booking_id=booking_id)
                if conflict:
                    return PROCESSOR_MESSAGES["BOOKING_CONFLICT"].format(
                        time_description=time_description,
                        technician_name=conflict['technician_name'],
                        specialty=conflict['specialty']
                    )
                success, message = BookingService.update_booking(booking_id, new_date)
                if success:
                    return message
            except Exception:
                UserContextManager.setup_for_booking_update(user_context, booking_id)
                booking_time = booking.booking_time.strftime(
                    DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
                return PROCESSOR_MESSAGES["UPDATE_BOOKING_PROMPT"].format(
                    technician_name=booking.technician_name,
                    specialty=booking.specialty,
                    booking_time=booking_time
                )
        return self.handle_update_booking(user_context, booking_id, text)

    def handle_update_booking(self, user_context: Dict,
                              booking_id: Optional[int], text: str) -> str:
        if booking_id is None:
            UserContextManager.set_awaiting_booking_id_for_update(user_context)
            bookings = get_all_bookings()
            return self.format_booking_list(bookings)
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        UserContextManager.setup_for_booking_update_with_specialty(
            user_context, booking_id, booking.specialty)
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        return PROCESSOR_MESSAGES["UPDATE_BOOKING_PROMPT"].format(
            technician_name=booking.technician_name,
            specialty=booking.specialty,
            booking_time=booking_time
        )

    def handle_technician_request(self, user_context: Dict, text: str) -> str:
        UserContextManager.set_awaiting_specialty(user_context)
        return PROCESSOR_MESSAGES["GENERIC_TECHNICIAN_PROMPT"]

    def handle_unclear_request(self, user_context: Dict, text: str) -> str:
        return PROCESSOR_MESSAGES["UNCLEAR_HELP"]

    def reset_context(self, user_context: Dict, fields: Optional[List[str]] = None) -> None:
        UserContextManager.reset_context(user_context, fields)

    def format_booking_list(self, bookings: List) -> str:
        if not bookings:
            return PROCESSOR_MESSAGES["NO_BOOKINGS_TO_UPDATE"]
        response = PROCESSOR_MESSAGES["PROVIDE_UPDATE_BOOKING_ID"] + "\n\n"
        for booking in bookings:
            booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
            response += f"Booking #{booking.id}: {booking.technician_name} ({booking.specialty}) on {booking_time}\n"
        return response
