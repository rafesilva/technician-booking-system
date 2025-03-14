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


class TestBookingEdgeCases:
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

    def test_booking_conflict_handling(self):
        self.process_and_log("Make an appointment for plumber April 15 3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("Make an appointment for plumber")
        assert "date" in response.lower(), "System should ask for date"
        response = self.process_and_log("April 15")
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("3:00 PM")
        assert "already a booking" in response.lower(
        ) or "conflict" in response.lower(), "System should detect booking conflict"
        response = self.process_and_log("4:00 PM")
        assert "For 4:00 PM, we have the following" in response, "System should offer technician selection"
        assert "Please select a technician by number or name" in response, "System should prompt for technician selection"

    def test_booking_cancellation(self):
        self.process_and_log("Make an appointment for plumber April 15 3:00 PM")
        response = self.process_and_log("1")
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = booking_id_match.group(1)
        self.nlp = NaturalLanguageProcessor()
        response = self.process_and_log("Cancel a booking")
        response = self.process_and_log(booking_id)
        assert "cancelled" in response.lower(), "System should confirm cancellation"
        booking = get_booking_by_id(int(booking_id))
        assert booking is None, f"Booking with ID {booking_id} should be deleted"

    def test_cancel_during_booking_process(self):
        self.process_and_log("Make an appointment for plumber")
        response = self.process_and_log("cancel")
        assert "cancelled" in response.lower(), "System should confirm cancellation"
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("April 15")
        response = self.process_and_log("cancel")
        assert "cancelled" in response.lower(), "System should confirm cancellation"

    def test_combined_command_with_conflict(self):
        self.process_and_log("Make an appointment for plumber April 15 3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("Make an appointment for plumber")
        assert "date" in response.lower(), "System should ask for date"
        response = self.process_and_log("April 15")
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("3:00 PM")
        assert "already a booking" in response.lower(
        ) or "conflict" in response.lower(), "System should detect booking conflict"
        response = self.process_and_log("no")
        assert "cancelled" in response.lower(), "System should cancel the booking process"
