import pytest
from datetime import datetime
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.db.database import reset_database


class TestDateParsingEdgeCases:
    def test_april_15_parsing(self):
        parser = DateTimeParser()
        date_result, date_desc = parser.parse_date("April 15")
        assert date_result is not None, "Date should be parsed successfully"
        assert date_desc == "April 15", f"Expected description 'April 15', got '{date_desc}'"
        assert date_result.month == 4, f"Expected month 4, got {date_result.month}"
        assert date_result.day == 15, f"Expected day 15, got {date_result.day}"

    def test_april_15_in_processor(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        assert "date" in response1.lower(), "System should ask for date"
        response2 = nlp.process_input("April 15")
        assert "time" in response2.lower(), "System should ask for time after recognizing the date"
        assert "temp_booking_date" in nlp.user_context, "temp_booking_date should be in user_context"
        date_obj = nlp.user_context["temp_booking_date"]
        assert date_obj.month == 4, f"Expected month 4, got {date_obj.month}"
        assert date_obj.day == 15, f"Expected day 15, got {date_obj.day}"

    def test_combined_date_time_input(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        print(f"\nResponse 1: {response1}")
        assert "date" in response1.lower(), "System should ask for date"
        response2 = nlp.process_input("Book a plumber for April 15 at 3:16 PM")
        print(f"\nResponse 2: {response2}")
        print(f"User context: {nlp.user_context}")
        if "time" in response2.lower():
            response3 = nlp.process_input("April 15 at 3:16 PM")
            print(f"\nResponse 3: {response3}")
            print(f"User context: {nlp.user_context}")
            assert "available" in response3.lower() or "select" in response3.lower(
            ), "System should show available technicians"
        else:
            assert "available" in response2.lower() or "select" in response2.lower(
            ), "System should show available technicians"
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.month == 4, f"Expected month 4, got {time_dt.month}"
        assert time_dt.day == 15, f"Expected day 15, got {time_dt.day}"
        assert time_dt.hour == 15, f"Expected hour 15, got {time_dt.hour}"
        assert time_dt.minute == 16, f"Expected minute 16, got {time_dt.minute}"

    def test_ampm_clarification_for_5_to_7(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        assert "date" in response1.lower(), "System should ask for date"
        response2 = nlp.process_input("tomorrow")
        assert "time" in response2.lower(), "System should ask for time"
        response3 = nlp.process_input("6:00")
        assert "AM or PM" in response3, "System should ask for AM/PM clarification"
        assert nlp.user_context.get("awaiting_ampm", False), "System should be awaiting AM/PM"
        response4 = nlp.process_input("PM")
        assert "available" in response4.lower(), "System should show available technicians"
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.hour == 18, f"Expected hour 18, got {time_dt.hour}"
        assert time_dt.minute == 0, f"Expected minute 0, got {time_dt.minute}"

    @pytest.mark.parametrize("time_input", ["5:00", "6:00", "7:00"])
    def test_time_without_ampm_pattern(self, time_input):
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
    def test_ampm_response_processing(self, time_input, am_pm, expected_hour):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        nlp.process_input(time_input)
        assert nlp.user_context.get(
            "awaiting_ampm", False), f"System should be awaiting AM/PM for {time_input}"
        nlp.process_input(am_pm)
        assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
        time_dt = nlp.user_context["temp_booking_time"]
        assert time_dt.hour == expected_hour, f"Expected hour {expected_hour}, got {time_dt.hour}"
        minute = int(time_input.split(":")[1])
        assert time_dt.minute == minute, f"Expected minute {minute}, got {time_dt.minute}"
