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


class TestTimeHandling:
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

    def test_ampm_clarification_for_ambiguous_times(self):
        ambiguous_times = ["5:00", "5:30", "6:15", "6:45", "7:00"]
        for time_str in ambiguous_times:
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            self.process_and_log("Make an appointment for plumber")
            self.process_and_log("April 15")
            response = self.process_and_log(time_str)
            assert "am or pm" in response.lower(
            ), f"System should ask for AM/PM clarification for {time_str}"
            response = self.process_and_log("PM")
            assert "we have the following Plumbers available" in response, f"System should offer technician selection for {time_str} PM"

    def test_no_ampm_clarification_for_unambiguous_times(self):
        unambiguous_times = [
            "1:00",
            "2:30",
            "3:15",
            "4:45",
            "8:00",
            "9:30",
            "10:15",
            "11:45",
            "12:00"]
        for time_str in unambiguous_times:
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            self.process_and_log("Make an appointment for plumber")
            self.process_and_log("April 15")
            response = self.process_and_log(time_str)
            assert "am or pm" in response.lower(
            ), f"System should ask for AM/PM clarification for {time_str}"
            assert "Is that" in response, "System should use the proper AM/PM clarification format"
            response = self.process_and_log("PM")
            assert "we have the following" in response.lower(
            ), f"System should proceed to technician selection after PM response"

    def test_different_time_formats(self):
        time_formats = {
            "3 PM": 15,
            "3:30 PM": 15,
            "3:45 PM": 15,
            "15:00 AM": 15,
            "15:30 PM": 15,
            "3 in the afternoon": 15,
            "3 in the evening": 15,
            "morning": 9,
            "afternoon": 12,
            "evening": 18,
            "night": 20
        }
        for time_str, expected_hour in time_formats.items():
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            self.process_and_log("Make an appointment for plumber")
            self.process_and_log("April 15")
            response = self.process_and_log(time_str)
            if "15:00" in time_str or "15:30" in time_str:
                if "am or pm" in response.lower():
                    response = self.process_and_log("PM")
            assert "we have the following Plumbers available" in response, f"System should offer technician selection for {time_str}"
            response = self.process_and_log("1")
            booking_id_match = re.search(r'booking ID is (\d+)', response)
            assert booking_id_match, f"Could not find booking ID in response for {time_str}"
            booking_id = int(booking_id_match.group(1))
            booking = get_booking_by_id(booking_id)
            assert booking is not None, f"Booking with ID {booking_id} not found in database for {time_str}"
            assert booking.booking_time.hour == expected_hour, f"Expected hour {expected_hour}, got {booking.booking_time.hour} for {time_str}"

    def test_ampm_response_handling(self):
        ampm_responses = {
            "AM": "AM",
            "am": "AM",
            "PM": "PM",
            "pm": "PM"
        }
        for response_str, expected_ampm in ampm_responses.items():
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            self.process_and_log("Make an appointment for plumber")
            self.process_and_log("April 15")
            self.process_and_log("5:00")
            response = self.process_and_log(response_str)
            assert "For 5:00" in response, f"System should offer technician selection for 5:00 {response_str}"

    def test_invalid_ampm_responses(self):
        invalid_responses = ["a.m.", "p.m.", "morning", "evening", "night", "afternoon"]
        for response_str in invalid_responses:
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            self.process_and_log("Make an appointment for plumber")
            self.process_and_log("April 15")
            self.process_and_log("5:00")
            response = self.process_and_log(response_str)
            assert "couldn't understand" in response.lower() or "invalid" in response.lower(
            ), f"System should reject invalid AM/PM response: {response_str}"
