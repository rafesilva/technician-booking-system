from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.db.database import get_booking_by_id
import re
import pytest
from datetime import datetime, timedelta


class TestCombinedBookingFlow:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.processor = NaturalLanguageProcessor()
        self.user_context = {}

    def process_and_log(self, text):
        response = self.processor.process_input(text, self.user_context)
        return response

    def test_complete_booking_with_single_request(self):
        response = self.process_and_log("I need a plumber April 15 6")
        assert "What date" not in response, "System should not ask for date"
        assert "What time" not in response, "System should not ask for time"
        assert "available technicians" in response or "select a technician" in response.lower(
        ), "System should prompt for technician selection"
        response = self.process_and_log("1")
        assert "confirmed" in response.lower() or "scheduled" in response.lower(), "Booking should be confirmed"
        assert "booking id" in response.lower() or "booking ID" in response.lower(), "Response should include booking ID"
        booking_id_match = re.search(
            r'(?:booking|appointment)\s+(?:id|ID)(?:\s+is)?\s+(\d+)',
            response,
            re.IGNORECASE)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found in database"
        assert booking.specialty.lower(
        ) == "plumber", f"Expected specialty 'plumber', got '{booking.specialty}'"
        assert booking.booking_time.month == 4, "Expected booking month to be April (4)"
        assert booking.booking_time.day == 15, "Expected booking day to be 15"
        assert booking.booking_time.hour == 18, "Expected booking hour to be 18 (6 PM)"

    def test_evening_time_defaults_to_pm(self):
        response = self.process_and_log("Book a plumber")
        assert "date" in response.lower() or "when" in response.lower(), "System should ask for date"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
        response = self.process_and_log(tomorrow)
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("6")
        assert "am or pm" not in response.lower(), "System should not ask for AM/PM clarification"
        assert "technician" in response.lower() or "available" in response.lower(
        ), "System should prompt for technician selection"

    def test_other_times_still_need_clarification(self):
        response = self.process_and_log("Book an electrician")
        assert "date" in response.lower() or "when" in response.lower(), "System should ask for date"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
        response = self.process_and_log(tomorrow)
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("10")
        assert "am or pm" in response.lower() or "morning or afternoon" in response.lower(
        ), "System should ask for AM/PM clarification"
