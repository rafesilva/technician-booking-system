from app.db.database import get_booking_by_id, reset_database
from app.models.booking import Booking
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
import pytest
import sys
import os
import re
from datetime import datetime, timedelta
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)))))


class TestContextRetentionIssues:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        reset_database()
        self.nlp = NaturalLanguageProcessor()
        self.responses = []

    def process_and_log(self, input_text):
        response = self.nlp.process_input(input_text)
        self.responses.append(f"User: {input_text}")
        self.responses.append(f"System: {response}")
        return response

    def test_combined_booking_command(self):
        response = self.process_and_log("Make an appointment for plumber April 15 3:00 PM")
        assert "we have the following Plumbers available" in response, "System should offer technician selection"
        assert "3:00 PM" in response, "System should recognize the time"
        response = self.process_and_log("1")
        assert "confirmed" in response.lower(), "Booking should be confirmed"
        assert "booking id" in response.lower(), "Booking ID should be provided"
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found in database"
        assert booking.specialty.lower(
        ) == "plumber", f"Expected specialty 'plumber', got '{booking.specialty}'"
        assert booking.booking_time.hour == 15, f"Expected hour 15 (3 PM), got {booking.booking_time.hour}"
        assert booking.booking_time.minute == 0, f"Expected minute 0, got {booking.booking_time.minute}"

    def test_time_without_ampm_clarification(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("April 15")
        response = self.process_and_log("5:15")
        assert "am or pm" in response.lower(), "System should ask for AM/PM clarification"
        response = self.process_and_log("PM")
        assert "we have the following Plumbers available" in response, "System should offer technician selection"
        assert "5:15 PM" in response, "System should recognize the time with PM"

    def test_combined_date_time_in_booking(self):
        self.process_and_log("Make an appointment for plumber")
        response = self.process_and_log("April 15 7:00 PM")
        if "What time would you like to book" in response:
            response = self.process_and_log("7:00 PM")
        assert "we have the following Plumbers available" in response, "System should offer technician selection"
        assert "7:00 PM" in response, "System should recognize the time"

    def test_redundant_prompting_fix(self):
        response = self.process_and_log("Make an appointment for plumber April 15 7:00 PM")
        assert "we have the following Plumbers available" in response, "System should offer technician selection"
        assert "7:00 PM" in response, "System should recognize the time"
        assert "What time would you like to book" not in response, "System should not ask for time again"

    def test_context_retention_between_messages(self):
        self.process_and_log("Make an appointment")
        response = self.process_and_log("plumber")
        assert "date" in response.lower(), "System should ask for date"
        response = self.process_and_log("April 15")
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("7:00 PM")
        assert "we have the following Plumbers available" in response, "System should offer technician selection"
        assert "7:00 PM" in response, "System should recognize the time"
