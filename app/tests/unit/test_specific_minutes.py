import pytest
from datetime import datetime
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser


class TestSpecificMinutes:
    @pytest.mark.parametrize("time_input, expected_hour, expected_minute", [
        ("3:14 PM", 15, 14),
        ("3:30 PM", 15, 30),
        ("3:45 PM", 15, 45),
        ("4:15 PM", 16, 15),
        ("4:20 PM", 16, 20),
        ("4:55 PM", 16, 55),
        ("9:05 PM", 21, 5),
        ("9:10 PM", 21, 10),
        ("9:59 PM", 21, 59),
        ("12:30 PM", 12, 30),
        ("12:45 PM", 12, 45)
    ])
    def test_specific_minutes_parser(self, time_input, expected_hour, expected_minute):
        parser = DateTimeParser()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = parser.parse_time(time_input, today)
        assert result is not None, f"Could not parse '{time_input}'"
        time_dt, time_desc = result
        actual_hour = time_dt.hour
        actual_minute = time_dt.minute
        assert actual_hour == expected_hour, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"
        assert actual_minute == expected_minute, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"

    @pytest.mark.parametrize("time_input, expected_minute", [
        ("3:14", 14),
        ("3:30", 30),
        ("3:45", 45),
        ("4:15", 15),
        ("4:20", 20),
        ("4:55", 55),
        ("9:05", 5),
        ("9:10", 10),
        ("9:59", 59),
        ("12:30", 30),
        ("12:45", 45)
    ])
    def test_specific_minutes_in_nlp(self, time_input, expected_minute):
        nlp = NaturalLanguageProcessor()
        nlp.user_context["awaiting_time"] = True
        nlp.user_context["temp_booking_date"] = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        nlp.user_context["temp_booking_specialty"] = "Plumber"
        response = nlp.process_input(time_input)
        assert time_input in response or f":{expected_minute:02d}" in response, f"Time '{time_input}' was not recognized in the response: {response}"
        assert nlp.user_context.get(
            "awaiting_ampm", False), f"System should ask for AM/PM clarification for '{time_input}'"
        if "temp_booking_minute" in nlp.user_context:
            minute = nlp.user_context.get("temp_booking_minute")
            assert minute == expected_minute, f"Expected minute {expected_minute}, got {minute}"

    def test_booking_with_specific_minutes(self):
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need to book a plumber")
        assert "date" in response1.lower() or "when" in response1.lower(
        ), f"System should ask for date, got: {response1}"
        response2 = nlp.process_input("Tomorrow")
        assert "time" in response2.lower() or "when" in response2.lower(
        ), f"System should ask for time, got: {response2}"
        response3 = nlp.process_input("3:45 PM")
        assert "3:45" in response3 or "3:45 PM" in response3, f"Time '3:45 PM' was not recognized in the response: {response3}"
        assert not nlp.user_context.get(
            "awaiting_ampm", False), "System should not ask for AM/PM clarification for '3:45 PM'"
        if "temp_booking_time" in nlp.user_context and nlp.user_context["temp_booking_time"]:
            time_dt = nlp.user_context["temp_booking_time"]
            assert time_dt.hour == 15, f"Expected hour 15, got {time_dt.hour}"
            assert time_dt.minute == 45, f"Expected minute 45, got {time_dt.minute}"
