from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.constants import MESSAGES


class BaseHandler:
    @staticmethod
    def format_datetime(dt: datetime, include_day: bool = True) -> str:
        from app.nlp.constants import DATE_TIME_FORMATS
        if include_day:
            return dt.strftime(DATE_TIME_FORMATS["DATETIME_WITH_DAY"])
        return dt.strftime(DATE_TIME_FORMATS["DATETIME_WITHOUT_DAY"])

    @staticmethod
    def get_hour_range(booking_date: datetime) -> Tuple[datetime, datetime]:
        start_time = booking_date.replace(minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        return start_time, end_time

    @staticmethod
    def reset_context(user_context: Dict, fields: List[str]) -> None:
        UserContextManager.reset_context(user_context, fields)

    @staticmethod
    def handle_cancellation(user_context: Dict) -> str:
        UserContextManager.cancel_booking_process(user_context)
        return MESSAGES["BOOKING_PROCESS_CANCELLED"]

    @classmethod
    def static_method_wrapper(cls, method_name: str, *args, **kwargs):
        instance = cls()
        method = getattr(instance, method_name)
        return method(*args, **kwargs)
