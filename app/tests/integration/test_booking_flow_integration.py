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


class TestBookingFlowIntegration:
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

    def test_complete_booking_flow(self):
        response = self.process_and_log("I need to book a plumber for a leaky faucet")
        assert "date" in response.lower(), "System should ask for date"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
        response = self.process_and_log(tomorrow)
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("3:30 PM")
        assert "technician" in response.lower() or "available" in response.lower(
        ), "System should prompt for technician selection"
        response = self.process_and_log("1")
        assert "confirmed" in response.lower(), "Booking should be confirmed"
        assert "booking id" in response.lower() or "booking ID" in response.lower(
        ), "Response should include booking ID"
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found in database"
        assert booking.specialty.lower(
        ) == "plumber", f"Expected specialty 'plumber', got '{booking.specialty}'"
        response = self.process_and_log(
            f"What are the details for booking {booking_id}?")
        assert str(booking_id) in response, "Response should include the booking ID"
        assert "plumber" in response.lower(), "Response should include the specialty"
        assert "3:30 pm" in response.lower() or "3:30 PM" in response.lower(
        ), "Response should include the booking time"

    def test_ampm_clarification_integration(self):
        self.process_and_log("I need a plumber")
        self.process_and_log("tomorrow")
        response = self.process_and_log("5:00")
        assert "am or pm" in response.lower(), "System should ask for AM/PM clarification"
        response = self.process_and_log("PM")
        assert "technician" in response.lower() or "available" in response.lower(
        ), "System should prompt for technician selection"
        response = self.process_and_log("1")
        assert "confirmed" in response.lower(), "Booking should be confirmed"
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found in database"
        assert booking.booking_time.hour == 17, f"Expected hour 17 (5 PM), got {booking.booking_time.hour}"

    def test_different_specialties(self):
        specialties = ["electrician", "plumber", "HVAC technician"]
        for specialty in specialties:
            reset_database()
            self.nlp = NaturalLanguageProcessor()
            self.responses = []
            response = self.process_and_log(f"I need an {specialty}")
            assert "date" in response.lower(
            ), f"System should ask for date when booking {specialty}"
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
            response = self.process_and_log(tomorrow)
            assert "time" in response.lower(
            ), f"System should ask for time when booking {specialty}"
            response = self.process_and_log("2:00 PM")
            assert "technician" in response.lower() or "available" in response.lower(
            ),                f"System should prompt for technician selection when booking {specialty}"
            response = self.process_and_log("1")
            assert "confirmed" in response.lower(), f"Booking should be confirmed for {specialty}"
            assert "booking id" in response.lower() or "booking ID" in response.lower(
            ),                f"Response should include booking ID for {specialty}"

    def test_full_booking_flow(self):
        response = self.process_and_log("Hello")
        assert "welcome" in response.lower() or "hello" in response.lower(), "System should greet the user"
        response = self.process_and_log("Make an appointment")
        assert "specialty" in response.lower() or "type of technician" in response.lower(
        ), "System should ask for technician type"
        response = self.process_and_log("plumber")
        assert "date" in response.lower(), "System should ask for date"
        response = self.process_and_log("April 15")
        assert "time" in response.lower(), "System should ask for time"
        response = self.process_and_log("3:30 PM")
        assert "technician" in response.lower() or "available" in response.lower(
        ), "System should prompt for technician selection"
        response = self.process_and_log("1")
        assert "confirmed" in response.lower(), "Booking should be confirmed"
        assert "booking id" in response.lower() or "booking ID" in response.lower(), "Booking ID should be provided"
        booking_id_match = re.search(r'booking ID is (\d+)', response)
        assert booking_id_match, "Could not find booking ID in response"
        booking_id = int(booking_id_match.group(1))
        booking = get_booking_by_id(booking_id)
        assert booking is not None, f"Booking with ID {booking_id} not found in database"
        assert booking.specialty.lower(
        ) == "plumber", f"Expected specialty 'plumber', got '{booking.specialty}'"
