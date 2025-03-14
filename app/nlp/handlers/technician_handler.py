from typing import Dict, List, Optional, Any
import re
import random
from datetime import datetime
from app.db.database import (
    create_booking,
    get_booking_by_id,
    get_all_bookings,
    update_booking
)
from app.models.booking import BookingCreate
from app.nlp.constants import (
    MESSAGES,
    TECHNICIANS,
    DEFAULT_SPECIALTY,
    CANCEL_TERMS,
    TECHNICIAN_TYPES,
    PROCESSOR_MESSAGES,
    TECHNICIAN_SELECTION_FORMAT,
    TECHNICIAN_OPTION_LINE_FORMAT,
    TECHNICIAN_SELECTION_SUFFIX,
    DATE_TIME_FORMATS
)
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.utils.intent_recognizer import IntentRecognizer
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.handlers.base_handler import BaseHandler
from app.nlp.managers.technician_manager import TechnicianManager


class TechnicianHandler(BaseHandler):
    def handle_technician_input(self, text: str, user_context: Dict) -> str:
        if any(term in text.lower() for term in CANCEL_TERMS):
            return self.handle_cancellation(user_context)
        if IntentRecognizer.is_booking_request(text):
            UserContextManager.cancel_booking_process(user_context)
            specialty = BookingDataExtractor.extract_specialty(text)
            if specialty:
                UserContextManager.set_temp_specialty(user_context, specialty)
                UserContextManager.set_awaiting_date(user_context)
                return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
            elif "technician" in text.lower() and not any(specific in text.lower() for specific in TECHNICIAN_TYPES):
                UserContextManager.set_awaiting_specialty(user_context)
                return PROCESSOR_MESSAGES["GENERIC_TECHNICIAN_PROMPT"]
            else:
                UserContextManager.set_awaiting_specialty(user_context)
                return PROCESSOR_MESSAGES["GENERIC_TECHNICIAN_PROMPT"]
        available_technicians = user_context.get("available_technicians", [])
        if not available_technicians:
            return MESSAGES["NO_TECHNICIANS"]
        is_updating = user_context.get("updating_booking", False)
        booking_id = user_context.get("updating_booking_id") if is_updating else None
        text_lower = text.lower()
        if text_lower.isdigit():
            index = int(text_lower) - 1
            if 0 <= index < len(available_technicians):
                return self._process_technician_selection(
                    available_technicians[index], user_context, is_updating, booking_id)
            else:
                return MESSAGES["TECHNICIAN_SELECTION_INVALID"].format(
                    num_technicians=len(available_technicians))
        ordinal_map = {
            "first": 0, "1st": 0,
            "second": 1, "2nd": 1,
            "third": 2, "3rd": 2,
            "fourth": 3, "4th": 3,
            "fifth": 4, "5th": 4
        }
        for ordinal, index in ordinal_map.items():
            if ordinal in text_lower and 0 <= index < len(available_technicians):
                return self._process_technician_selection(
                    available_technicians[index], user_context, is_updating, booking_id)
        return self._handle_technician_selection_by_name(
            text, available_technicians, user_context, is_updating, booking_id)

    @classmethod
    def handle_technician_input_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper("handle_technician_input", text, user_context)

    def _format_technician_options(self, user_context: Dict) -> str:
        available_technicians = user_context.get("available_technicians", [])
        if not available_technicians:
            return MESSAGES["NO_TECHNICIANS"]
        booking_date = user_context.get("temp_booking_date")
        if not booking_date:
            return MESSAGES["NO_DATE_SELECTED"]
        specialty = user_context.get("specialty", DEFAULT_SPECIALTY)
        time_str = booking_date.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        response = TECHNICIAN_SELECTION_FORMAT.format(
            time_str=time_str, specialty=specialty.capitalize())
        for i, technician in enumerate(available_technicians, 1):
            response += TECHNICIAN_OPTION_LINE_FORMAT.format(
                index=i, technician=technician)
        response += TECHNICIAN_SELECTION_SUFFIX
        return response

    def _handle_technician_selection_by_name(self, text: str, available_technicians: List[str],
                                             user_context: Dict, is_updating: bool,
                                             booking_id: Optional[int]) -> str:
        text_lower = text.lower().strip()
        for technician in available_technicians:
            if technician.lower() == text_lower:
                return self._process_technician_selection(
                    technician, user_context, is_updating, booking_id)
        for technician in available_technicians:
            tech_lower = technician.lower()
            if tech_lower in text_lower or text_lower in tech_lower:
                return self._process_technician_selection(
                    technician, user_context, is_updating, booking_id)
            name_parts = tech_lower.split()
            for part in name_parts:
                if part in text_lower or text_lower in part:
                    return self._process_technician_selection(
                        technician, user_context, is_updating, booking_id)
        return MESSAGES["TECHNICIAN_NOT_FOUND"].format(
            text=text,
            num_technicians=len(available_technicians)
        )

    def _process_technician_selection(self, technician_name: str, user_context: Dict,
                                      is_updating: bool, booking_id: Optional[int]) -> str:
        if is_updating and booking_id:
            return self._update_booking_with_technician(
                booking_id, technician_name, user_context.get("temp_booking_date"), user_context)
        booking_date = user_context.get("temp_booking_date")
        if not booking_date:
            return MESSAGES["NO_DATE_SELECTED"]
        specialty = user_context.get("temp_booking_specialty", DEFAULT_SPECIALTY)
        booking_create = BookingCreate(
            technician_name=technician_name,
            specialty=specialty,
            booking_time=booking_date
        )
        try:
            booking_id = create_booking(booking_create)
            UserContextManager.update_booking_context(
                user_context,
                booking_id,
                booking_date,
                specialty,
                technician_name
            )
            day_of_week = booking_date.strftime(DATE_TIME_FORMATS["DAY_OF_WEEK_FORMAT"])
            date_str = booking_date.strftime(DATE_TIME_FORMATS["DATE_ONLY_FORMAT"])
            time_str = booking_date.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
            UserContextManager.reset_context(user_context)
            return MESSAGES["BOOKING_CONFIRMATION"].format(
                technician_name=technician_name,
                specialty=specialty,
                day_of_week=day_of_week,
                date_str=date_str,
                time_str=time_str,
                booking_id=booking_id
            )
        except ValueError as e:
            return str(e)

    def _update_booking_with_technician(self, booking_id: int, technician_name: str,
                                        booking_date: datetime, user_context: Dict) -> str:
        booking = get_booking_by_id(booking_id)
        if not booking:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        old_date = booking.booking_time.strftime(DATE_TIME_FORMATS["DATE_ONLY_FORMAT"])
        old_time = booking.booking_time.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        old_datetime = f"{old_date} at {old_time}"
        update_booking(booking_id, {"technician_name": technician_name})
        UserContextManager.update_booking_context(
            user_context,
            booking_id,
            booking.booking_time,
            booking.specialty,
            technician_name
        )
        UserContextManager.reset_context(
            user_context, [
                "updating_booking", "updating_booking_id"])
        new_date = booking_date.strftime(DATE_TIME_FORMATS["DATE_ONLY_FORMAT"])
        new_time = booking_date.strftime(DATE_TIME_FORMATS["TIME_ONLY_FORMAT"])
        new_datetime = f"{new_date} at {new_time}"
        return MESSAGES["UPDATE_CONFIRMATION"].format(
            old_time=old_datetime,
            new_time=new_datetime,
            technician_name=technician_name,
            specialty=booking.specialty
        )
