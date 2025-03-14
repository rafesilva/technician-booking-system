from typing import Dict
from datetime import datetime


class ConflictContextHandler:
    def set_conflict_detected(self, user_context: Dict, booking_date: datetime) -> None:
        user_context["conflict_detected"] = True
        user_context["temp_booking_date"] = booking_date

    def clear_conflict(self, user_context: Dict) -> None:
        user_context["conflict_detected"] = False
