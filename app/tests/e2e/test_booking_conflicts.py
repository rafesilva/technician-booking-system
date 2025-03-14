from app.tests.utils import (
    send_request, reset_session, reset_database, print_header,
    print_test_result, print_step, print_user_message,
    print_system_response, generate_session_id, is_conflict_detected,
    is_booking_confirmed, is_technician_prompt
)
import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def test_overlapping_bookings():
    print_header("Testing Overlapping Booking Scenarios")
    session_id = generate_session_id("test_conflicts")
    reset_database()
    print_step("First booking", "Making first booking at 2 PM")
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "2 PM")
    print_system_response(response)
    if is_technician_prompt(response):
        response = send_request(session_id, "1")
        print_system_response(response)
    first_booking_successful = is_booking_confirmed(response)
    print_test_result("First booking at 2 PM", first_booking_successful)
    assert first_booking_successful, "First booking should succeed"
    print_step(
        "Same technician overlap",
        "Attempting overlapping booking at 2:30 PM with same technician")
    reset_session(session_id)
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "2:30 PM")
    print_system_response(response)
    conflict_detected = is_conflict_detected(response)
    print_test_result("Conflict detected for overlapping booking", conflict_detected)
    print_step("Different technician overlap",
               "Attempting overlapping booking at 2:30 PM with different technician")
    reset_session(session_id)
    response = send_request(session_id, "I need an electrician")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "2:30 PM")
    print_system_response(response)
    if is_technician_prompt(response):
        response = send_request(session_id, "1")
        print_system_response(response)
    different_tech_booking_successful = is_booking_confirmed(response)
    print_test_result(
        "Different technician booking at overlapping time",
        different_tech_booking_successful)
    print_step(
        "Within hour window",
        "Attempting booking at 3:15 PM (within first booking's hour)")
    reset_session(session_id)
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "3:15 PM")
    print_system_response(response)
    conflict_detected = is_conflict_detected(response)
    print_test_result(
        "Conflict detected for booking within hour window",
        conflict_detected)
    print_step(
        "Outside hour window",
        "Attempting booking at 3:30 PM (outside first booking's hour)")
    reset_session(session_id)
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "3:30 PM")
    print_system_response(response)
    if is_technician_prompt(response):
        response = send_request(session_id, "1")
        print_system_response(response)
    sequential_booking_successful = is_booking_confirmed(response)
    print_test_result(
        "Sequential booking after one hour",
        sequential_booking_successful)
    assert sequential_booking_successful, "Should allow booking after one hour window"


def test_edge_case_conflicts():
    print_header("Testing Edge Case Conflict Scenarios")
    session_id = generate_session_id("test_edge_conflicts")
    reset_database()
    print_step("Late night booking", "Making booking at 11:45 PM")
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    response = send_request(session_id, "11:45 PM")
    print_system_response(response)
    if is_technician_prompt(response):
        response = send_request(session_id, "1")
        print_system_response(response)
    late_booking_successful = is_booking_confirmed(response)
    print_test_result("Late night booking at 11:45 PM", late_booking_successful)
    assert late_booking_successful, "Should allow booking at 11:45 PM"
    print_step("Early morning booking", "Attempting booking at 12:15 AM next day")
    reset_session(session_id)
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    response = send_request(session_id, "day after tomorrow")
    print_system_response(response)
    response = send_request(session_id, "12:15 AM")
    print_system_response(response)
    if is_technician_prompt(response):
        response = send_request(session_id, "1")
        print_system_response(response)
    midnight_booking_successful = is_booking_confirmed(response)
    print_test_result("Early morning booking at 12:15 AM", midnight_booking_successful)
    assert midnight_booking_successful, "Should allow booking at 12:15 AM next day"


if __name__ == "__main__":
    test_overlapping_bookings()
    test_edge_case_conflicts()
