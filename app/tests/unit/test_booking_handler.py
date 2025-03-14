from datetime import datetime
from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.handlers.booking_handler import BookingHandler
from app.nlp.handlers.technician_handler import TechnicianHandler
from app.nlp.managers.user_context_manager import UserContextManager
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestBookingHandler(unittest.TestCase):
    def setUp(self):
        self.handler = BookingHandler()
        self.date_time_parser = DateTimeParser()

    def test_extract_specialty(self):
        text = "I need a plumber"
        specialty = BookingDataExtractor.extract_specialty(text)
        self.assertEqual(specialty, "Plumber")

    def test_parse_date_time(self):
        text = "tomorrow at 3 PM"
        booking_date, time_description = self.date_time_parser.parse_date_time(text)
        self.assertIsNotNone(booking_date)
        self.assertEqual(booking_date.hour, 15)
        self.assertEqual(booking_date.minute, 0)

    def test_handle_booking_request(self):
        text = "I need a plumber"
        user_context = {}
        result = self.handler.handle_booking_request(text, user_context)
        self.assertTrue(
            "What date would you like to book" in result or "What date would you like to book" in result)

    def test_booking_request_during_technician_selection(self):
        user_context = UserContextManager.create_default_context()
        user_context["awaiting_technician"] = True
        user_context["available_technicians"] = ["Nicolas Woollett", "John Pipe", "Sarah Waters"]
        user_context["temp_booking_date"] = datetime.now().replace(
            hour=15, minute=0, second=0, microsecond=0)
        user_context["temp_booking_specialty"] = "Plumber"
        handler = TechnicianHandler()
        response = handler.handle_technician_input("Book a technician", user_context)
        self.assertIn("technician", response)
        self.assertFalse(user_context["awaiting_technician"])
        self.assertTrue(user_context["awaiting_specialty"])
        user_context = UserContextManager.create_default_context()
        user_context["awaiting_technician"] = True
        user_context["available_technicians"] = ["Nicolas Woollett", "John Pipe", "Sarah Waters"]
        user_context["temp_booking_date"] = datetime.now().replace(
            hour=15, minute=0, second=0, microsecond=0)
        response = handler.handle_technician_input("Book a plumber", user_context)
        self.assertIn("date", response)
        self.assertFalse(user_context["awaiting_technician"])
        self.assertEqual(user_context["temp_booking_specialty"], "Plumber")


if __name__ == "__main__":
    unittest.main()
