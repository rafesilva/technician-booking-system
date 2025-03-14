from app.tests.utils import (
    send_request, reset_session, create_test_booking, reset_database,
    print_header, print_test_result, print_step, print_user_message,
    print_system_response, generate_session_id, is_date_prompt, is_time_prompt,
    is_technician_prompt, is_booking_confirmed, is_conflict_detected, is_error_message
)
from app.db.database import get_all_bookings, get_booking_by_id
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
import sys
import uuid
import re
import time
from datetime import datetime, timedelta
import unittest
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
SESSION_ID = generate_session_id("test_create")
MAX_WAIT_TIME = 10


def test_basic_booking_creation():
    print_header("Testing Basic Booking Creation")
    print("Resetting database")
    reset_database()
    session_id = generate_session_id()
    reset_session(session_id)
    print_step(1, "Requesting a plumber")
    start_time = time.time()
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    print(f"Step completed in {time.time() - start_time:.2f} seconds")
    assert is_date_prompt(response), "System should ask for a date"
    print_step(2, "Providing a date")
    future_date = "December 25, 2030"
    start_time = time.time()
    response = send_request(session_id, future_date)
    print_system_response(response)
    print(f"Step completed in {time.time() - start_time:.2f} seconds")
    assert is_time_prompt(response), "System should ask for a time"
    print_step(3, "Providing a time")
    times_to_try = ["9 am", "10 am", "11 am", "1 pm", "2 pm", "3 pm", "4 pm", "5 pm"]
    booking_successful = False
    for time_slot in times_to_try:
        start_time = time.time()
        response = send_request(session_id, time_slot)
        print_system_response(response)
        print(f"Tried time: {time_slot}")
        if is_conflict_detected(response):
            print(f"Conflict detected for {time_slot}, trying another time")
            continue
        if is_technician_prompt(response):
            print("Selecting first technician")
            response = send_request(session_id, "1")
        print_system_response(response)
        if is_booking_confirmed(response):
            booking_successful = True
            print(f"Successfully booked at {time_slot}")
            booking_id_match = re.search(r'booking ID is (\d+)', response)
            if booking_id_match:
                booking_id = booking_id_match.group(1)
                print(f"Booking ID: {booking_id}")
            break
    assert booking_successful, "Booking should be successful with at least one of the time slots"
    print_test_result("Basic booking creation", booking_successful)
    return True


if __name__ == "__main__":
    test_basic_booking_creation()
