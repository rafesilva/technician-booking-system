from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.handlers.booking_handler import BookingHandler
from app.nlp.utils.date_time_parser import DateTimeParser
import unittest
from datetime import datetime


class TestCombinedDateTimeProcessing(unittest.TestCase):
    def setUp(self):
        self.parser = DateTimeParser()
        self.handler = BookingHandler()

    def test_combined_month_day_hour_parsing(self):
        text = "April 15 6"
        result, description = self.parser.parse_date_time(text)
        self.assertIsNotNone(result)
        self.assertEqual(result.month, 4)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 18)
        self.assertEqual(result.minute, 0)

    def test_combined_text_with_am_specified(self):
        text = "April 15 6 AM"
        result, description = self.parser.parse_date_time(text)
        self.assertIsNotNone(result)
        self.assertEqual(result.month, 4)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 6)
        self.assertEqual(result.minute, 0)

    def test_single_digit_evening_time_defaults_to_pm(self):
        today = datetime.now().date()
        for hour in range(5, 9):
            text = str(hour)
            result, description = self.parser.parse_time(text)
            self.assertIsNotNone(result)
            self.assertEqual(result[0], hour + 12)
            self.assertEqual(result[1], 0)

    def test_single_digit_other_times_require_clarification(self):
        for hour in [1, 2, 3, 4, 9, 10, 11, 12]:
            text = str(hour)
            result, description = self.parser.parse_time(text)
            self.assertIsNone(result)

    def test_full_booking_request_parsing(self):
        text = "Book a plumber April 15 6"
        user_context = UserContextManager.create_default_context()
        response = self.handler.handle_booking_request(text, user_context)
        self.assertIsNotNone(user_context.get("temp_booking_date"))
        self.assertIsNotNone(user_context.get("temp_booking_time"))
        booking_date = user_context.get("temp_booking_date")
        booking_time = user_context.get("temp_booking_time")
        self.assertEqual(booking_date.month, 4)
        self.assertEqual(booking_date.day, 15)
        self.assertEqual(booking_time.hour, 18)
        self.assertNotIn("What date", response)
        self.assertNotIn("What time", response)


if __name__ == "__main__":
    unittest.main()
