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


@pytest.fixture(autouse=True)
def reset_database():
    from app.db.database import bookings_db, next_id
    bookings_db.clear()
    globals()['next_id'] = 1
    yield
    bookings_db.clear()
    globals()['next_id'] = 1


class TestContextResetIssues:
    def setup_method(self):
        self.nlp = NaturalLanguageProcessor()
        self.responses = []

    def process_and_log(self, input_text):
        response = self.nlp.process_input(input_text)
        self.responses.append((input_text, response))
        return response

    def test_context_reset_after_booking(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("Hello")
        assert "how can i assist you" in response.lower(), "System should respond with a greeting"
        assert "couldn't find a technician matching" not in response.lower(
        ), "System should not think we're selecting a technician"

    def test_greeting_after_booking(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("Hello")
        assert "hello" in response.lower() or "welcome" in response.lower(
        ) or "hi" in response.lower(), "System should respond to greeting"
        assert "how can i help" in response.lower(
        ) or "assist you" in response.lower(), "System should offer assistance"

    def test_new_booking_after_completion(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("Make another appointment")
        assert "technician" in response.lower() and "need" in response.lower(), "System should ask for technician type"
        self.process_and_log("electrician")
        self.process_and_log("next monday")
        self.process_and_log("2:00 PM")
        response = self.process_and_log("1")
        assert "confirmed" in response.lower(), "Second booking should be confirmed"

    def test_error_handling_after_booking(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        self.process_and_log("1")
        response = self.process_and_log("1")
        assert "error" not in response.lower(), "System should not show an error message"
        assert "sorry" not in response.lower(), "System should not apologize for an error"

    def test_multiple_bookings_sequence(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        response1 = self.process_and_log("1")
        booking_id_match1 = re.search(r'booking ID is (\d+)', response1)
        assert booking_id_match1, "Could not find booking ID in first response"
        booking_id1 = int(booking_id_match1.group(1))
        self.process_and_log("Make an appointment for electrician")
        self.process_and_log("next tuesday")
        self.process_and_log("2:00 PM")
        response2 = self.process_and_log("1")
        booking_id_match2 = re.search(r'booking ID is (\d+)', response2)
        assert booking_id_match2, "Could not find booking ID in second response"
        booking_id2 = int(booking_id_match2.group(1))
        assert booking_id1 != booking_id2, "Booking IDs should be different"
        booking1 = get_booking_by_id(booking_id1)
        booking2 = get_booking_by_id(booking_id2)
        assert booking1 is not None, "First booking should exist"
        assert booking2 is not None, "Second booking should exist"
        assert booking1.specialty == "Plumber", "First booking should be for a plumber"
        assert booking2.specialty == "Electrician", "Second booking should be for an electrician"

    def test_cancel_during_update(self):
        self.process_and_log("Make an appointment for plumber")
        self.process_and_log("tomorrow")
        self.process_and_log("3:00 PM")
        response = self.process_and_log("1")
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = booking_id_match.group(1)
        self.process_and_log(f"Update booking {booking_id}")
        response = self.process_and_log("Cancel")
        assert "cancel" in response.lower() or "process" in response.lower(), "System should acknowledge cancellation"
        assert "date" not in response.lower(), "System should not ask for a date after cancellation"
        response = self.process_and_log("Hello")
        assert "hello" in response.lower() or "hi" in response.lower(
        ), "System should respond to greeting after cancellation"
