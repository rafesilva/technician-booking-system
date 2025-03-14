from app.models.booking import BookingCreate
from app.db.database import reset_database, create_booking
from app.nlp.processor import NaturalLanguageProcessor
from app.nlp.utils.date_time_parser import DateTimeParser
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_specific_time_inputs():
    parser = DateTimeParser()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    test_inputs = [
        "3:14",
        "3:14 PM",
        "3:14 in the afternoon",
        "3:14 afternoon",
        "3:15",
        "3:15 PM",
        "5:30",
        "5:30 PM",
        "10:45 AM",
        "12:30 PM"
    ]
    print("\n=== Testing Specific Time Inputs ===")
    for input_text in test_inputs:
        result = parser.parse_time(input_text, today)
        if result:
            time_dt, time_desc = result
            if isinstance(time_dt, datetime):
                print(
                    f"Input: '{input_text}' -> Parsed: {time_dt.hour}:{time_dt.minute:02d} ({time_desc})")
            elif isinstance(time_dt, tuple) and len(time_dt) == 2:
                hour, minute = time_dt
                print(f"Input: '{input_text}' -> Parsed: {hour}:{minute:02d} ({time_desc})")
            else:
                print(f"Input: '{input_text}' -> Parsed: {time_dt} ({time_desc})")
        else:
            print(f"Input: '{input_text}' -> Failed to parse")


def test_booking_with_specific_times():
    nlp = NaturalLanguageProcessor()
    print("\n=== Testing Booking Flow with Specific Times ===")
    response = nlp.process_input("Hello")
    print(f"User: Hello")
    print(f"System: {response}")
    response = nlp.process_input("I need to book an electrician")
    print(f"User: I need to book an electrician")
    print(f"System: {response}")
    response = nlp.process_input("tomorrow")
    print(f"User: tomorrow")
    print(f"System: {response}")
    response = nlp.process_input("3:14 PM")
    print(f"User: 3:14 PM")
    print(f"System: {response}")
    nlp2 = NaturalLanguageProcessor()
    response = nlp2.process_input("Hello")
    response = nlp2.process_input("I need to book a plumber")
    response = nlp2.process_input("tomorrow")
    response = nlp2.process_input("3:15")
    print(f"User: 3:15")
    print(f"System: {response}")


def test_technician_selection():
    print("\n" + "="*70)
    print("TESTING TECHNICIAN SELECTION BY NUMBER")
    print("="*70)
    nlp = NaturalLanguageProcessor()
    print("\nStep 1: Request a plumber")
    response = nlp.process_input("I need a plumber")
    print(f"Response: {response}")
    print("\nStep 2: Provide a date")
    response = nlp.process_input("April 15")
    print(f"Response: {response}")
    print("\nStep 3: Provide a time with specific minutes")
    response = nlp.process_input("3:13 PM")
    print(f"Response: {response}")
    if "available" in response and "Please select a technician" in response:
        print("✅ Successfully entered technician selection mode")
        print("\nStep 4: Select a technician by number")
        response = nlp.process_input("1")
        print(f"Response: {response}")
        if "confirmed" in response:
            print("✅ Successfully selected technician by number")
        else:
            print("❌ Failed to select technician by number")
    else:
        print("❌ Failed to enter technician selection mode")


def test_technician_selection_by_name():
    print("\n" + "="*70)
    print("TESTING TECHNICIAN SELECTION BY NAME")
    print("="*70)
    nlp = NaturalLanguageProcessor()
    print("\nStep 1: Request a plumber")
    response = nlp.process_input("I need a plumber")
    print(f"Response: {response}")
    print("\nStep 2: Provide a date")
    response = nlp.process_input("April 16")
    print(f"Response: {response}")
    print("\nStep 3: Provide a time with specific minutes")
    response = nlp.process_input("4:13 PM")
    print(f"Response: {response}")
    if "available" in response and "Please select a technician" in response:
        print("✅ Successfully entered technician selection mode")
        print("\nStep 4: Select a technician by name")
        response = nlp.process_input("Nicolas")
        print(f"Response: {response}")
        if "confirmed" in response:
            print("✅ Successfully selected technician by name")
        else:
            print("❌ Failed to select technician by name")
    else:
        print("❌ Failed to enter technician selection mode")


if __name__ == "__main__":
    print("Starting manual tests...")
    test_specific_time_inputs()
    test_booking_with_specific_times()
    test_technician_selection()
    test_technician_selection_by_name()
    print("\nAll manual tests completed!")
