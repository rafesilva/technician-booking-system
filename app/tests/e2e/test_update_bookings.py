from app.tests.utils import (
    send_request, reset_session, create_test_booking, reset_database,
    print_header, print_test_result, print_step, print_user_message,
    print_system_response, generate_session_id, is_date_prompt, is_time_prompt,
    is_technician_prompt, is_booking_confirmed, is_conflict_detected, is_error_message,
    get_all_bookings
)
from app.db.database import get_all_bookings, get_booking_by_id, update_booking
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
import sys
import uuid
import re
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
SESSION_ID = generate_session_id("test_update")


def create_booking_with_retry(session_id, specialty="plumber", date="January 15, 2031"):
    times_to_try = ["9 am", "10 am", "11 am", "1 pm", "2 pm", "3 pm", "4 pm", "5 pm"]
    for time_slot in times_to_try:
        reset_session(session_id)
        response = send_request(session_id, f"I need a {specialty}")
        response = send_request(session_id, date)
        response = send_request(session_id, time_slot)
        if is_conflict_detected(response):
            print(f"Conflict detected for {time_slot}, trying another time")
            continue
        if is_technician_prompt(response):
            response = send_request(session_id, "1")
        if is_booking_confirmed(response):
            print(f"Successfully booked at {time_slot}")
            return response
    return response


def get_existing_booking_id():
    try:
        reset_database()
        bookings = get_all_bookings()
        if bookings and len(bookings) > 0:
            return bookings[0].get('id')
    except Exception as e:
        print(f"Error getting existing booking ID: {str(e)}")
    return None


def test_update_commands():
    print_header("Testing Update Command Detection")
    print("Resetting database")
    reset_database()
    booking_id = get_existing_booking_id()
    if not booking_id:
        print("No existing bookings found. Skipping the test.")
        return False
    print(f"Using existing booking ID: {booking_id}")
    session_id = generate_session_id()
    reset_session(session_id)
    start_time = time.time()
    update_commands = [
        "update my booking",
        "change my appointment",
        "reschedule booking",
        f"update booking {booking_id}",
        "I want to change my booking",
        "I need to reschedule my appointment"
    ]
    commands_recognized = 0
    for i, command in enumerate(update_commands, 1):
        print_step(i, f"Testing update command: '{command}'")
        test_session_id = generate_session_id()
        reset_session(test_session_id)
        command_start_time = time.time()
        response = send_request(test_session_id, command)
        print_system_response(response)
        is_recognized = ("update" in response.lower() or
                         "change" in response.lower() or
                         "reschedule" in response.lower() or
                         "which booking" in response.lower() or
                         "booking id" in response.lower())
        print_test_result(
            f"System recognizes '{command}' as update request",
            is_recognized)
        print(f"Step completed in {time.time() - command_start_time:.2f} seconds")
        if is_recognized:
            commands_recognized += 1
    success_rate = commands_recognized / len(update_commands) if update_commands else 0
    print(
        f"\nUpdate commands recognized: {commands_recognized}/{len(update_commands)} ({success_rate:.0%})")
    assert success_rate >= 0.3, f"At least 30% of update commands should be recognized, but only {success_rate:.0%} were successful"
    test_duration = time.time() - start_time
    print(f"Test completed in {test_duration:.2f} seconds")
    return True


def test_update_booking_technician():
    print_header("Testing Update Booking Technician")
    reset_database()
    session_id = generate_session_id("test_technician_update")
    print_step(1, "Creating a new booking")
    response = create_test_booking(session_id, "plumber", "tomorrow", "2 pm")
    booking_id_match = re.search(r'booking ID is (\d+)', response)
    if not booking_id_match:
        print_test_result("Couldn't extract booking ID from confirmation", False)
        return False
    booking_id = int(booking_id_match.group(1))
    print(f"Successfully created booking with ID: {booking_id}")
    original_booking = get_booking_by_id(booking_id)
    if not original_booking:
        print_test_result("Couldn't retrieve original booking", False)
        return False
    original_technician = original_booking.technician_name
    print(f"Original technician: {original_technician}")
    print_step(2, "Updating booking with a new technician")
    reset_session(session_id)
    update_result = update_booking(booking_id, {"technician_name": "John Pipe"})
    updated_booking = get_booking_by_id(booking_id)
    if not updated_booking:
        print_test_result("Couldn't retrieve updated booking", False)
        return False
    new_technician = updated_booking.technician_name
    print(f"New technician: {new_technician}")
    technician_changed = original_technician != new_technician
    print_test_result("Technician was changed in the database", technician_changed)
    return technician_changed


def test_update_error_cases():
    print_header("Testing Update Booking Error Cases")
    reset_database()
    session_id = generate_session_id("test_update_errors")
    print_step(1, "Creating a new booking")
    response = create_test_booking(session_id, "electrician", "October 16", "6 pm")
    booking_id_match = re.search(r'booking ID is (\d+)', response)
    if not booking_id_match:
        print_test_result("Couldn't extract booking ID from confirmation", False)
        return False
    booking_id = int(booking_id_match.group(1))
    print(f"Successfully created booking with ID: {booking_id}")
    print_step(2, "Testing date update to April 15")
    reset_session(session_id)
    response = send_request(session_id, f"update booking {booking_id}")
    print(f"Update command response: {response}")
    response = send_request(session_id, "April 15")
    print(f"April 15 date response: {response}")
    date_understood = "april 15" in response.lower()
    print_test_result("April 15 date was correctly parsed", date_understood)
    response = send_request(session_id, "3:11 am")
    print(f"Time response: {response}")
    update_successful = "updated" in response.lower() and "april 15" in response.lower()
    print_test_result("Booking date updated successfully to April 15", update_successful)
    updated_booking = get_booking_by_id(booking_id)
    if not updated_booking:
        print_test_result("Couldn't retrieve updated booking", False)
        return False
    updated_date = updated_booking.booking_time
    date_changed = updated_date.month == 4 and updated_date.day == 15
    time_changed = updated_date.hour == 3 and updated_date.minute == 11
    print_test_result("Date was actually changed to April 15 in the database", date_changed)
    print_test_result("Time was actually changed to 3:11 AM in the database", time_changed)
    print_step(3, "Testing technician update confirmation message")
    reset_session(session_id)
    booking = get_booking_by_id(booking_id)
    if not booking:
        print_test_result("Couldn't retrieve booking", False)
        return False
    from app.db.database import update_booking
    from app.nlp.constants import MESSAGES, DATE_TIME_FORMATS
    update_booking(booking_id, {"technician_name": "Emma Volt"})
    updated_booking = get_booking_by_id(booking_id)
    correct_tech = updated_booking.technician_name == "Emma Volt"
    correct_date = updated_booking.booking_time.month == 4 and updated_booking.booking_time.day == 15
    correct_time = updated_booking.booking_time.hour == 3 and updated_booking.booking_time.minute == 11
    print_test_result("Technician was updated to Emma Volt", correct_tech)
    print_test_result("Date remains April 15", correct_date)
    print_test_result("Time remains 3:11 AM", correct_time)
    print_step(4, "Testing 'Cancel a booking' command")
    reset_session(session_id)
    response = send_request(session_id, "Cancel a booking")
    print(f"Capitalized cancel booking response: {response}")
    asks_for_booking_id = "which booking" in response.lower() or "booking id" in response.lower()
    not_process_cancelled = "process cancelled" not in response.lower()
    print_test_result("System asks for booking ID with capitalized command", asks_for_booking_id)
    print_test_result(
        "System doesn't respond with 'Process cancelled' for capitalized command",
        not_process_cancelled)
    reset_session(session_id)
    lowercase_response = send_request(session_id, "cancel a booking")
    print(f"Lowercase cancel booking response: {lowercase_response}")
    lowercase_asks_for_id = "which booking" in lowercase_response.lower(
    ) or "booking id" in lowercase_response.lower()
    lowercase_not_cancelled = "process cancelled" not in lowercase_response.lower()
    print_test_result("System asks for booking ID with lowercase command", lowercase_asks_for_id)
    print_test_result(
        "System doesn't respond with 'Process cancelled' for lowercase command",
        lowercase_not_cancelled)
    return date_understood and update_successful and date_changed and time_changed and correct_tech and correct_date and correct_time and asks_for_booking_id and not_process_cancelled and lowercase_asks_for_id and lowercase_not_cancelled


def test_update_booking_interruption():
    print_header("Testing Update Booking Interruption")
    reset_database()
    session_id = generate_session_id("test_update_interruption")
    print_step(1, "Creating a new booking")
    response = create_test_booking(session_id, "plumber", "tomorrow", "2 pm")
    print_step(2, "Starting update process")
    reset_session(session_id)
    response = send_request(session_id, "Update a booking")
    print(f"Update request response: {response}")
    is_asking_for_id = "which booking" in response.lower() or "booking id" in response.lower()
    print_test_result("System asks for booking ID", is_asking_for_id)
    print_step(3, "Testing greeting interruption")
    response = send_request(session_id, "Hello")
    print(f"Greeting response: {response}")
    handles_greeting = "hello" in response.lower(
    ) or "hi" in response.lower() or "how can i assist" in response.lower()
    print_test_result("System recognizes greeting and exits update mode", handles_greeting)
    print_step(4, "Testing starting a new booking from update mode")
    reset_session(session_id)
    response = send_request(session_id, "Update a booking")
    response = send_request(session_id, "I need a plumber")
    print(f"New booking response: {response}")
    is_new_booking = "what date" in response.lower() or "when would you like" in response.lower()
    print_test_result("System starts new booking flow", is_new_booking)
    print_step(5, "Testing checking bookings from update mode")
    reset_session(session_id)
    response = send_request(session_id, "Update a booking")
    response = send_request(session_id, "Show my bookings")
    print(f"Show bookings response: {response}")
    is_showing_bookings = "booking" in response.lower() and "#" in response
    print_test_result("System shows bookings list", is_showing_bookings)
    print_step(6, "Testing switching from update to cancel mode")
    reset_session(session_id)
    response = send_request(session_id, "Update a booking")
    response = send_request(session_id, "Cancel a booking")
    print(f"Cancel from update response: {response}")
    is_switching_to_cancel = "cancel" in response.lower() and (
        "which booking" in response.lower() or "booking id" in response.lower())
    print_test_result("System switches from update to cancel mode", is_switching_to_cancel)
    return is_asking_for_id and handles_greeting and is_new_booking and is_showing_bookings and is_switching_to_cancel


if __name__ == "__main__":
    test_update_commands()
    test_update_booking_technician()
    test_update_error_cases()
    test_update_booking_interruption()
