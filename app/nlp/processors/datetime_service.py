import re
from datetime import datetime, time
from typing import Dict, Optional, Tuple, Union, List
from app.nlp.constants import TIME_PATTERNS
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.handlers.conflict_checker import BookingConflictChecker
from app.nlp.handlers.datetime_handler import DateTimeHandler
from app.nlp.processors.technician_service import TechnicianService
from app.nlp.utils.date_time_parser import DateTimeParser


class DateTimeService:
    def __init__(self):
        self.date_time_parser = DateTimeParser()
        self.date_time_handler = DateTimeHandler()

    def handle_date_input(self, user_context: Dict, text: str, specialty: str) -> str:
        simple_date_match = re.fullmatch(r'([a-z]+)\s+(\d{1,2})$', text.lower())
        if simple_date_match:
            date_result, date_desc = self.date_time_parser.parse_date(text)
            if date_result:
                UserContextManager.update_date_context(user_context, date_result)
                UserContextManager.set_awaiting_date(user_context, False)
                UserContextManager.set_awaiting_time(user_context, True)
                return self._prompt_for_time(specialty)
        date_time_result, date_time_desc = self.date_time_parser.parse_date_time(text)
        if date_time_result:
            UserContextManager.update_date_context(user_context, date_time_result.date())
            UserContextManager.update_time_context(user_context, date_time_result)
            conflict_message = TechnicianService.check_and_handle_conflict(
                user_context, date_time_result, date_time_desc)
            if conflict_message:
                return conflict_message
            return TechnicianService.setup_technician_selection(
                user_context, date_time_result, specialty)
        date_result, date_desc = self.date_time_parser.parse_date(text)
        if date_result is None:
            return self._handle_invalid_date()
        UserContextManager.update_date_context(user_context, date_result)
        UserContextManager.set_awaiting_date(user_context, False)
        UserContextManager.set_awaiting_time(user_context, True)
        return self._prompt_for_time(specialty)

    def handle_time_input(self, user_context: Dict, text: str, specialty: str) -> str:
        booking_date = user_context.get("temp_booking_date")
        if not booking_date:
            return self._handle_missing_date(specialty)
        single_digit_match = re.fullmatch(r'(\d{1,2})$', text.strip())
        if single_digit_match:
            hour = int(single_digit_match.group(1))
            UserContextManager.setup_for_ampm_clarification(user_context, hour, 0)
            return self._prompt_for_ampm(hour, 0)
        time_without_ampm = re.search(r'(\d{1,2}):(\d{2})$', text.strip())
        if time_without_ampm and not re.search(r'(am|pm|a\.m\.|p\.m\.)', text.lower()):
            hour = int(time_without_ampm.group(1))
            minute = int(time_without_ampm.group(2))
            UserContextManager.setup_for_ampm_clarification(user_context, hour, minute)
            return self._prompt_for_ampm(hour, minute)
        time_result, time_desc = self.date_time_parser.parse_time(text, booking_date)
        if not time_result:
            return self._handle_invalid_time()
        if isinstance(time_result, tuple):
            hour, minute = time_result
            booking_datetime = datetime.combine(booking_date, time(hour, minute))
        else:
            booking_datetime = time_result
        UserContextManager.update_time_context(user_context, booking_datetime)
        conflict_message = TechnicianService.check_and_handle_conflict(
            user_context, booking_datetime, time_desc)
        if conflict_message:
            return conflict_message
        return TechnicianService.setup_technician_selection(
            user_context, booking_datetime, specialty)

    def handle_ampm_input(self, user_context: Dict, text: str) -> str:
        text_lower = text.lower().strip()
        hour = user_context.get("temp_booking_hour")
        minute = user_context.get("temp_booking_minute", 0)
        booking_date = user_context.get("temp_booking_date")
        specialty = user_context.get("temp_booking_specialty", "Technician")
        if not hour or not booking_date:
            UserContextManager.set_awaiting_ampm(user_context, False)
            UserContextManager.set_awaiting_time(user_context, True)
            return self._handle_invalid_time()
        am_terms = ["am", "morning", "a.m."]
        pm_terms = ["pm", "afternoon", "evening", "night", "p.m."]
        is_am = any(term in text_lower for term in am_terms)
        is_pm = any(term in text_lower for term in pm_terms)
        if (is_am and is_pm) or (not is_am and not is_pm):
            from app.nlp.constants import MESSAGES
            return MESSAGES["INVALID_AMPM_FORMAT"]
        if is_am:
            if hour == 12:
                hour = 0
        else:
            if hour != 12:
                hour += 12
        booking_datetime = datetime.combine(
            booking_date,
            time(hour, minute)
        )
        UserContextManager.update_time_context(user_context, booking_datetime)
        UserContextManager.set_awaiting_ampm(user_context, False)
        time_str = booking_datetime.strftime("%I:%M %p")
        conflict_message = TechnicianService.check_and_handle_conflict(
            user_context, booking_datetime, time_str)
        if conflict_message:
            return conflict_message
        return TechnicianService.setup_technician_selection(
            user_context, booking_datetime, specialty)

    def handle_conflict_response(self, user_context: Dict, text: str) -> str:
        return self.date_time_handler.handle_conflict_response(text, user_context)

    def _contains_time(self, text: str) -> bool:
        for pattern in TIME_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _create_datetime(self, date_result: datetime.date,
                         time_result: Union[datetime, Tuple[int, int]]) -> datetime:
        if isinstance(time_result, datetime):
            return time_result
        else:
            hour, minute = time_result
            return datetime.combine(date_result, time(hour, minute))

    def _handle_invalid_date(self) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["INVALID_DATE_FORMAT"]

    def _handle_invalid_time(self) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["TIME_ERROR"]

    def _handle_missing_date(self, specialty: str) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["DATE_PROMPT"].format(specialty=specialty)

    def _prompt_for_time(self, specialty: str) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["TIME_PROMPT"].format(specialty=specialty)

    def _prompt_for_ampm(self, hour: int, minute: int) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["AMPM_PROMPT"].format(hour=hour, minute=minute)

    def _prompt_for_different_time(self, specialty: str) -> str:
        from app.nlp.constants import MESSAGES
        return MESSAGES["DIFFERENT_TIME_PROMPT"].format(specialty=specialty)
