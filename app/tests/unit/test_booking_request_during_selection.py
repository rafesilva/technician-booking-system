import pytest
import unittest
from datetime import datetime
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.handlers.technician_handler import TechnicianHandler
from app.nlp.managers.user_context_manager import UserContextManager
from app.db.database import reset_database


class TestBookingRequestDuringSelection(unittest.TestCase):
    def test_book_a_technician_during_selection(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        self.assertIn("date", response1.lower(), "System should ask for date")
        response2 = nlp.process_input("tomorrow")
        self.assertIn("time", response2.lower(), "System should ask for time")
        response3 = nlp.process_input("1:30 PM")
        if "conflict" in response3.lower() or "already a booking" in response3.lower():
            response3 = nlp.process_input("10:30 AM")
        self.assertTrue(
            "available" in response3.lower() or
            "select a technician" in response3.lower(),
            f"System should show available technicians, got: {response3}"
        )
        self.assertTrue(nlp.user_context.get("awaiting_technician", False),
                        "System should be awaiting technician selection")
        response4 = nlp.process_input("Book a technician")
        self.assertIn("technician", response4.lower(), "System should ask for technician type")
        self.assertFalse(nlp.user_context.get("awaiting_technician", False),
                         "System should no longer be awaiting technician selection")
        self.assertTrue(nlp.user_context.get("awaiting_specialty", False),
                        "System should be awaiting specialty")

    def test_book_specific_technician_during_selection(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        self.assertIn("date", response1.lower(), "System should ask for date")
        response2 = nlp.process_input("tomorrow")
        self.assertIn("time", response2.lower(), "System should ask for time")
        response3 = nlp.process_input("3:45 PM")
        if "conflict" in response3.lower() or "already a booking" in response3.lower():
            response3 = nlp.process_input("8:45 AM")
        self.assertTrue(
            "available" in response3.lower() or
            "select a technician" in response3.lower(),
            f"System should show available technicians, got: {response3}"
        )
        self.assertTrue(nlp.user_context.get("awaiting_technician", False),
                        "System should be awaiting technician selection")
        response4 = nlp.process_input("Book an electrician")
        self.assertIn("date", response4.lower(), "System should ask for date for the new booking")
        self.assertFalse(nlp.user_context.get("awaiting_technician", False),
                         "System should no longer be awaiting technician selection")
        self.assertEqual(nlp.user_context.get("temp_booking_specialty"), "Electrician",
                         "System should set the new specialty to Electrician")

    def test_normal_technician_selection_still_works(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        self.assertIn("date", response1.lower(), "System should ask for date")
        response2 = nlp.process_input("tomorrow")
        self.assertIn("time", response2.lower(), "System should ask for time")
        response3 = nlp.process_input("3:45 PM")
        if "conflict" in response3.lower() or "already a booking" in response3.lower():
            response3 = nlp.process_input("8:45 AM")
        self.assertTrue(
            "available" in response3.lower() or
            "select a technician" in response3.lower(),
            f"System should show available technicians, got: {response3}"
        )
        self.assertTrue(nlp.user_context.get("awaiting_technician", False),
                        "System should be awaiting technician selection")
        response4 = nlp.process_input("1")
        self.assertIn("confirmed", response4.lower(), "System should confirm the booking")
        self.assertIn("booking id", response4.lower(), "System should provide a booking ID")

    def test_technician_selection_by_name_still_works(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        self.assertIn("date", response1.lower(), "System should ask for date")
        response2 = nlp.process_input("tomorrow")
        self.assertIn("time", response2.lower(), "System should ask for time")
        response3 = nlp.process_input("2:30 PM")
        if "conflict" in response3.lower() or "already a booking" in response3.lower():
            response3 = nlp.process_input("11:30 AM")
        self.assertTrue(
            "available" in response3.lower() or
            "select a technician" in response3.lower(),
            f"System should show available technicians, got: {response3}"
        )
        self.assertTrue(nlp.user_context.get("awaiting_technician", False),
                        "System should be awaiting technician selection")
        technicians = nlp.user_context.get("available_technicians", [])
        self.assertTrue(len(technicians) > 0, "There should be available technicians")
        first_name = technicians[0].split()[0]
        response4 = nlp.process_input(first_name)
        self.assertIn("confirmed", response4.lower(), "System should confirm the booking")
        self.assertIn("booking id", response4.lower(), "System should provide a booking ID")


if __name__ == "__main__":
    unittest.main()
