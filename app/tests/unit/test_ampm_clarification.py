import pytest
from datetime import datetime
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.constants import TIME_WITHOUT_AMPM_PATTERN


class TestAMPMClarification:
    @pytest.mark.parametrize("time_input", [
        "3:00", "3:14",
        "5:00", "5:50",
        "9:00", "9:41",
        "4:00", "4:44",
        "12:00", "12:30"
    ])
    def test_ampm_clarification_behavior(self, time_input):
        nlp = NaturalLanguageProcessor()
        nlp.user_context["awaiting_time"] = True
        nlp.user_context["temp_booking_date"] = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        nlp.user_context["temp_booking_specialty"] = "Plumber"
        response = nlp.process_input(time_input)
        time_recognized = time_input in response or (
            time_input.split(':')[0] in response and ':00' in response)
        assert time_recognized, f"Time '{time_input}' was not recognized in the response: {response}"
        assert nlp.user_context.get(
            "awaiting_ampm", False), f"System should ask for AM/PM clarification for '{time_input}'"
        hour = int(time_input.split(':')[0])
        minute = int(time_input.split(':')[1])
        assert nlp.user_context.get(
            "temp_booking_hour") == hour, f"Expected hour {hour}, got {nlp.user_context.get('temp_booking_hour')}"
        assert nlp.user_context.get(
            "temp_booking_minute") == minute, f"Expected minute {minute}, got {nlp.user_context.get('temp_booking_minute')}"

    @pytest.mark.parametrize("time_input, expected_hour, expected_minute", [
        ("3:00 AM", 3, 0),
        ("3:14 AM", 3, 14),
        ("5:00 AM", 5, 0),
        ("5:50 PM", 17, 50),
        ("9:00 AM", 9, 0),
        ("9:41 PM", 21, 41),
        ("4:00 PM", 16, 0),
        ("4:44 PM", 16, 44),
        ("12:00 PM", 12, 0),
        ("12:30 PM", 12, 30)
    ])
    def test_parser_directly(self, time_input, expected_hour, expected_minute):
        parser = DateTimeParser()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = parser.parse_time(time_input, today)
        assert result is not None, f"Could not parse '{time_input}'"
        time_dt, time_desc = result
        actual_hour = time_dt.hour
        actual_minute = time_dt.minute
        assert actual_hour == expected_hour, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"
        assert actual_minute == expected_minute, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"

    def test_booking_with_ampm_response(self):
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need to book a plumber")
        assert "What date" in response1 or "When" in response1, "System should ask for date"
        response2 = nlp.process_input("Tomorrow")
        assert "What time" in response2 or "When" in response2, "System should ask for time"
        response3 = nlp.process_input("5:00")
        assert nlp.user_context.get(
            "awaiting_ampm", False), "System should ask for AM/PM clarification for '5:00'"
        assert "AM or PM" in response3, "Response should ask for AM or PM"
        response4 = nlp.process_input("AM")
        assert not nlp.user_context.get(
            "awaiting_ampm", False), "System should no longer be awaiting AM/PM"
        if "temp_booking_time" in nlp.user_context and nlp.user_context["temp_booking_time"]:
            time_dt = nlp.user_context["temp_booking_time"]
            assert time_dt.hour == 5, f"Expected 05:00, got {time_dt.hour:02d}:{time_dt.minute:02d}"

    @pytest.mark.parametrize("time_input", ["5:00", "6:00", "7:00", "5:30", "6:45", "7:15"])
    def test_time_without_ampm_pattern_matching(self, time_input):
        import re
        match = re.search(TIME_WITHOUT_AMPM_PATTERN, time_input)
        assert match is not None, f"TIME_WITHOUT_AMPM_PATTERN should match '{time_input}'"
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        expected_hour = int(time_input.split(':')[0])
        expected_minute = int(time_input.split(':')[1]) if ':' in time_input else 0
        assert hour == expected_hour, f"Expected hour {expected_hour}, got {hour}"
        assert minute == expected_minute, f"Expected minute {expected_minute}, got {minute}"
        parser = DateTimeParser()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = parser.parse_time(time_input, today)
        assert result[0] is None, f"Expected None for time {time_input} without AM/PM"

    @pytest.mark.parametrize("time_input, am_pm, expected_hour", [
        ("5:00", "AM", 5),
        ("5:00", "PM", 17),
        ("6:30", "AM", 6),
        ("6:30", "PM", 18),
        ("7:15", "AM", 7),
        ("7:15", "PM", 19)
    ])
    def test_full_ampm_clarification_flow(self, time_input, am_pm, expected_hour):
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response = nlp.process_input(time_input)
        assert "AM or PM" in response, f"Response should ask for AM or PM for time {time_input}"
        assert nlp.user_context.get(
            "awaiting_ampm", False), f"System should be awaiting AM/PM for {time_input}"
        nlp.process_input(am_pm)
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.hour == expected_hour, f"Expected hour {expected_hour}, got {time_dt.hour}"
        minute = int(time_input.split(':')[1])
        assert time_dt.minute == minute, f"Expected minute {minute}, got {time_dt.minute}"
