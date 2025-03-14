from fastapi import APIRouter, HTTPException
from typing import List
from app.models.booking import Booking, BookingCreate
from app.db.database import get_all_bookings, get_booking_by_id, delete_booking, create_booking, update_booking
router = APIRouter()


@router.get("/", response_model=List[Booking])
def list_bookings():
    return get_all_bookings()


@router.get("/{booking_id}", response_model=Booking)
def retrieve_booking(booking_id: int):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.delete("/{booking_id}")
def remove_booking(booking_id: int):
    success = delete_booking(booking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted successfully"}


@router.post("/", response_model=Booking)
def schedule_booking(booking: BookingCreate):
    try:
        booking_id = create_booking(booking)
        return get_booking_by_id(booking_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{booking_id}", response_model=Booking)
def update_booking_endpoint(booking_id: int, booking: BookingCreate):
    try:
        updated_booking = update_booking(booking_id, booking.dict())
        if updated_booking is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        return updated_booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
