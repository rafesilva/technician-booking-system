from typing import Dict, List, Optional, Any
from datetime import datetime


class BookingContextHandler:
    def update_booking_context(self, user_context: Dict, *args) -> None:
        if len(args) == 1:
            specialty = args[0]
            user_context["temp_booking_specialty"] = specialty
            user_context["awaiting_date"] = True
        elif len(args) == 4:
            booking_id, booking_date, specialty, technician_name = args
            user_context["last_booking_id"] = booking_id
            user_context["last_booking_time"] = booking_date
            user_context["last_booking_specialty"] = specialty
            user_context["last_booking_technician"] = technician_name

    def update_date_context(self, user_context: Dict, booking_date: datetime) -> None:
        user_context["temp_booking_date"] = booking_date
        user_context["awaiting_date"] = False
        user_context["awaiting_time"] = True

    def update_time_context(self, user_context: Dict, booking_time: datetime) -> None:
        user_context["temp_booking_time"] = booking_time
        user_context["temp_booking_date"] = booking_time
        user_context["awaiting_time"] = False

    def setup_for_ampm_clarification(self, user_context: Dict, hour: int, minute: int) -> None:
        user_context["temp_booking_hour"] = hour
        user_context["temp_booking_minute"] = minute
        user_context["awaiting_ampm"] = True

    def cancel_booking_process(self, user_context: Dict) -> None:
        user_context["booking_in_progress"] = False
        user_context["awaiting_date"] = False
        user_context["awaiting_time"] = False
        user_context["awaiting_technician"] = False
        user_context["awaiting_ampm"] = False
        user_context["conflict_detected"] = False
        user_context["available_technicians"] = None
        user_context["temp_booking_hour"] = None
        user_context["temp_booking_minute"] = None
        user_context["is_test_booking"] = False

    def set_temp_booking_date(self, user_context: Dict, booking_date: datetime) -> None:
        user_context["temp_booking_date"] = booking_date

    def set_temp_booking_time(self, user_context: Dict, booking_time: datetime) -> None:
        user_context["temp_booking_time"] = booking_time

    def set_temp_booking_hour(self, user_context: Dict, hour: int) -> None:
        user_context["temp_booking_hour"] = hour

    def set_temp_booking_minute(self, user_context: Dict, minute: int) -> None:
        user_context["temp_booking_minute"] = minute

    def set_booking_in_progress(self, user_context: Dict, value: bool = True) -> None:
        user_context["booking_in_progress"] = value

    def set_awaiting_date(self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_date"] = value

    def set_awaiting_time(self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_time"] = value

    def set_awaiting_ampm(self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_ampm"] = value

    def set_is_test_booking(self, user_context: Dict, value: bool = True) -> None:
        user_context["is_test_booking"] = value
