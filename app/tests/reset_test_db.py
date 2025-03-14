from app.db.database import bookings_db, next_id, initialize_db
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def reset_database():
    global bookings_db, next_id
    bookings_db.clear()
    next_id = 1
    now = datetime.now()
    base_date = datetime(
        now.year,
        now.month,
        now.day).replace(
        hour=10,
        minute=0,
        second=0)
    test_bookings = [
        {
            "technician_name": "Nicolas Woollett",
            "specialty": "Plumber",
            "booking_time": base_date
        },
        {
            "technician_name": "Franky Flay",
            "specialty": "Electrician",
            "booking_time": base_date + timedelta(days=1, hours=8)
        },
        {
            "technician_name": "Griselda Dickson",
            "specialty": "Welder",
            "booking_time": base_date + timedelta(days=3, hours=1)
        },
        {
            "technician_name": "Bob Johnson",
            "specialty": "HVAC",
            "booking_time": base_date + timedelta(days=5, hours=2)
        }
    ]
    for booking_data in test_bookings:
        booking_id = next_id
        next_id += 1
        bookings_db[booking_id] = {
            "technician_name": booking_data["technician_name"],
            "specialty": booking_data["specialty"],
            "booking_time": booking_data["booking_time"]
        }
    print(f"Database reset with {len(test_bookings)} test bookings:")
    for booking_id, booking in bookings_db.items():
        print(
            f"  ID: {booking_id}, Time: {booking['booking_time']}, Technician: {booking['technician_name']}, Specialty: {booking['specialty']}")


if __name__ == "__main__":
    reset_database()
