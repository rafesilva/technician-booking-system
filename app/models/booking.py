from pydantic import BaseModel
from datetime import datetime


class BookingBase(BaseModel):
    technician_name: str
    specialty: str
    booking_time: datetime


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    id: int

    class Config:
        from_attributes = True
