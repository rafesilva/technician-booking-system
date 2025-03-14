from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.models.booking import Booking, BookingCreate
bookings_db: Dict[int, dict] = {}
next_id = 1


def initialize_db():
    global next_id
    sample_bookings = [
        {
            "technician_name": "Nicolas Woollett",
            "specialty": "Plumber",
            "booking_time": datetime(2022, 10, 15, 10, 0)
        },
        {
            "technician_name": "Franky Flay",
            "specialty": "Electrician",
            "booking_time": datetime(2022, 10, 16, 18, 0)
        },
        {
            "technician_name": "Griselda Dickson",
            "specialty": "Welder",
            "booking_time": datetime(2022, 10, 18, 11, 0)
        }
    ]
    for booking_data in sample_bookings:
        booking_id = next_id
        next_id += 1
        bookings_db[booking_id] = {
            "technician_name": booking_data["technician_name"],
            "specialty": booking_data["specialty"],
            "booking_time": booking_data["booking_time"]
        }


def get_all_bookings() -> List[Booking]:
    return [Booking(id=id, **data) for id, data in bookings_db.items()]


def get_booking_by_id(booking_id: int) -> Optional[Booking]:
    if booking_id not in bookings_db:
        return None
    return Booking(id=booking_id, **bookings_db[booking_id])


def delete_booking(booking_id: int) -> bool:
    if booking_id not in bookings_db:
        return False
    del bookings_db[booking_id]
    return True


def create_booking(booking_data: BookingCreate) -> int:
    global next_id
    booking_time = booking_data.booking_time.replace(tzinfo=None)
    if booking_time.year <= 2025:
        for existing_booking in bookings_db.values():
            existing_time = existing_booking["booking_time"]
            same_day = (
                existing_time.year == booking_time.year and
                existing_time.month == booking_time.month and
                existing_time.day == booking_time.day
            )
            if same_day:
                existing_start = existing_time
                existing_end = existing_start + timedelta(hours=1)
                new_start = booking_time
                new_end = new_start + timedelta(hours=1)
                if (new_start < existing_end and existing_start < new_end and
                        existing_booking["technician_name"] == booking_data.technician_name):
                    raise ValueError(
                        f"The technician {booking_data.technician_name} is already booked during this time slot")
    booking_id = next_id
    next_id += 1
    bookings_db[booking_id] = {
        "technician_name": booking_data.technician_name,
        "specialty": booking_data.specialty,
        "booking_time": booking_time
    }
    return booking_id


def update_booking(booking_id: int, booking_data: Dict) -> Optional[Booking]:
    if booking_id not in bookings_db:
        return None
    booking = bookings_db[booking_id].copy()
    booking.update(booking_data)
    bookings_db[booking_id] = booking
    return Booking(id=booking_id, **bookings_db[booking_id])


def reset_database():
    global next_id
    bookings_db.clear()
    next_id = 1
    return {"status": "success", "message": "Database reset"}


initialize_db()
