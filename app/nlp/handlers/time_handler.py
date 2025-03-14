from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple, Union
import re
from app.nlp.handlers.base_handler import BaseHandler
from app.nlp.handlers.datetime_handler import DateTimeHandler
from app.nlp.handlers.technician_handler import TechnicianHandler
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.models.time_result import TimeResult


@dataclass
class BookingResponse:
    message: str
    success: bool = True
    booking_id: Optional[int] = None
    error_code: Optional[str] = None


class TimeHandler(BaseHandler):
    def handle_time_input(self, text: str, user_context: Dict) -> str:
        return DateTimeHandler().handle_time_input(text, user_context)

    def handle_technician_selection(self, text: str, user_context: Dict) -> str:
        return TechnicianHandler().handle_technician_input(text, user_context)

    def parse_time_from_text(self, text: str, user_context: Dict) -> TimeResult:
        booking_date = user_context.get('temp_booking_date')
        if not booking_date:
            return TimeResult(
                success=False,
                message="Please provide a date first."
            )
        time_parser = DateTimeParser()
        parsed_time, time_desc = time_parser.parse_time(text, booking_date)
        if parsed_time is None:
            single_digit_match = re.fullmatch(r'(\d{1,2})$', text.strip())
            if single_digit_match:
                hour = int(single_digit_match.group(1))
                if 5 <= hour <= 8:
                    pm_hour = hour + 12 if hour != 12 else hour
                    from datetime import datetime, time
                    booking_datetime = datetime.combine(
                        booking_date,
                        time(pm_hour, 0)
                    )
                    time_str = f"{hour}:00 PM"
                    return TimeResult(
                        success=True,
                        booking_time=booking_datetime,
                        time_description=time_str
                    )
            time_without_ampm = re.search(r'(\d{1,2})(?::(\d{2}))?', text.strip())
            if time_without_ampm:
                hour = int(time_without_ampm.group(1))
                minute = int(time_without_ampm.group(2) or 0)
                user_context["temp_booking_hour"] = hour
                user_context["temp_booking_minute"] = minute
                user_context["awaiting_ampm"] = True
                user_context["awaiting_time"] = False
                from app.nlp.constants import AMPM_PROMPT_FORMAT
                return TimeResult(
                    success=False,
                    message=AMPM_PROMPT_FORMAT.format(hour=hour, minute=minute),
                    error_code="AWAITING_AMPM"
                )
            from app.nlp.constants import MESSAGES
            return TimeResult(
                success=False,
                message=MESSAGES["INVALID_TIME_FORMAT"]
            )
        if isinstance(parsed_time, tuple):
            hour, minute = parsed_time
            from datetime import datetime, time
            booking_datetime = datetime.combine(
                booking_date,
                time(hour, minute)
            )
        else:
            booking_datetime = parsed_time
        return TimeResult(
            success=True,
            booking_time=booking_datetime,
            time_description=time_desc
        )
