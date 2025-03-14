from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.db.database import get_booking_by_id
import re
import pytest
from datetime import datetime, timedelta


class TestSimpleBookingFlow:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.processor = NaturalLanguageProcessor()
        self.user_context = {}

    def process_and_print(self, text):
        response = self.processor.process_input(text, self.user_context)
        print(f"\nInput: {text}")
        print(f"Response: {response}")
        print(f"Context: awaiting_specialty={self.user_context.get('awaiting_specialty', False)}, " +
              f"awaiting_date={self.user_context.get('awaiting_date', False)}, " +
              f"awaiting_time={self.user_context.get('awaiting_time', False)}, " +
              f"awaiting_technician={self.user_context.get('awaiting_technician', False)}, " +
              f"awaiting_ampm={self.user_context.get('awaiting_ampm', False)}")
        if 'temp_booking_date' in self.user_context:
            print(f"Booking date: {self.user_context.get('temp_booking_date')}")
        if 'temp_booking_time' in self.user_context:
            print(f"Booking time: {self.user_context.get('temp_booking_time')}")
        return response

    def test_simple_combined_booking(self):
        response = self.process_and_print("Book a plumber April 15 3 PM")
        if "conflict" in response.lower() or "different time" in response.lower():
            response = self.process_and_print("4 PM")
            if "conflict" in response.lower() or "different time" in response.lower():
                response = self.process_and_print("7 PM")
        assert "available" in response.lower(), "Should show available technicians"
        response = self.process_and_print("1")
        assert "booking" in response.lower() and "confirmed" in response.lower(), "Should confirm booking"
        booking_id_match = re.search(
            r'(?:booking|appointment)\s+(?:id|ID)(?:\s+is)?\s+(\d+)',
            response,
            re.IGNORECASE)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found"
        assert booking.specialty.lower(
        ) == "plumber", f"Expected 'plumber', got '{booking.specialty}'"
        assert booking.booking_time.month == 4, f"Expected month 4, got {booking.booking_time.month}"
        assert booking.booking_time.day == 15, f"Expected day 15, got {booking.booking_time.day}"
        assert booking.booking_time.hour == 15, f"Expected hour 15 (3 PM), got {booking.booking_time.hour}"

    def test_evening_time_default(self):
        response = self.process_and_print("Book a plumber")
        assert "date" in response.lower(), "Should ask for date"
        response = self.process_and_print("tomorrow")
        assert "time" in response.lower(), "Should ask for time"
        response = self.process_and_print("6")
        assert "AM or PM" not in response, "Should not ask for AM/PM"
        assert "available" in response.lower(), "Should show available technicians"
