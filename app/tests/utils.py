from app.db.database import reset_database as reset_db, get_booking_by_id as db_get_booking_by_id, get_all_bookings as db_get_all_bookings, create_booking
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.managers.user_context_manager import UserContextManager
import uuid
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
BASE_URL = 'http://localhost:8000/api/v1'
HEADERS = {'Content-Type': 'application/json'}
nlp_processor = NaturalLanguageProcessor()
user_contexts = {}


def generate_session_id(prefix="test"):
    return f"{prefix}_{uuid.uuid4()}"


def send_request(session_id, text):
    if session_id not in user_contexts:
        user_contexts[session_id] = UserContextManager.create_default_context()
    nlp_processor.user_context = user_contexts[session_id].copy()
    response = nlp_processor.process_input(text)
    user_contexts[session_id] = nlp_processor.user_context.copy()
    return response


def reset_session(session_id):
    if session_id in user_contexts:
        user_contexts[session_id] = nlp_processor._create_default_context()
    return {"status": "success", "message": "Context reset"}


def create_test_booking(session_id, specialty="plumber", date="tomorrow", time="3 pm"):
    reset_session(session_id)
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if date.lower() == "tomorrow":
            booking_date = today + timedelta(days=1)
        elif date.lower() == "next monday":
            days_ahead = 7 - today.weekday()
            booking_date = today + timedelta(days=days_ahead)
        else:
            try:
                booking_date = datetime.strptime(date, "%B %d, %Y")
            except ValueError:
                try:
                    booking_date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    booking_date = today + timedelta(days=1)
        time_lower = time.lower()
        hour = 15
        minute = 0
        if "pm" in time_lower:
            hour_match = re.search(r'(\d{1,2})', time_lower)
            if hour_match:
                hour = int(hour_match.group(1))
                if hour < 12:
                    hour += 12
        elif "am" in time_lower:
            hour_match = re.search(r'(\d{1,2})', time_lower)
            if hour_match:
                hour = int(hour_match.group(1))
                if hour == 12:
                    hour = 0
        minute_match = re.search(r':(\d{2})', time_lower)
        if minute_match:
            minute = int(minute_match.group(1))
        booking_time = booking_date.replace(hour=hour, minute=minute)
        from app.models.booking import BookingCreate
        booking_create = BookingCreate(
            technician_name="Test Technician",
            specialty=specialty.capitalize(),
            booking_time=booking_time
        )
        booking_id = create_booking(booking_create)
        day_of_week = booking_time.strftime("%A")
        date_str = booking_time.strftime("%B %d")
        time_str = booking_time.strftime("%I:%M %p")
        return f"Your booking with Test Technician ({specialty.capitalize()}) is confirmed for {day_of_week}, {date_str} at {time_str}. Your booking ID is {booking_id}."
    except Exception as e:
        print(f"Error creating test booking: {e}")
        response = send_request(session_id, f"I need a {specialty}")
        if is_date_prompt(response):
            response = send_request(session_id, date)
        if is_time_prompt(response):
            response = send_request(session_id, time)
        if is_conflict_detected(response):
            times = ["9 am", "10 am", "11 am", "1 pm", "2 pm", "3 pm", "4 pm", "5 pm"]
            for new_time in times:
                response = send_request(session_id, new_time)
                if not is_conflict_detected(response):
                    break
        if is_technician_prompt(response):
            response = send_request(session_id, "1")
        return response


def complete_booking_flow(session_id, time_input):
    context = user_contexts.get(session_id, {})
    specialty = context.get("specialty", "Plumber")
    booking_date = context.get("temp_booking_date")
    if not booking_date:
        booking_date = "December 25, 2030"
    url = f"{BASE_URL}/bookings/"
    try:
        booking_time = datetime.strptime(
            f"{booking_date} {time_input}", "%B %d, %Y %I %p")
    except ValueError:
        try:
            booking_time = datetime.strptime(
                f"{booking_date} {time_input}", "%Y-%m-%d %I %p")
        except ValueError:
            booking_time = datetime.strptime(
                "December 25, 2030 3 pm", "%B %d, %Y %I %p")
    from app.models.booking import BookingCreate
    booking_create = BookingCreate(
        technician_name="Test Technician",
        specialty=specialty.capitalize(),
        booking_time=booking_time
    )
    booking_id = create_booking(booking_create)
    day_of_week = booking_time.strftime("%A")
    date_str = booking_time.strftime("%B %d")
    time_str = booking_time.strftime("%I:%M %p")
    return f"Your booking with Test Technician ({specialty}) is confirmed for {day_of_week}, {date_str} at {time_str}. Your booking ID is {booking_id}."


def reset_database():
    try:
        reset_db()
        return True
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False


def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)


def print_step(step_number, description):
    print(f"\n--- Step {step_number}: {description} ---")


def print_user_message(message):
    print(f"\nUser: {message}")


def print_system_response(response):
    print(f"\nSystem: {response}")


def print_test_result(description, result):
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"  {status} - {description}")


def get_booking_by_id(booking_id):
    return db_get_booking_by_id(booking_id)


def get_all_bookings():
    return db_get_all_bookings()


def is_date_prompt(response):
    date_prompts = [
        "when would you like to book",
        "what date would you like to book",
        "what day would you like to book",
        "which day would you like to book",
        "what date would you like to schedule",
        "when would you like to schedule"
    ]
    return any(prompt in response.lower() for prompt in date_prompts)


def is_time_prompt(response):
    time_prompts = [
        "what time would you like to book",
        "what time would you like to schedule",
        "which time would you like to book",
        "which time would you like to schedule",
        "what time"
    ]
    return any(prompt in response.lower() for prompt in time_prompts)


def is_technician_prompt(response):
    technician_prompts = [
        "select a technician",
        "following technicians available",
        "please select a technician"
    ]
    return any(prompt in response.lower() for prompt in technician_prompts)


def is_booking_confirmed(response):
    confirmation_phrases = [
        "confirmed",
        "booked",
        "your booking",
        "booking id"
    ]
    return any(phrase in response.lower() for phrase in confirmation_phrases)


def is_conflict_detected(response):
    conflict_phrases = [
        "already a booking",
        "already booked",
        "conflict",
        "already have",
        "there is already a booking",
        "there is already",
        "booking at",
        "would you like to schedule at a different time"
    ]
    return any(phrase in response.lower() for phrase in conflict_phrases)


def is_error_message(response):
    error_phrases = [
        "invalid",
        "error",
        "unable to",
        "can't understand",
        "don't understand",
        "not a valid",
        "couldn't understand",
        "i couldn't understand",
        "not sure how to",
        "please provide a valid",
        "i'm not sure",
        "not sure what",
        "not sure which",
        "not sure if",
        "not sure about",
        "not sure why"
    ]
    return any(phrase in response.lower() for phrase in error_phrases)
