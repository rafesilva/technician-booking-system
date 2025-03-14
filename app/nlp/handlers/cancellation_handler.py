from app.db.database import get_booking_by_id, delete_booking
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.constants import MESSAGES
from app.nlp.handlers.base_handler import BaseHandler
from typing import Dict


class CancellationHandler(BaseHandler):
    def handle_cancellation_request(self, text: str, user_context: Dict) -> str:
        booking_id = BookingDataExtractor.extract_booking_id(text)
        if booking_id is None:
            UserContextManager.set_awaiting_booking_id_for_cancel(user_context)
            return MESSAGES["PROVIDE_BOOKING_ID_CANCEL"]
        booking = get_booking_by_id(booking_id)
        if booking is None:
            return MESSAGES["NO_BOOKING_FOUND"].format(booking_id=booking_id)
        delete_booking(booking_id)
        return self._format_cancellation_confirmation(booking)

    @classmethod
    def handle_cancellation_request_static(cls, text: str, user_context: Dict) -> str:
        return cls.static_method_wrapper(
            "handle_cancellation_request", text, user_context)

    def _format_cancellation_confirmation(self, booking: object) -> str:
        booking_time = self.format_datetime(booking.booking_time)
        return MESSAGES["CANCELLATION_CONFIRMATION"].format(
            technician_name=booking.technician_name,
            booking_time=booking_time
        )
