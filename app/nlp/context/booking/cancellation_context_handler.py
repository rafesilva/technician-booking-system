from typing import Dict


class CancellationContextHandler:
    def set_cancelling_booking(self, user_context: Dict, value: bool = True) -> None:
        user_context["cancelling_booking"] = value
        user_context["awaiting_booking_id_for_cancel"] = value

    def set_awaiting_booking_id_for_cancel(
            self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_booking_id_for_cancel"] = value

    def set_last_booking_id(self, user_context: Dict, booking_id: int) -> None:
        user_context["last_booking_id"] = booking_id
