from datetime import datetime
from typing import Dict, Optional, Tuple
from app.db.database import create_booking, get_booking_by_id, delete_booking, update_booking
from app.models.booking import BookingCreate
from app.nlp.constants import (
    MESSAGES,
    DATE_TIME_FORMATS
)
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.managers import TechnicianManager
from app.nlp.utils.booking_data_extractor import BookingDataExtractor


class BookingService:
    @staticmethod
    def create_booking(user_context: Dict, specialty: str, booking_date: datetime) -> str:
        is_test = user_context.get("is_test_booking", False)
        if is_test:
            UserContextManager.set_is_test_booking(user_context)
        technician_name = TechnicianManager.assign_technician(specialty)
        booking_create = BookingCreate(
            technician_name=technician_name,
            specialty=specialty,
            booking_time=booking_date
        )
        booking_id = create_booking(booking_create)
        UserContextManager.update_booking_context(
            user_context,
            booking_id,
            booking_date,
            specialty,
            technician_name
        )
        day_of_week = booking_date.strftime("%A")
        date_str = booking_date.strftime("%B %d")
        time_str = booking_date.strftime("%I:%M %p")
        return MESSAGES["BOOKING_CONFIRMATION"].format(
            technician_name=technician_name,
            specialty=specialty,
            day_of_week=day_of_week,
            date_str=date_str,
            time_str=time_str,
            booking_id=booking_id
        )

    @staticmethod
    def update_booking(booking_id: int, new_datetime: datetime) -> Tuple[bool, str]:
        booking = get_booking_by_id(booking_id)
        if not booking:
            return False, f"No booking found with ID {booking_id}"
        old_time = booking.booking_time.strftime(DATE_TIME_FORMATS["TIME_ONLY_DISPLAY"])
        old_date = booking.booking_time.strftime(DATE_TIME_FORMATS["DATE_ONLY_DISPLAY"])
        update_booking(booking_id, {"booking_time": new_datetime})
        new_time = new_datetime.strftime(DATE_TIME_FORMATS["TIME_ONLY_DISPLAY"])
        new_date_str = new_datetime.strftime(DATE_TIME_FORMATS["DATE_ONLY_DISPLAY"])
        message = MESSAGES["BOOKING_UPDATED"].format(
            technician_name=booking.technician_name,
            old_date=old_date,
            old_time=old_time,
            new_date_str=new_date_str,
            new_time=new_time
        )
        return True, message

    @staticmethod
    def cancel_booking(booking_id: int) -> Tuple[bool, str]:
        booking = get_booking_by_id(booking_id)
        if not booking:
            return False, f"No booking found with ID {booking_id}"
        delete_booking(booking_id)
        booking_time = booking.booking_time.strftime(DATE_TIME_FORMATS["BOOKING_TIME_DISPLAY"])
        message = MESSAGES["BOOKING_CANCELLED"].format(
            technician_name=booking.technician_name,
            booking_time=booking_time
        )
        return True, message

    @staticmethod
    def extract_booking_id_from_text(text: str) -> Optional[int]:
        try:
            booking_id = int(text.strip())
            return booking_id
        except ValueError:
            return BookingDataExtractor.extract_booking_id(text)
