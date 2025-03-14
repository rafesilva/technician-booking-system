import pytest
from datetime import datetime, timedelta
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.db.database import reset_database


class TestCombinedInputs:
    @pytest.mark.parametrize("date_input, time_input, expected_hour, expected_minute", [
        ("tomorrow", "3 PM", 15, 0),
        ("next Monday", "2:30 PM", 14, 30),
        ("Friday", "10 AM", 10, 0),
        ("Tuesday", "4:15 PM", 16, 15),
        ("tomorrow", "morning", 9, 0),
        ("next Wednesday", "afternoon", 12, 0),
        ("Thursday", "evening", 18, 0),
        ("tomorrow", "9:30 AM", 9, 30)
    ])
    def test_date_then_time_inputs(
            self, date_input, time_input, expected_hour, expected_minute):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        assert "date" in response1.lower() or "when" in response1.lower(
        ), f"System should ask for date, got: {response1}"
        response2 = nlp.process_input(date_input)
        assert "time" in response2.lower() or "when" in response2.lower(
        ), f"System should ask for time, got: {response2}"
        response3 = nlp.process_input(time_input)
        assert ("technician" in response3.lower() or
                "available" in response3.lower() or
                "already a booking" in response3.lower()), f"System did not recognize time input or conflict: {response3}"
        if "already a booking" in response3.lower():
            return
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.hour == expected_hour, f"Expected hour {expected_hour}, got {time_dt.hour}"
        assert time_dt.minute == expected_minute, f"Expected minute {expected_minute}, got {time_dt.minute}"

    @pytest.mark.parametrize("specialty, date_input, time_input", [
        ("plumber", "tomorrow", "3 PM"),
        ("electrician", "next Monday", "2:30 PM"),
        ("welder", "Friday", "10 AM"),
        ("carpenter", "Tuesday", "4:15 PM")
    ])
    def test_specialty_with_date_time(self, specialty, date_input, time_input):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input(f"I need to book a {specialty}")
        assert "date" in response1.lower() or "when" in response1.lower(
        ), f"System should ask for date, got: {response1}"
        response2 = nlp.process_input(date_input)
        assert "time" in response2.lower() or "when" in response2.lower(
        ), f"System should ask for time, got: {response2}"
        response3 = nlp.process_input(time_input)
        assert ("technician" in response3.lower() or
                "available" in response3.lower() or
                "already a booking" in response3.lower()), f"System did not recognize time input or conflict: {response3}"
        if "already a booking" in response3.lower():
            return
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        assert not nlp.user_context.get(
            "awaiting_time", False), "System should not be awaiting time after time input"

    def test_complete_booking_flow(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        assert "date" in response1.lower() or "when" in response1.lower(
        ), f"System should ask for date, got: {response1}"
        response2 = nlp.process_input("tomorrow")
        assert "time" in response2.lower() or "when" in response2.lower(
        ), f"System should ask for time, got: {response2}"
        response3 = nlp.process_input("3 PM")
        assert ("technician" in response3.lower() or
                "available" in response3.lower() or
                "already a booking" in response3.lower()), f"System did not recognize time input or conflict: {response3}"
        if "already a booking" in response3.lower():
            return
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.hour == 15, f"Expected hour 15, got {time_dt.hour}"
        assert time_dt.minute == 0, f"Expected minute 0, got {time_dt.minute}"
        assert nlp.user_context.get(
            "awaiting_technician", False), "System should be awaiting technician selection"
        specialty = nlp.user_context.get(
            "specialty") or nlp.user_context.get("temp_booking_specialty")
        assert specialty is not None, "Specialty should be set in user_context"
        assert specialty.lower(
        ) == "plumber", f"Expected specialty 'plumber', got '{specialty}'"

    @pytest.mark.parametrize("combined_input, expected_month, expected_day, expected_hour, expected_minute", [
        ("Book a plumber for April 15 at 3:16 PM", 4, 15, 15, 16),
        ("Book a plumber for May 20 at 10:30 AM", 5, 20, 10, 30),
        ("Book a plumber for June 5 at 2:45 PM", 6, 5, 14, 45),
        ("Book a plumber for July 10 at 9 PM", 7, 10, 21, 0)
    ])
    def test_combined_date_time_inputs(
            self, combined_input, expected_month, expected_day, expected_hour, expected_minute):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response = nlp.process_input(combined_input)
        assert ("technician" in response.lower() or
                "available" in response.lower() or
                "already a booking" in response.lower()), f"System did not recognize combined input or conflict: {response}"
        if "already a booking" in response.lower():
            return
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.month == expected_month, f"Expected month {expected_month}, got {time_dt.month}"
        assert time_dt.day == expected_day, f"Expected day {expected_day}, got {time_dt.day}"
        assert time_dt.hour == expected_hour, f"Expected hour {expected_hour}, got {time_dt.hour}"
        assert time_dt.minute == expected_minute, f"Expected minute {expected_minute}, got {time_dt.minute}"
