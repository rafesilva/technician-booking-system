from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import random
import re
from app.nlp.constants import (
    TECHNICIANS,
    TECHNICIAN_OPTION_LINE_FORMAT,
    TECHNICIAN_SELECTION_FORMAT,
    TECHNICIAN_SELECTION_SUFFIX,
    MESSAGES,
    DEFAULT_SPECIALTY,
    DEFAULT_PLUMBER_SPECIALTY
)
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.handlers.conflict_checker import BookingConflictChecker
from app.nlp.managers.technician_manager import TechnicianManager


class TechnicianService:
    @staticmethod
    def setup_technician_selection(user_context: Dict, time_dt: datetime, specialty: str) -> str:
        if specialty and specialty.lower() != DEFAULT_SPECIALTY.lower():
            available_technicians = TechnicianManager.get_available_technicians(specialty)
        else:
            specialty = DEFAULT_SPECIALTY
            available_technicians = TechnicianManager.get_available_technicians(
                DEFAULT_PLUMBER_SPECIALTY)
        if not available_technicians:
            return MESSAGES["NO_TECHNICIANS"]
        UserContextManager.setup_for_technician_selection(
            user_context,
            time_dt,
            available_technicians
        )
        time_str = time_dt.strftime("%-I:%M %p")
        response = TECHNICIAN_SELECTION_FORMAT.format(
            time_str=time_str, specialty=specialty.capitalize())
        for i, technician in enumerate(available_technicians, 1):
            response += f"{i}. {technician}\n"
        response += TECHNICIAN_SELECTION_SUFFIX
        return response

    @staticmethod
    def check_and_handle_conflict(user_context: Dict,
                                  booking_date: datetime,
                                  time_description: str,
                                  exclude_booking_id: Optional[int] = None) -> Optional[str]:
        conflict = BookingConflictChecker.check_conflict(
            booking_date, exclude_booking_id=exclude_booking_id)
        if conflict:
            UserContextManager.set_conflict_detected(user_context, booking_date)
            return MESSAGES["CONFLICT_DETECTED"].format(time_description=time_description)
        return None
