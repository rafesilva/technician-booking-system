from typing import Dict
from app.nlp.handlers.base_handler import BaseHandler
from app.nlp.handlers.datetime_handler import DateTimeHandler


class DateHandler(BaseHandler):
    def handle_date_input(self, text: str, user_context: Dict) -> str:
        return DateTimeHandler().handle_date_input(text, user_context)
