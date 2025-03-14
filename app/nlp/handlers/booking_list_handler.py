from typing import Dict, List
from app.db.database import get_all_bookings
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.constants import MESSAGES, BOOKINGS_LIST_HEADER, BOOKING_DISPLAY_FORMAT, DATE_TIME_FORMATS
from app.nlp.handlers.base_handler import BaseHandler


class BookingListHandler(BaseHandler):
    @classmethod
    def handle_list_bookings_request(cls, user_context: Dict = None) -> str:
        return cls.static_method_wrapper(
            "handle_list_bookings_request_instance", user_context)

    def handle_list_bookings_request_instance(self, user_context: Dict = None) -> str:
        bookings = get_all_bookings()
        if not bookings:
            return MESSAGES["NO_BOOKINGS"]
        response = BOOKINGS_LIST_HEADER
        for booking in bookings:
            booking_time = booking.booking_time.strftime(
                DATE_TIME_FORMATS["DATETIME_WITH_DAY"])
            response += BOOKING_DISPLAY_FORMAT.format(
                id=booking.id,
                specialty=booking.specialty,
                technician_name=booking.technician_name,
                booking_time=booking_time
            ) + "\n"
        return response

    def reset_context(self, user_context: Dict, fields: List[str]) -> None:
        UserContextManager.reset_context(user_context, fields)

    def _create_default_context(self) -> Dict:
        return UserContextManager.create_default_context()
