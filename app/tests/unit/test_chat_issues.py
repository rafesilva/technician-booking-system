import pytest
from datetime import datetime, timedelta
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser
from app.db.database import reset_database, create_booking
from app.models.booking import BookingCreate
import re


class TestChatIssues:
    def test_month_day_date_parsing(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        response1 = nlp.process_input("I need a plumber")
        assert "date" in response1.lower(), "System should ask for date"
        response2 = nlp.process_input("July 7")
        assert "time" in response2.lower(), "System should accept July 7 as a valid date and ask for time"
        assert "temp_booking_date" in nlp.user_context, "temp_booking_date should be in user_context"
        date_obj = nlp.user_context["temp_booking_date"]
        assert date_obj.month == 7, f"Expected month 7, got {date_obj.month}"
        assert date_obj.day == 7, f"Expected day 7, got {date_obj.day}"

    def test_time_confirmation_accuracy(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response = nlp.process_input("3")
        if "AM or PM" in response:
            assert nlp.user_context.get("awaiting_ampm", False), "System should be awaiting AM/PM"
            assert nlp.user_context.get("temp_booking_hour") == 3, "Hour should be set to 3"
            response = nlp.process_input("PM")
            assert "3:00 PM" in response or "3 PM" in response, "Response should confirm 3:00 PM"
            assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
            time_obj = nlp.user_context["temp_booking_time"]
            assert time_obj.hour == 15, f"Expected hour 15, got {time_obj.hour}"
            assert time_obj.minute == 0, f"Expected minute 0, got {time_obj.minute}"
        else:
            assert "3:00 PM" in response or "3 PM" in response, "Response should include 3:00 PM"
            assert "temp_booking_time" in nlp.user_context, "temp_booking_time should be in user_context"
            time_obj = nlp.user_context["temp_booking_time"]
            assert time_obj.hour == 15, f"Expected hour 15, got {time_obj.hour}"
            assert time_obj.minute == 0, f"Expected minute 0, got {time_obj.minute}"

    def test_calendar_date_clarification(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        response = nlp.process_input("Monday")
        assert "time" in response.lower(), "System should ask for time after accepting the date"
        assert "temp_booking_date" in nlp.user_context, "temp_booking_date should be in user_context"
        date_obj = nlp.user_context["temp_booking_date"]
        today = datetime.now().date()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        expected_date = today + timedelta(days=days_until_monday)
        assert date_obj.weekday() == 0, f"Expected weekday 0 (Monday), got {date_obj.weekday()}"
        assert date_obj.month == expected_date.month, f"Month should match expected date"
        assert date_obj.day == expected_date.day, f"Day should match expected date"

    def test_time_slot_availability_suggestions(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        tomorrow = datetime.now() + timedelta(days=1)
        booking_time = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 15, 20)
        booking_create = BookingCreate(
            technician_name="Test Technician",
            specialty="Plumbing",
            booking_time=booking_time
        )
        create_booking(booking_create)
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response = nlp.process_input("3:20 PM")
        assert "already a booking" in response.lower(),            "System should detect booking conflict"
        assert "different time" in response.lower(),            "System should ask for an alternative time"
        assert "alternative times available" in response.lower() or "would you like to schedule" in response.lower(
        ),            "System should suggest alternative times or ask to schedule at a different time"
        assert nlp.user_context.get(
            "conflict_detected", False),            "Conflict flag should be set in user context"

    def test_yes_response_after_conflict(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        tomorrow = datetime.now() + timedelta(days=1)
        booking_time = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 15, 20)
        booking_create = BookingCreate(
            technician_name="Test Technician",
            specialty="Plumbing",
            booking_time=booking_time
        )
        create_booking(booking_create)
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        nlp.process_input("3:20 PM")
        response = nlp.process_input("yes")
        assert "time" in response.lower() or "when would you like" in response.lower(
        ),            "System should prompt for a new time or restart the booking flow"
        assert not nlp.user_context.get("conflict_detected", False) or nlp.user_context.get(
            "awaiting_time", False),            "Conflict flag should be cleared or awaiting_time should be set after 'yes' response"

    def test_none_specialty_display(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        tomorrow = datetime.now() + timedelta(days=1)
        booking_time = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 15, 10)
        booking_create = BookingCreate(
            technician_name="Test Technician",
            specialty="Plumbing",
            booking_time=booking_time
        )
        create_booking(booking_create)
        conflict_response = nlp.process_input("3:10 PM")
        assert "already a booking" in conflict_response.lower(), "System should detect booking conflict"
        different_time_response = nlp.process_input("yes")
        assert "None appointment" not in different_time_response, "System should not display 'None' in place of the specialty"
        assert "plumber" in different_time_response.lower() or "technician" in different_time_response.lower(
        ),            "System should display the correct specialty or a default term"

    def test_datetime_format_consistency(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        time_responses = []
        response1 = nlp.process_input("3:10 PM")
        time_responses.append(response1)
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response2 = nlp.process_input("15:17")
        time_responses.append(response2)
        for response in time_responses:
            if "technician" in response.lower() or "available" in response.lower():
                format_check = re.findall(r'(\d{1,2}):(\d{2})\s*(AM|PM)', response)
                format_check_24hr = re.findall(r'(\d{2}):(\d{2})', response)
                if format_check:
                    hour, minute, ampm = format_check[0]
                    assert not hour.startswith(
                        '0'), f"Hour should not have leading zero in 12-hour format: {hour}:{minute} {ampm}"
                    assert 1 <= int(
                        hour) <= 12, f"Hour should be between 1-12 in 12-hour format: {hour}"
                if format_check_24hr and not format_check:
                    assert False, f"Found 24-hour format time without AM/PM: {format_check_24hr[0]}"

    def test_unusual_time_format_validation(self):
        reset_database()
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response1 = nlp.process_input("3:10")
        if "AM or PM" in response1:
            assert nlp.user_context.get(
                "awaiting_ampm", False), "System should be awaiting AM/PM clarification"
        else:
            assert "temp_booking_time" in nlp.user_context, "Should have set a time in the context"
        nlp = NaturalLanguageProcessor()
        nlp.process_input("I need a plumber")
        nlp.process_input("tomorrow")
        response2 = nlp.process_input("5")
        if "AM or PM" in response2:
            assert nlp.user_context.get(
                "awaiting_ampm", False), "System should be awaiting AM/PM clarification"
        else:
            assert "temp_booking_time" in nlp.user_context, "Should have set a time in the context"
        await_ampm1 = "AM or PM" in response1
        await_ampm2 = "AM or PM" in response2
        assert await_ampm1 == await_ampm2, "System should be consistent in requiring AM/PM clarification"
