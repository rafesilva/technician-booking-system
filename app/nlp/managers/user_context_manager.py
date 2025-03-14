from typing import Dict, List, Optional, Any
from datetime import datetime
from app.nlp.constants import DEFAULT_USER_CONTEXT


class UserContextManager:
    @staticmethod
    def create_default_context() -> Dict[str, Any]:
        return DEFAULT_USER_CONTEXT.copy()

    @staticmethod
    def reset_context(user_context: Dict, fields: Optional[List[str]] = None) -> None:
        if fields:
            for field in fields:
                if field in DEFAULT_USER_CONTEXT:
                    user_context[field] = DEFAULT_USER_CONTEXT[field]
        else:
            user_context.clear()
            user_context.update(DEFAULT_USER_CONTEXT.copy())

    @staticmethod
    def update_booking_context(user_context: Dict, *args) -> None:
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

    @staticmethod
    def update_date_context(user_context: Dict, booking_date: datetime) -> None:
        user_context["temp_booking_date"] = booking_date
        user_context["awaiting_date"] = False
        user_context["awaiting_time"] = True

    @staticmethod
    def set_conflict_detected(user_context: Dict, booking_date: datetime) -> None:
        user_context["conflict_detected"] = True
        user_context["temp_booking_date"] = booking_date

    @staticmethod
    def clear_conflict(user_context: Dict) -> None:
        user_context["conflict_detected"] = False

    @staticmethod
    def setup_for_technician_selection(user_context: Dict, booking_date: datetime,
                                       available_technicians: List[str]) -> None:
        user_context["temp_booking_date"] = booking_date
        user_context["conflict_detected"] = False
        user_context["awaiting_time"] = False
        user_context["awaiting_technician"] = True
        user_context["available_technicians"] = available_technicians

    @staticmethod
    def setup_for_booking_update(user_context: Dict, booking_id: int) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["awaiting_date"] = True

    @staticmethod
    def setup_for_booking_update_with_specialty(
            user_context: Dict, booking_id: int, specialty: str) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["specialty"] = specialty
        user_context["temp_booking_specialty"] = specialty
        user_context["awaiting_date"] = True
        user_context["awaiting_booking_id_for_update"] = False

    @staticmethod
    def cancel_booking_process(user_context: Dict) -> None:
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

    @staticmethod
    def update_time_context(user_context: Dict, booking_time: datetime) -> None:
        user_context["temp_booking_time"] = booking_time
        user_context["temp_booking_date"] = booking_time
        user_context["awaiting_time"] = False

    @staticmethod
    def prepare_booking_update(user_context: Dict, booking_id: int) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["awaiting_date"] = True

    @staticmethod
    def set_cancelling_booking(user_context: Dict, value: bool = True) -> None:
        user_context["cancelling_booking"] = value
        user_context["awaiting_booking_id_for_cancel"] = value

    @staticmethod
    def set_updating_booking(user_context: Dict, value: bool = True) -> None:
        user_context["updating_booking"] = value

    @staticmethod
    def set_specialty(user_context: Dict, specialty: str) -> None:
        user_context["specialty"] = specialty

    @staticmethod
    def set_temp_specialty(user_context: Dict, specialty: str) -> None:
        user_context["temp_booking_specialty"] = specialty

    @staticmethod
    def set_booking_in_progress(user_context: Dict, value: bool = True) -> None:
        user_context["booking_in_progress"] = value

    @staticmethod
    def set_awaiting_specialty(user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_specialty"] = value

    @staticmethod
    def set_awaiting_date(user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_date"] = value

    @staticmethod
    def set_awaiting_time(user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_time"] = value

    @staticmethod
    def set_awaiting_booking_id_for_update(
            user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_booking_id_for_update"] = value

    @staticmethod
    def set_awaiting_booking_id_for_cancel(
            user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_booking_id_for_cancel"] = value

    @staticmethod
    def set_last_booking_id(user_context: Dict, booking_id: int) -> None:
        user_context["last_booking_id"] = booking_id

    @staticmethod
    def set_last_technician(user_context: Dict, technician_name: str) -> None:
        user_context["last_technician"] = technician_name

    @staticmethod
    def set_is_test_booking(user_context: Dict, value: bool = True) -> None:
        user_context["is_test_booking"] = value

    @staticmethod
    def set_temp_booking_time(user_context: Dict, booking_time: datetime) -> None:
        user_context["temp_booking_time"] = booking_time

    @staticmethod
    def set_awaiting_technician(user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_technician"] = value

    @staticmethod
    def change_specialty_and_reset_to_date(user_context: Dict, specialty: str) -> None:
        user_context["temp_booking_specialty"] = specialty
        user_context["awaiting_time"] = False
        user_context["awaiting_date"] = True

    @staticmethod
    def set_temp_booking_hour(user_context: Dict, hour: int) -> None:
        user_context["temp_booking_hour"] = hour

    @staticmethod
    def set_temp_booking_minute(user_context: Dict, minute: int) -> None:
        user_context["temp_booking_minute"] = minute

    @staticmethod
    def set_awaiting_ampm(user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_ampm"] = value

    @staticmethod
    def setup_for_ampm_clarification(
            user_context: Dict, hour: int, minute: int) -> None:
        user_context["temp_booking_hour"] = hour
        user_context["temp_booking_minute"] = minute
        user_context["awaiting_ampm"] = True

    @staticmethod
    def set_temp_booking_date(user_context: Dict, booking_date: datetime) -> None:
        user_context["temp_booking_date"] = booking_date

    @staticmethod
    def reset_booking_context(user_context: Dict) -> None:
        booking_fields = [
            "booking_in_progress", "awaiting_date", "awaiting_time",
            "awaiting_technician", "available_technicians", "conflict_detected",
            "temp_booking_date", "temp_booking_specialty", "awaiting_ampm",
            "temp_booking_hour", "temp_booking_minute", "is_test_booking",
            "specialty", "temp_booking_specialty"
        ]
        for field in booking_fields:
            user_context[field] = DEFAULT_USER_CONTEXT.get(field)
        user_context["specialty"] = None
        user_context["temp_booking_specialty"] = None
        user_context["available_technicians"] = None
        user_context["temp_booking_date"] = None
        user_context["temp_booking_hour"] = None
        user_context["temp_booking_minute"] = None

    @staticmethod
    def update_available_technicians(user_context: Dict, available_technicians: List[str]) -> None:
        user_context["available_technicians"] = available_technicians


__all__ = ['UserContextManager']
