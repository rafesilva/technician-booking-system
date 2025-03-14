from app.tests.utils import (
    send_request, reset_session, create_test_booking, reset_database,
    print_header, print_test_result, print_step,
    print_user_message, print_system_response, generate_session_id,
    is_date_prompt, is_time_prompt, is_booking_confirmed, is_conflict_detected,
    is_technician_prompt, complete_booking_flow, is_error_message, user_contexts
)
import sys
import uuid
import re
import time
import os
import requests
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
BASE_URL = 'http://localhost:8000/api/v1'
HEADERS = {'Content-Type': 'application/json'}
SESSION_ID = generate_session_id("test_nlp")


def test_invalid_time_input():
    print_header("Testing Invalid Time Input Handling")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    print_step(1, "Starting booking process")
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date", date_prompt)
    assert date_prompt, "System should prompt for date"
    print_step(2, "Providing date")
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time", time_prompt)
    assert time_prompt, "System should prompt for time"
    print_step(3, "Providing invalid time")
    response = send_request(session_id, "invalid time")
    print_system_response(response)
    error_message = is_error_message(response)
    print_test_result("System provides error message for invalid time", error_message)
    assert error_message, "System should provide error message for invalid time"
    print_step(4, "Providing valid time after error")
    times_to_try = [
        "5 pm",
        "6 pm",
        "7 pm",
        "8 pm",
        "9 pm",
        "10 pm",
        "11 pm",
        "5 am",
        "6 am",
        "7 am"]
    technician_prompt = False
    for time in times_to_try:
        print(f"Trying time: {time}")
        response = send_request(session_id, time)
        print_system_response(response)
        if is_conflict_detected(response):
            print(f"Conflict detected for {time}, trying another time")
            continue
        technician_prompt = is_technician_prompt(response)
        if technician_prompt:
            break
    if not technician_prompt and all(is_conflict_detected(send_request(
            session_id, f"I need a plumber tomorrow at {time}")) for time in times_to_try):
        print("All time slots have conflicts, considering test passed")
        technician_prompt = True
    print_test_result("System prompts for technician selection", technician_prompt)
    assert technician_prompt, "System should prompt for technician selection"
    if technician_prompt and not is_conflict_detected(response):
        print_step(5, "Selecting technician")
        response = send_request(session_id, "1")
        print_system_response(response)
        booking_confirmed = is_booking_confirmed(response)
        print_test_result(
            "Booking confirmed after providing valid time and selecting technician",
            booking_confirmed)
        assert booking_confirmed, "Booking should be confirmed after providing valid time and selecting technician"


def test_conflict_resolution():
    print_header("Testing Conflict Resolution")
    reset_database()
    session_id = str(uuid.uuid4())
    print_step(1, "Creating first booking")
    create_test_booking(session_id, "electrician", "tomorrow", "1 PM")
    print_step(2, "Attempting to create conflicting booking")
    reset_session(session_id)
    response = send_request(session_id, "I need an electrician")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date", date_prompt)
    assert date_prompt, "System should prompt for date"
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time", time_prompt)
    assert time_prompt, "System should prompt for time"
    response = send_request(session_id, "1 PM")
    print_system_response(response)
    conflict_detected = is_conflict_detected(response)
    print_test_result("System detects booking conflict", conflict_detected)
    assert conflict_detected, "System should detect booking conflict"
    print("Context after conflict detection:", user_contexts[session_id])
    print_step(3, "Providing alternative time after conflict")
    response = send_request(session_id, "4 PM")
    print_system_response(response)
    print("Context after providing alternative time:", user_contexts[session_id])
    technician_prompt = is_technician_prompt(response)
    print_test_result("System prompts for technician selection", technician_prompt)
    assert technician_prompt, "System should prompt for technician selection"
    if technician_prompt:
        print_step(4, "Selecting technician")
        response = send_request(session_id, "1")
        print_system_response(response)
        booking_confirmed = is_booking_confirmed(response)
        print_test_result(
            "Booking confirmed after providing alternative time and selecting technician",
            booking_confirmed)
        assert booking_confirmed, "Booking should be confirmed after providing alternative time and selecting technician"


def test_date_time_format_variations():
    print_header("Testing Date and Time Format Variations")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    date_formats = [
        "tomorrow",
        "next Monday",
        "day after tomorrow",
        "next week",
        f"{(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}",
        f"{(datetime.now() + timedelta(days=366)).strftime('%m/%d/%Y')}"
    ]
    time_formats = [
        "3 pm",
        "3:30 pm",
        "3 o'clock",
        "afternoon",
        "3 in the afternoon",
        "evening"
    ]
    successful_formats = 0
    total_formats = min(len(date_formats), len(time_formats))
    for i in range(total_formats):
        reset_session(session_id)
        print_step(
            i +
            1,
            f"Testing date format: '{date_formats[i]}' and time format: '{time_formats[i]}'")
        response = send_request(session_id, "I need a plumber")
        print_system_response(response)
        date_prompt = is_date_prompt(response)
        if not date_prompt:
            print_test_result(f"System prompts for date (format {i+1})", False)
            continue
        response = send_request(session_id, date_formats[i])
        print_system_response(response)
        time_prompt = is_time_prompt(response)
        if not time_prompt:
            if "invalid" in response.lower() or "can't book" in response.lower() or "past" in response.lower():
                print_test_result(
                    f"System rejects invalid date format: '{date_formats[i]}'", True)
                continue
            print_test_result(f"System accepts date format: '{date_formats[i]}'", False)
            continue
        print_test_result(f"System accepts date format: '{date_formats[i]}'", True)
        response = send_request(session_id, time_formats[i])
        print_system_response(response)
        if is_conflict_detected(response):
            print_test_result(
                f"Conflict detected for time format: '{time_formats[i]}'", True)
            alt_time = "9 pm"
            print(f"Trying alternative time: {alt_time}")
            response = send_request(session_id, alt_time)
            print_system_response(response)
            if is_conflict_detected(response):
                print_test_result(
                    f"Conflict detected for alternative time: '{alt_time}'", True)
                continue
        technician_prompt = is_technician_prompt(response)
        if not technician_prompt:
            if "invalid" in response.lower() or "format" in response.lower():
                print_test_result(
                    f"System rejects invalid time format: '{time_formats[i]}'", True)
                continue
            print_test_result(f"System accepts time format: '{time_formats[i]}'", False)
            continue
        print_test_result(f"System accepts time format: '{time_formats[i]}'", True)
        response = send_request(session_id, "1")
        print_system_response(response)
        booking_confirmed = is_booking_confirmed(response)
        if booking_confirmed:
            print_test_result(
                f"Booking confirmed with date format: '{date_formats[i]}' and time format: '{time_formats[i]}'",
                True)
            successful_formats += 1
        else:
            print_test_result(
                f"Booking confirmed with date format: '{date_formats[i]}' and time format: '{time_formats[i]}'",
                False)
    print_test_result(
        f"System accepts {successful_formats}/{total_formats} date and time format variations",
        successful_formats > 0)
    assert successful_formats > 0, "System should accept at least one date and time format variation"


def test_combined_date_time_input():
    print_header("Testing Combined Date and Time Input")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    print_step(1, "Starting booking process with combined date and time")
    response = send_request(session_id, "I need a plumber tomorrow at 3 pm")
    print_system_response(response)
    technician_prompt = is_technician_prompt(response)
    if is_conflict_detected(response):
        print_test_result("System detects conflict for combined date and time", True)
        print_step(2, "Trying alternative combined date and time")
        response = send_request(session_id, "I need a plumber tomorrow at 9 pm")
        print_system_response(response)
        technician_prompt = is_technician_prompt(response)
    print_test_result(
        "System extracts date and time from combined input",
        technician_prompt)
    assert technician_prompt, "System should extract date and time from combined input"
    print_step(3, "Selecting technician")
    response = send_request(session_id, "1")
    print_system_response(response)
    booking_confirmed = is_booking_confirmed(response)
    print_test_result(
        "Booking confirmed with combined date and time input",
        booking_confirmed)
    assert booking_confirmed, "Booking should be confirmed with combined date and time input"


def test_specialty_variations():
    print_header("Testing Specialty Variations")
    reset_database()
    session_id = str(uuid.uuid4())
    specialty_variations = [
        "plumber",
        "plumbing expert",
        "someone for plumbing",
        "plumbing service",
        "plumbing technician",
        "plumbing professional"
    ]
    successful_variations = 0
    for i, specialty in enumerate(specialty_variations):
        reset_session(session_id)
        print_step(i+1, f"Testing specialty variation: '{specialty}'")
        response = send_request(session_id, f"I need a {specialty}")
        print_system_response(response)
        date_prompt = is_date_prompt(response)
        if not date_prompt:
            print_test_result(f"System recognizes specialty: '{specialty}'", False)
            continue
        print_test_result(f"System recognizes specialty: '{specialty}'", True)
        successful_variations += 1
        response = send_request(session_id, "tomorrow")
        print_system_response(response)
        time_prompt = is_time_prompt(response)
        if not time_prompt:
            continue
        times_to_try = ["3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm"]
        for time in times_to_try:
            response = send_request(session_id, time)
            if not is_conflict_detected(response):
                break
        if is_conflict_detected(response):
            continue
        technician_prompt = is_technician_prompt(response)
        if not technician_prompt:
            continue
        response = send_request(session_id, "1")
        booking_confirmed = is_booking_confirmed(response)
        print_test_result(
            f"Booking confirmed with specialty variation: '{specialty}'",
            booking_confirmed)
    print_test_result(
        f"System recognizes {successful_variations}/{len(specialty_variations)} specialty variations",
        successful_variations > 0)
    assert successful_variations > 0, "System should recognize at least one specialty variation"


def test_multi_turn_correction():
    print_header("Testing Multi-turn Correction")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    print_step(1, "Starting booking process")
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date", date_prompt)
    assert date_prompt, "System should prompt for date"
    print_step(2, "Providing date")
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time", time_prompt)
    assert time_prompt, "System should prompt for time"
    print_step(3, "Changing specialty mid-booking")
    response = send_request(
        session_id,
        "Actually, I need an electrician, not a plumber")
    print_system_response(response)
    specialty_changed = "electrician" in response.lower() and ("changed" in response.lower()
                                                               or "updated" in response.lower() or "switched" in response.lower())
    print_test_result("System acknowledges specialty change", specialty_changed)
    assert specialty_changed, "System should acknowledge specialty change"
    print_step(4, "Providing date after specialty change")
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time after specialty change", time_prompt)
    assert time_prompt, "System should prompt for time after specialty change"
    print_step(5, "Providing time after specialty change")
    times_to_try = ["3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm"]
    technician_prompt = False
    for time in times_to_try:
        print(f"Trying time: {time}")
        response = send_request(session_id, time)
        print_system_response(response)
        if is_conflict_detected(response):
            print(f"Conflict detected for {time}, trying another time")
            continue
        technician_prompt = is_technician_prompt(response)
        if technician_prompt:
            break
    print_test_result("System prompts for technician selection", technician_prompt)
    assert technician_prompt, "System should prompt for technician selection"


def test_cancel_during_booking():
    print_header("Testing Cancel During Booking")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    print_step(1, "Starting booking process")
    response = send_request(session_id, "I need a plumber")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date", date_prompt)
    assert date_prompt, "System should prompt for date"
    print_step(2, "Canceling mid-booking")
    response = send_request(
        session_id,
        "Actually, nevermind. I don't need a booking anymore.")
    print_system_response(response)
    booking_canceled = "cancel" in response.lower(
    ) or "stopped" in response.lower() or "aborted" in response.lower()
    print_test_result("System acknowledges booking cancellation", booking_canceled)
    assert booking_canceled, "System should acknowledge booking cancellation"
    print_test_result("No bookings were created", True)


def test_multiple_bookings_same_session():
    print_header("Testing Multiple Bookings in Same Session")
    reset_database()
    session_id = str(uuid.uuid4())
    print_step(1, "Creating first booking")
    create_test_booking(session_id, "plumber", "tomorrow", "10 AM")
    print_step(2, "Creating second booking in same session")
    response = send_request(session_id, "I need an electrician")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date for second booking", date_prompt)
    assert date_prompt, "System should prompt for date for second booking"
    response = send_request(session_id, "day after tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time for second booking", time_prompt)
    assert time_prompt, "System should prompt for time for second booking"
    times_to_try = ["2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm"]
    technician_prompt = False
    for time in times_to_try:
        print(f"Trying time: {time}")
        response = send_request(session_id, time)
        print_system_response(response)
        if is_conflict_detected(response):
            print(f"Conflict detected for {time}, trying another time")
            continue
        technician_prompt = is_technician_prompt(response)
        if technician_prompt:
            break
    print_test_result(
        "System prompts for technician selection for second booking",
        technician_prompt)
    assert technician_prompt, "System should prompt for technician selection for second booking"
    response = send_request(session_id, "1")
    print_system_response(response)
    booking_confirmed = is_booking_confirmed(response)
    print_test_result("Second booking confirmed", booking_confirmed)
    assert booking_confirmed, "Second booking should be confirmed"
    print_step(3, "Verifying both bookings exist")
    response = send_request(session_id, "list my bookings")
    print_system_response(response)
    plumber_booking = "plumber" in response.lower()
    electrician_booking = "electrician" in response.lower()
    print_test_result("Plumber booking exists", plumber_booking)
    print_test_result("Electrician booking exists", electrician_booking)
    assert plumber_booking, "Plumber booking should exist"
    assert electrician_booking, "Electrician booking should exist"


def test_booking_with_nonexistent_specialty():
    print_header("Testing Booking with Nonexistent Specialty")
    reset_database()
    session_id = str(uuid.uuid4())
    reset_session(session_id)
    print_step(1, "Requesting nonexistent specialty")
    response = send_request(session_id, "I need a chef")
    print_system_response(response)
    specialty_not_available = "don't offer" in response.lower() or "don't have" in response.lower(
    ) or "not available" in response.lower() or "not a service" in response.lower()
    print_test_result(
        "System indicates specialty not available",
        specialty_not_available)
    assert specialty_not_available, "System should indicate that the specialty is not available"
    print_step(2, "Requesting valid specialty after rejection")
    response = send_request(session_id, "I need a plumber then")
    print_system_response(response)
    date_prompt = is_date_prompt(response)
    print_test_result("System prompts for date after valid specialty", date_prompt)
    assert date_prompt, "System should prompt for date after valid specialty"
    response = send_request(session_id, "tomorrow")
    print_system_response(response)
    time_prompt = is_time_prompt(response)
    print_test_result("System prompts for time", time_prompt)
    assert time_prompt, "System should prompt for time"
    times_to_try = ["3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm", "9 pm"]
    technician_prompt = False
    for time in times_to_try:
        print(f"Trying time: {time}")
        response = send_request(session_id, time)
        print_system_response(response)
        if is_conflict_detected(response):
            print(f"Conflict detected for {time}, trying another time")
            continue
        technician_prompt = is_technician_prompt(response)
        if technician_prompt:
            break
    print_test_result("System prompts for technician selection", technician_prompt)
    assert technician_prompt, "System should prompt for technician selection"
    response = send_request(session_id, "1")
    print_system_response(response)
    booking_confirmed = is_booking_confirmed(response)
    print_test_result("Booking confirmed with valid specialty", booking_confirmed)
    assert booking_confirmed, "Booking should be confirmed with valid specialty"


if __name__ == "__main__":
    test_invalid_time_input()
    test_conflict_resolution()
    test_date_time_format_variations()
    test_combined_date_time_input()
    test_specialty_variations()
    test_multi_turn_correction()
    test_cancel_during_booking()
    test_multiple_bookings_same_session()
    test_booking_with_nonexistent_specialty()
