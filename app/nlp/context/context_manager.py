from typing import Dict, List, Optional, Any
from datetime import datetime
from app.nlp.context.base.base_context_handler import BaseContextHandler
from app.nlp.context.booking.booking_context_handler import BookingContextHandler
from app.nlp.context.booking.technician_context_handler import TechnicianContextHandler
from app.nlp.context.booking.conflict_context_handler import ConflictContextHandler
from app.nlp.context.booking.update_context_handler import UpdateContextHandler
from app.nlp.context.booking.cancellation_context_handler import CancellationContextHandler


class ContextManager:
    def __init__(self):
        self.base_handler = BaseContextHandler()
        self.booking_handler = BookingContextHandler()
        self.technician_handler = TechnicianContextHandler()
        self.conflict_handler = ConflictContextHandler()
        self.update_handler = UpdateContextHandler()
        self.cancellation_handler = CancellationContextHandler()

    def create_default_context(self) -> Dict[str, Any]:
        return self.base_handler.create_default_context()

    def reset_context(self, user_context: Dict, fields: Optional[List[str]] = None) -> None:
        self.base_handler.reset_context(user_context, fields)

    def update_booking_context(self, user_context: Dict, *args) -> None:
        self.booking_handler.update_booking_context(user_context, *args)

    def update_date_context(self, user_context: Dict, booking_date: datetime) -> None:
        self.booking_handler.update_date_context(user_context, booking_date)

    def update_time_context(self, user_context: Dict, booking_time: datetime) -> None:
        self.booking_handler.update_time_context(user_context, booking_time)

    def cancel_booking_process(self, user_context: Dict) -> None:
        self.booking_handler.cancel_booking_process(user_context)

    def set_booking_in_progress(self, user_context: Dict, value: bool = True) -> None:
        self.booking_handler.set_booking_in_progress(user_context, value)

    def set_awaiting_date(self, user_context: Dict, value: bool = True) -> None:
        self.booking_handler.set_awaiting_date(user_context, value)

    def set_awaiting_time(self, user_context: Dict, value: bool = True) -> None:
        self.booking_handler.set_awaiting_time(user_context, value)

    def set_temp_booking_date(self, user_context: Dict, booking_date: datetime) -> None:
        self.booking_handler.set_temp_booking_date(user_context, booking_date)

    def set_temp_booking_time(self, user_context: Dict, booking_time: datetime) -> None:
        self.booking_handler.set_temp_booking_time(user_context, booking_time)

    def set_temp_booking_hour(self, user_context: Dict, hour: int) -> None:
        self.booking_handler.set_temp_booking_hour(user_context, hour)

    def set_temp_booking_minute(self, user_context: Dict, minute: int) -> None:
        self.booking_handler.set_temp_booking_minute(user_context, minute)

    def set_awaiting_ampm(self, user_context: Dict, value: bool = True) -> None:
        self.booking_handler.set_awaiting_ampm(user_context, value)

    def setup_for_ampm_clarification(self, user_context: Dict, hour: int, minute: int) -> None:
        self.booking_handler.setup_for_ampm_clarification(user_context, hour, minute)

    def set_is_test_booking(self, user_context: Dict, value: bool = True) -> None:
        self.booking_handler.set_is_test_booking(user_context, value)

    def setup_for_technician_selection(self, user_context: Dict, booking_date: datetime,
                                       available_technicians: List[str]) -> None:
        self.technician_handler.setup_for_technician_selection(
            user_context, booking_date, available_technicians)

    def set_awaiting_technician(self, user_context: Dict, value: bool = True) -> None:
        self.technician_handler.set_awaiting_technician(user_context, value)

    def set_last_technician(self, user_context: Dict, technician_name: str) -> None:
        self.technician_handler.set_last_technician(user_context, technician_name)

    def set_specialty(self, user_context: Dict, specialty: str) -> None:
        self.technician_handler.set_specialty(user_context, specialty)

    def set_temp_specialty(self, user_context: Dict, specialty: str) -> None:
        self.technician_handler.set_temp_specialty(user_context, specialty)

    def set_awaiting_specialty(self, user_context: Dict, value: bool = True) -> None:
        self.technician_handler.set_awaiting_specialty(user_context, value)

    def change_specialty_and_reset_to_date(self, user_context: Dict, specialty: str) -> None:
        self.technician_handler.change_specialty_and_reset_to_date(user_context, specialty)

    def set_conflict_detected(self, user_context: Dict, booking_date: datetime) -> None:
        self.conflict_handler.set_conflict_detected(user_context, booking_date)

    def clear_conflict(self, user_context: Dict) -> None:
        self.conflict_handler.clear_conflict(user_context)

    def setup_for_booking_update(self, user_context: Dict, booking_id: int) -> None:
        self.update_handler.setup_for_booking_update(user_context, booking_id)

    def setup_for_booking_update_with_specialty(
            self, user_context: Dict, booking_id: int, specialty: str) -> None:
        self.update_handler.setup_for_booking_update_with_specialty(
            user_context, booking_id, specialty)

    def prepare_booking_update(self, user_context: Dict, booking_id: int) -> None:
        self.update_handler.prepare_booking_update(user_context, booking_id)

    def set_updating_booking(self, user_context: Dict, value: bool = True) -> None:
        self.update_handler.set_updating_booking(user_context, value)

    def set_awaiting_booking_id_for_update(
            self, user_context: Dict, value: bool = True) -> None:
        self.update_handler.set_awaiting_booking_id_for_update(user_context, value)

    def set_cancelling_booking(self, user_context: Dict, value: bool = True) -> None:
        self.cancellation_handler.set_cancelling_booking(user_context, value)

    def set_awaiting_booking_id_for_cancel(
            self, user_context: Dict, value: bool = True) -> None:
        self.cancellation_handler.set_awaiting_booking_id_for_cancel(user_context, value)

    def set_last_booking_id(self, user_context: Dict, booking_id: int) -> None:
        self.cancellation_handler.set_last_booking_id(user_context, booking_id)
