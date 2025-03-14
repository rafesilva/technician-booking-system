import re
from datetime import datetime, time, timedelta
from typing import Dict, Optional, Tuple
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.constants import (
    MESSAGES,
    NEGATIVE_RESPONSES,
    CANCEL_TERMS,
    DEFAULT_SPECIALTY,
    DEFAULT_PLUMBER_SPECIALTY,
    TIME_WITHOUT_AMPM_PATTERN,
    TECHNICIAN_SELECTION_FORMAT,
    TECHNICIAN_OPTION_LINE_FORMAT,
    TECHNICIAN_SELECTION_SUFFIX,
    AMPM_PROMPT_FORMAT,
    DATE_TIME_FORMATS,
    AM_RESPONSE,
    PM_RESPONSE,
)
from app.nlp.handlers.base_handler import BaseHandler
from app.nlp.handlers.conflict_checker import BookingConflictChecker
from app.nlp.managers.technician_manager import TechnicianManager


class DateTimeHandler(BaseHandler):
    def __init__(self):
        pass

    def handle_date_input(self, text: str, user_context: Dict) -> str:
        if self._check_for_list_bookings_request(text, user_context):
            return self._forward_to_list_bookings_handler(user_context)
        if text.lower() in NEGATIVE_RESPONSES:
            return self._handle_negative_date_response(user_context)
        if any(term in text.lower() for term in CANCEL_TERMS):
            UserContextManager.reset_context(user_context)
            return MESSAGES["PROCESS_CANCELLED"]
        date_result = DateTimeParser.parse_date(text)
        if date_result[0] is None:
            return MESSAGES["INVALID_DATE_FORMAT"]
        booking_date, date_description = date_result
        weekday_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"]
        if any(day.lower() in text.lower() for day in weekday_names):
            date_description = booking_date.strftime("%A, %B %d")
        UserContextManager.update_date_context(user_context, booking_date)
        UserContextManager.set_awaiting_date(user_context, False)
        UserContextManager.set_awaiting_time(user_context, True)
        specialty = user_context.get("temp_booking_specialty", "technician")
        return MESSAGES["TIME_PROMPT"].format(
            specialty=specialty) + f" We've scheduled for {date_description}."

    def handle_time_input(self, text: str, user_context: Dict) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            self.reset_context(user_context, ["awaiting_time"])
            return MESSAGES["TIME_SELECTION_CANCELLED"]
        date_time_parser = DateTimeParser()
        booking_date = user_context.get("temp_booking_date")
        if not booking_date:
            return MESSAGES["NO_DATE_SELECTED"]
        single_digit_match = re.fullmatch(r'(\d{1,2})$', text.strip())
        if single_digit_match:
            hour = int(single_digit_match.group(1))
            minute = 0
            if 5 <= hour <= 8:
                pass
            else:
                user_context["temp_booking_hour"] = hour
                user_context["temp_booking_minute"] = minute
                user_context["awaiting_ampm"] = True
                user_context["awaiting_time"] = False
                return AMPM_PROMPT_FORMAT.format(hour=hour, minute=minute)
        time_result, time_desc = date_time_parser.parse_time(text, booking_date)
        if time_result is None:
            time_match = re.search(TIME_WITHOUT_AMPM_PATTERN, text.strip())
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                user_context["temp_booking_hour"] = hour
                user_context["temp_booking_minute"] = minute
                user_context["awaiting_ampm"] = True
                user_context["awaiting_time"] = False
                return AMPM_PROMPT_FORMAT.format(hour=hour, minute=minute)
            return MESSAGES["INVALID_TIME_FORMAT"]
        return self._process_time_input(time_result, user_context)

    def handle_ampm_input(self, text: str, user_context: Dict) -> str:
        text_lower = text.lower()
        if any(term in text_lower for term in CANCEL_TERMS):
            return self.handle_cancellation(user_context)
        hour = user_context.get("temp_booking_hour")
        minute = user_context.get("temp_booking_minute", 0)
        booking_date = user_context.get("temp_booking_date")
        if not hour or not booking_date:
            return MESSAGES["INVALID_AMPM_FORMAT"]
        if text_lower == AM_RESPONSE:
            pass
        elif text_lower == PM_RESPONSE:
            if hour != 12:
                hour += 12
        elif AM_RESPONSE in text_lower:
            pass
        elif PM_RESPONSE in text_lower:
            if hour != 12:
                hour += 12
        else:
            return MESSAGES["INVALID_AMPM_FORMAT"]
        time_dt = datetime(
            year=booking_date.year,
            month=booking_date.month,
            day=booking_date.day,
            hour=hour,
            minute=minute
        )
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        am_pm = "AM" if hour < 12 else "PM"
        time_str = f"{display_hour}:{minute:02d} {am_pm}"
        UserContextManager.update_time_context(user_context, time_dt)
        UserContextManager.set_awaiting_ampm(user_context, False)
        conflict = BookingConflictChecker.check_conflict(time_dt)
        specialty = user_context.get("temp_booking_specialty") or user_context.get(
            "specialty", DEFAULT_SPECIALTY)
        if conflict:
            UserContextManager.set_conflict_detected(user_context, time_dt)
            return MESSAGES["CONFLICT_DETECTED"].format(time_description=time_str)
        return self._setup_technician_selection(user_context, time_dt, specialty)

    def handle_conflict_response(self, text: str, user_context: Dict) -> str:
        text_lower = text.lower().strip()
        affirmative_responses = ["yes", "y", "sure", "ok", "okay", "yep", "yeah", "yea"]
        if any(resp == text_lower for resp in affirmative_responses):
            UserContextManager.clear_conflict(user_context)
            UserContextManager.set_awaiting_time(user_context, True)
            specialty = user_context.get("specialty", DEFAULT_SPECIALTY)
            return MESSAGES["DIFFERENT_TIME_PROMPT"].format(specialty=specialty)
        elif any(resp == text_lower for resp in NEGATIVE_RESPONSES) or any(term in text_lower for term in CANCEL_TERMS):
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["BOOKING_PROCESS_CANCELLED"]
        else:
            parser = DateTimeParser()
            booking_date = user_context.get("temp_booking_date")
            if not booking_date:
                return MESSAGES["INVALID_TIME_FORMAT"]
            time_result = parser.parse_time(text, booking_date)
            if not time_result or time_result[0] is None:
                return MESSAGES["INVALID_TIME_FORMAT"]
            time_dt, time_desc = time_result
            UserContextManager.update_time_context(user_context, time_dt)
            UserContextManager.clear_conflict(user_context)
            conflict = BookingConflictChecker.check_conflict(time_dt)
            if conflict:
                UserContextManager.set_conflict_detected(user_context, time_dt)
                return MESSAGES["CONFLICT_DETECTED"].format(time_description=time_desc)
            specialty = user_context.get("specialty", DEFAULT_SPECIALTY)
            return self._setup_technician_selection(user_context, time_dt, specialty)

    @classmethod
    def handle_date_input_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_date_input", text, user_context)

    @classmethod
    def handle_time_input_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_time_input", text, user_context)

    @classmethod
    def handle_ampm_input_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_ampm_input", text, user_context)

    @classmethod
    def handle_conflict_response_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_conflict_response", text, user_context)

    def _check_for_list_bookings_request(self, text: str, user_context: Dict) -> bool:
        from app.nlp.utils.intent_recognizer import IntentRecognizer
        return IntentRecognizer.is_list_bookings_request(text)

    def _forward_to_list_bookings_handler(self, user_context: Dict) -> str:
        UserContextManager.reset_context(user_context)
        from app.nlp.handlers.booking_list_handler import BookingListHandler
        booking_list_handler = BookingListHandler()
        return booking_list_handler.handle_list_bookings_request_instance(user_context)

    def _handle_negative_date_response(self, user_context: Dict) -> str:
        if user_context.get("updating_booking"):
            UserContextManager.reset_context(user_context, ["awaiting_date"])
            return MESSAGES["UPDATE_DATE_PROMPT"]
        return MESSAGES["DATE_PROMPT"].format(
            specialty=user_context.get("temp_booking_specialty", "technician"))

    def _handle_negative_time_response(self, user_context: Dict) -> str:
        if user_context.get("updating_booking"):
            UserContextManager.reset_context(user_context, ["awaiting_time"])
            return MESSAGES["UPDATE_TIME_PROMPT"]
        return MESSAGES["TIME_PROMPT"].format(
            specialty=user_context.get("temp_booking_specialty", "technician"))

    def _format_time_prompt(self, user_context: Dict) -> str:
        specialty = user_context.get("temp_booking_specialty", "technician")
        if user_context.get("updating_booking"):
            return MESSAGES["UPDATE_TIME_PROMPT"]
        return MESSAGES["TIME_PROMPT"].format(specialty=specialty)

    def _setup_technician_selection(self, user_context: Dict,
                                    time_dt: datetime, specialty: str) -> str:
        if user_context.get("updating_booking"):
            booking_id = user_context.get("updating_booking_id")
            if booking_id:
                from app.nlp.handlers.update_handler import UpdateHandler
                return UpdateHandler().handle_update_booking_time(
                    time_dt, f"{time_dt.hour}:{time_dt.minute}", user_context)
        available_technicians = TechnicianManager.get_available_technicians(specialty)
        if not available_technicians:
            UserContextManager.cancel_booking_process(user_context)
            return MESSAGES["NO_TECHNICIANS"]
        UserContextManager.update_available_technicians(user_context, available_technicians)
        UserContextManager.set_awaiting_technician(user_context, True)
        self.update_context(user_context, "specialty", specialty)
        time_str = time_dt.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        response = TECHNICIAN_SELECTION_FORMAT.format(
            time_str=time_str, specialty=specialty.capitalize())
        for i, technician in enumerate(available_technicians, 1):
            response += TECHNICIAN_OPTION_LINE_FORMAT.format(
                index=i, technician=technician)
        response += TECHNICIAN_SELECTION_SUFFIX
        return response

    def _process_time_input(
            self, time_result: Tuple[Optional[datetime], Optional[str]], user_context: Dict) -> str:
        if isinstance(time_result, tuple):
            hour, minute = time_result
            booking_date = user_context.get("temp_booking_date")
            if booking_date:
                time_dt = datetime.combine(booking_date.date(), time(hour, minute))
            else:
                return MESSAGES["NO_DATE_SELECTED"]
        else:
            time_dt = time_result
        UserContextManager.update_time_context(user_context, time_dt)
        UserContextManager.set_awaiting_time(user_context, False)
        conflict = BookingConflictChecker.check_conflict(time_dt)
        specialty = user_context.get("temp_booking_specialty") or user_context.get(
            "specialty", DEFAULT_SPECIALTY)
        if conflict:
            UserContextManager.set_conflict_detected(user_context, time_dt)
            time_desc = time_dt.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
            alt_times = []
            one_hour_before = time_dt - timedelta(hours=1)
            if not BookingConflictChecker.check_conflict(one_hour_before):
                alt_times.append(one_hour_before.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"]))
            thirty_min_after = time_dt + timedelta(minutes=30)
            if not BookingConflictChecker.check_conflict(thirty_min_after):
                alt_times.append(thirty_min_after.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"]))
            one_hour_after = time_dt + timedelta(hours=1)
            if not BookingConflictChecker.check_conflict(one_hour_after):
                alt_times.append(one_hour_after.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"]))
            suggestion_message = ""
            if alt_times:
                suggestion_message = f" Alternative times available: {', '.join(alt_times)}. "
            return MESSAGES["CONFLICT_DETECTED"].format(
                time_description=time_desc) + suggestion_message + "Would you like to select a different time?"
        return self._setup_technician_selection(user_context, time_dt, specialty)

    def _handle_ampm_response(
            self, time_result: Tuple[Optional[datetime], Optional[str]], user_context: Dict) -> str:
        if not time_result or not time_result[0]:
            return MESSAGES["INVALID_AMPM_FORMAT"]
        time_dt, time_description = time_result
        conflict = BookingConflictChecker.check_conflict(time_dt)
        if conflict:
            return MESSAGES["CONFLICT_DETECTED"].format(
                time_description=time_description)
        specialty = user_context.get("specialty", DEFAULT_SPECIALTY)
        return self._setup_technician_selection(user_context, time_dt, specialty)
