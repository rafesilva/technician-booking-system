import pytest
from datetime import datetime
from app.nlp.utils.date_time_parser import DateTimeParser
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor


class TestTimeInputVariations:
    @pytest.mark.parametrize("time_str, expected_hour, expected_minute", [
        ("3:14 AM", 3, 14),
        ("3:14 PM", 15, 14),
        ("5:50 AM", 5, 50),
        ("5:50 PM", 17, 50),
        ("9:41 AM", 9, 41),
        ("9:41 PM", 21, 41),
        ("4:44 AM", 4, 44),
        ("4:44 PM", 16, 44),
        ("3:14 in the morning", 3, 14),
        ("3:14 in the afternoon", 15, 14),
        ("5:50 in the morning", 5, 50),
        ("5:50 in the evening", 17, 50),
        ("9:41 in the morning", 9, 41),
        ("9:41 at night", 21, 41),
        ("4:44 in the morning", 4, 44),
        ("4:44 in the evening", 16, 44),
    ])
    def test_time_parser(self, time_str, expected_hour, expected_minute):
        parser = DateTimeParser()
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = parser.parse_time(time_str, today)
        assert result is not None, f"Could not parse '{time_str}'"
        time_dt, time_desc = result
        actual_hour = time_dt.hour
        actual_minute = time_dt.minute
        assert actual_hour == expected_hour, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"
        assert actual_minute == expected_minute, f"Expected {expected_hour:02d}:{expected_minute:02d}, got {actual_hour:02d}:{actual_minute:02d}"

    @pytest.mark.parametrize("specialty, day, time_input", [
        ("plumber", "tomorrow", "3:14 AM"),
        ("plumber", "tomorrow", "3:14 PM"),
        ("plumber", "tomorrow", "3:14"),
        ("electrician", "tomorrow", "5:50 AM"),
        ("electrician", "tomorrow", "5:50 PM"),
        ("electrician", "tomorrow", "5:50"),
        ("welder", "tomorrow", "9:41 AM"),
        ("welder", "tomorrow", "9:41 PM"),
        ("welder", "tomorrow", "9:41"),
        ("carpenter", "tomorrow", "4:44 AM"),
        ("carpenter", "tomorrow", "4:44 PM"),
        ("carpenter", "tomorrow", "4:44")
    ])
    def test_booking_conversations(self, specialty, day, time_input):
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input(f"I need to book a {specialty}")
        assert "date" in response1.lower() or "when" in response1.lower(
        ), f"System should ask for date, got: {response1}"
        response2 = nlp.process_input(day)
        assert "time" in response2.lower() or "when" in response2.lower(
        ), f"System should ask for time, got: {response2}"
        response3 = nlp.process_input(time_input)
        time_recognized = time_input in response3 or time_input.replace(
            " AM", "").replace(" PM", "") in response3
        assert time_recognized or "technician" in response3.lower(
        ), f"Time '{time_input}' was not recognized in the response: {response3}"
        if "AM" in time_input.upper() or "PM" in time_input.upper():
            assert not nlp.user_context.get(
                "awaiting_ampm", False), f"System should not ask for AM/PM clarification for '{time_input}'"
        else:
            assert nlp.user_context.get(
                "awaiting_ampm", False), f"System should ask for AM/PM clarification for '{time_input}'"

    @pytest.mark.parametrize("time_input", ["3:14", "5:50", "9:41", "4:44"])
    def test_ampm_handling(self, time_input):
        nlp = NaturalLanguageProcessor()
        nlp.user_context["awaiting_time"] = True
        nlp.user_context["temp_booking_date"] = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        nlp.user_context["temp_booking_specialty"] = "Plumber"
        response = nlp.process_input(time_input)
        assert time_input in response, f"Time '{time_input}' was not recognized in the response: {response}"
        assert nlp.user_context.get(
            "awaiting_ampm", False), f"System should ask for AM/PM clarification for '{time_input}'"
        hour = int(time_input.split(':')[0])
        minute = int(time_input.split(':')[1])
        assert nlp.user_context.get(
            "temp_booking_hour") == hour, f"Expected hour {hour}, got {nlp.user_context.get('temp_booking_hour')}"
        assert nlp.user_context.get(
            "temp_booking_minute") == minute, f"Expected minute {minute}, got {nlp.user_context.get('temp_booking_minute')}"
