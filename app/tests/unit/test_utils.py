from app.nlp.utils.booking_data_extractor import BookingDataExtractor
from app.nlp.utils.intent_recognizer import IntentRecognizer
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestUtils(unittest.TestCase):
    def test_extract_specialty(self):
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need a plumber"), "Plumber")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need an electrician"), "Electrician")
        self.assertEqual(
            BookingDataExtractor.extract_specialty("I need a welder"),
            "Welder")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need a gardener"), "Gardener")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need a carpenter"), "Carpenter")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need a painter"), "Painter")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need an HVAC technician"), "HVAC")
        self.assertEqual(
            BookingDataExtractor.extract_specialty("I need a plumer"),
            "Plumber")
        self.assertEqual(BookingDataExtractor.extract_specialty(
            "I need an electritian"), "Electrician")
        self.assertIsNone(BookingDataExtractor.extract_specialty("Hello"))
        self.assertIsNone(BookingDataExtractor.extract_specialty("I need help"))
        self.assertIsNone(BookingDataExtractor.extract_specialty("I need a technician"))

    def test_intent_recognizer(self):
        self.assertTrue(IntentRecognizer.is_booking_request("I need a plumber"))
        self.assertTrue(IntentRecognizer.is_booking_request(
            "I want to book an electrician"))
        self.assertTrue(IntentRecognizer.is_booking_request(
            "I'd like to schedule a welder"))
        self.assertTrue(
            IntentRecognizer.is_list_bookings_request("Show me my bookings"))
        self.assertTrue(IntentRecognizer.is_list_bookings_request(
            "List all my appointments"))
        self.assertTrue(IntentRecognizer.is_list_bookings_request("Show my bookings"))
        self.assertTrue(IntentRecognizer.is_cancellation_request(
            "Cancel my booking with ID 123"))
        self.assertTrue(IntentRecognizer.is_cancellation_request(
            "I want to cancel my appointment"))
        self.assertTrue(IntentRecognizer.is_cancellation_request("Cancel booking 456"))
        self.assertTrue(IntentRecognizer.is_update_request(
            "Update my booking with ID 123"))
        self.assertTrue(IntentRecognizer.is_update_request(
            "I want to reschedule my appointment"))
        self.assertTrue(IntentRecognizer.is_update_request("Change booking 456"))


if __name__ == "__main__":
    unittest.main()
