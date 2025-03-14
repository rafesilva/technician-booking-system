from typing import Dict, List
from datetime import datetime


class TechnicianContextHandler:
    def setup_for_technician_selection(self, user_context: Dict, booking_date: datetime,
                                       available_technicians: List[str]) -> None:
        user_context["temp_booking_date"] = booking_date
        user_context["conflict_detected"] = False
        user_context["awaiting_time"] = False
        user_context["awaiting_technician"] = True
        user_context["available_technicians"] = available_technicians

    def set_awaiting_technician(self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_technician"] = value

    def set_last_technician(self, user_context: Dict, technician_name: str) -> None:
        user_context["last_technician"] = technician_name

    def set_specialty(self, user_context: Dict, specialty: str) -> None:
        user_context["specialty"] = specialty

    def set_temp_specialty(self, user_context: Dict, specialty: str) -> None:
        user_context["temp_booking_specialty"] = specialty

    def set_awaiting_specialty(self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_specialty"] = value

    def change_specialty_and_reset_to_date(self, user_context: Dict, specialty: str) -> None:
        user_context["temp_booking_specialty"] = specialty
        user_context["awaiting_time"] = False
        user_context["awaiting_date"] = True
