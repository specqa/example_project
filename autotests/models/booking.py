from pydantic import BaseModel
from datetime import date
from typing import Optional

class BookingDates(BaseModel):
    checkin: date
    checkout: date

class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: Optional[str] = None

class BookingCreateResponse(BaseModel):
    bookingid: int
    booking: Booking

class BookingListItem(BaseModel):
    bookingid: int

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str