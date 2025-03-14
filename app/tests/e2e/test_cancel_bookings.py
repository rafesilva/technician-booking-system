from app.tests.utils import (
    send_request, reset_session, create_test_booking, reset_database,
    print_header, print_test_result, print_step, print_user_message,
    print_system_response, generate_session_id, is_booking_confirmed
)
from app.db.database import get_all_bookings, get_booking_by_id, delete_booking
from app.nlp.utils.intent_recognizer import IntentRecognizer
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
import sys
import uuid
import re
import time
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
SESSION_ID = generate_session_id("test_cancel")
intent_recognizer = IntentRecognizer()


def test_cancel_commands():
    print_header("Testing Cancellation Command Detection")
    print("Resetting database")
    reset_database()
    session_id = generate_session_id()
    reset_session(session_id)
    start_time = time.time()
    print_step(1, "Creating test booking")
    booking_id = create_test_booking(
        session_id,
        specialty="plumber",
        date="December 25, 2030",
        time="3 pm")
    assert booking_id, "Test booking should be created successfully"
    print_test_result("Create test booking", True)
    for list_command in ["check bookings",
                         "show bookings", "list bookings", "my bookings"]:
        response = send_request(session_id, list_command)
        if "ID:" in response or "ID: " in response or "bookings" in response.lower():
            print(f"Successfully listed bookings with command: '{list_command}'")
            break
    print_system_response(response)
    cancel_commands = [
        "cancel my booking",
        "cancel appointment",
        "cancel booking",
        f"cancel booking {booking_id}",
        "I want to cancel",
        "I need to cancel my appointment"
    ]
    commands_recognized = 0
    for i, command in enumerate(cancel_commands, 1):
        print_step(i+1, f"Testing cancel command: '{command}'")
        test_session_id = generate_session_id()
        reset_session(test_session_id)
        test_booking_id = create_test_booking(
            test_session_id,
            specialty="plumber",
            date="December 25, 2030",
            time="3 pm")
        command_start_time = time.time()
        response = send_request(test_session_id, command)
        print_system_response(response)
        is_recognized = ("cancel" in response.lower() or
                         "which booking" in response.lower() or
                         "booking id" in response.lower() or
                         "has been cancelled" in response.lower() or
                         "process cancelled" in response.lower())
        print_test_result(
            f"System recognizes '{command}' as cancellation",
            is_recognized)
        print(f"Step completed in {time.time() - command_start_time:.2f} seconds")
        if is_recognized:
            commands_recognized += 1
    success_rate = commands_recognized / len(cancel_commands)
    print(
        f"\nCancellation commands recognized: {commands_recognized}/{len(cancel_commands)} ({success_rate:.0%})")
    assert success_rate >= 0.5, f"At least 50% of cancellation commands should be recognized, but only {success_rate:.0%} were successful"
    test_duration = time.time() - start_time
    print(f"Test completed in {test_duration:.2f} seconds")
    return True


def test_cancel_booking_interruption():
    print_header("Testing Cancel Booking Interruption")
    reset_database()
    session_id = generate_session_id("test_cancel_interruption")
    print_step(1, "Creating a new booking")
    response = create_test_booking(session_id, "plumber", "tomorrow", "2 pm")
    print_step(2, "Starting cancellation process")
    reset_session(session_id)
    response = send_request(session_id, "Cancel a booking")
    print(f"Cancel request response: {response}")
    is_asking_for_id = "which booking" in response.lower() or "booking id" in response.lower()
    print_test_result("System asks for booking ID", is_asking_for_id)
    print_step(3, "Testing greeting interruption")
    response = send_request(session_id, "Hello")
    print(f"Greeting response: {response}")
    handles_greeting = "hello" in response.lower(
    ) or "hi" in response.lower() or "how can i assist" in response.lower()
    print_test_result("System recognizes greeting and exits cancel mode", handles_greeting)
    print_step(4, "Testing starting a new booking from cancel mode")
    reset_session(session_id)
    response = send_request(session_id, "Cancel a booking")
    response = send_request(session_id, "I need a plumber")
    print(f"New booking response: {response}")
    is_new_booking = "what date" in response.lower() or "when would you like" in response.lower()
    print_test_result("System starts new booking flow", is_new_booking)
    print_step(5, "Testing checking bookings from cancel mode")
    reset_session(session_id)
    response = send_request(session_id, "Cancel a booking")
    response = send_request(session_id, "Show my bookings")
    print(f"Show bookings response: {response}")
    is_showing_bookings = "booking" in response.lower() and "#" in response
    print_test_result("System shows bookings list", is_showing_bookings)
    return is_asking_for_id and handles_greeting and is_new_booking and is_showing_bookings


def test_cancel_booking_id():
    print_header("Testing Cancel Booking with ID")
    reset_database()
    session_id = generate_session_id("test_cancel_id")
    print_step(1, "Creating a new booking")
    response = create_test_booking(session_id, "plumber", "tomorrow", "2 pm")
    booking_id_match = re.search(r'booking ID is (\d+)', response)
    if not booking_id_match:
        print_test_result("Couldn't extract booking ID from confirmation", False)
        return False
    booking_id = int(booking_id_match.group(1))
    print(f"Successfully created booking with ID: {booking_id}")
    print_step(2, "Cancelling booking with ID")
    reset_session(session_id)
    response = send_request(session_id, f"Cancel booking {booking_id}")
    print(f"Cancel response: {response}")
    is_cancelled = "cancelled" in response.lower()
    print_test_result("Booking was successfully cancelled", is_cancelled)
    booking = get_booking_by_id(booking_id)
    is_deleted = booking is None
    print_test_result("Booking was actually deleted from the database", is_deleted)
    return is_cancelled and is_deleted


if __name__ == "__main__":
    test_cancel_commands()
    test_cancel_booking_id()
    test_cancel_booking_interruption()
