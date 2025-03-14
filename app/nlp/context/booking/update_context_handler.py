from typing import Dict


class UpdateContextHandler:
    def setup_for_booking_update(self, user_context: Dict, booking_id: int) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["awaiting_date"] = True

    def setup_for_booking_update_with_specialty(
            self, user_context: Dict, booking_id: int, specialty: str) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["specialty"] = specialty
        user_context["temp_booking_specialty"] = specialty
        user_context["awaiting_date"] = True
        user_context["awaiting_booking_id_for_update"] = False

    def prepare_booking_update(self, user_context: Dict, booking_id: int) -> None:
        user_context["updating_booking"] = True
        user_context["updating_booking_id"] = booking_id
        user_context["awaiting_date"] = True

    def set_updating_booking(self, user_context: Dict, value: bool = True) -> None:
        user_context["updating_booking"] = value

    def set_awaiting_booking_id_for_update(
            self, user_context: Dict, value: bool = True) -> None:
        user_context["awaiting_booking_id_for_update"] = value
