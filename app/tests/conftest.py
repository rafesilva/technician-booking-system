import pytest
import requests
import time
import json
import sys
from datetime import datetime, timedelta
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture
def session_id():
    return f"pytest_{int(time.time())}_{random.randint(1000, 9999)}"


@pytest.fixture
def api_client(session_id):
    class ApiClient:
        def send_message(self, text):
            url = f"{BASE_URL}/nlp/process"
            payload = {
                "text": text,
                "session_id": session_id
            }
            response = requests.post(url, json=payload)
            return response.json()

        def get_context(self):
            url = f"{BASE_URL}/nlp/debug/contexts"
            response = requests.get(url)
            contexts = response.json()
            return contexts.get("contexts", {}).get(session_id, {})

        def get_bookings(self):
            url = f"{BASE_URL}/bookings/"
            response = requests.get(url)
            return response.json()

        def get_booking(self, booking_id):
            url = f"{BASE_URL}/bookings/{booking_id}"
            response = requests.get(url)
            return response.json()

        def reset_context(self):
            url = f"{BASE_URL}/nlp/debug/reset-context/{session_id}"
            response = requests.get(url)
            return response.json()
        def create_booking(self, specialty=None, days_ahead=None,
                           hour=None, am_pm=None):
            if specialty is None:
                specialty = random.choice([
                    "plumbing",
                    "electrical",
                    "HVAC",
                    "general repairs"
                ])
            if days_ahead is None:
                days_ahead = random.randint(1, 30)
            future_date = (datetime.now() + timedelta(days=days_ahead))
            if hour is None:
                hour = random.randint(8, 18)
                am_pm = "am" if hour < 12 else "pm"
                if hour > 12:
                    hour -= 12
            date_str = future_date.strftime(f"%B %d, %Y at {hour}{am_pm}")
            booking_request = f"I need {specialty} service on {date_str}"
            response = self.send_message(booking_request)
            message = response.get("message", "")
            if "What time would you like to book" in message or "What time" in message:
                response = self.send_message(f"{hour}{am_pm}")
            context = self.get_context()
            booking_id = context.get("last_booking_id")
            if booking_id is None:
                message = response.get("message", "")
                import re
                match = re.search(r"booking ID is (\d+)", message)
                if match:
                    booking_id = int(match.group(1))
            return booking_id, response
    return ApiClient()


@pytest.fixture
def existing_booking_id():
    return 3


@pytest.fixture
def future_date():
    days_ahead = random.randint(1, 30)
    future_date = (datetime.now() + timedelta(days=days_ahead))
    return future_date.strftime("%B %d, %Y at 3pm")
