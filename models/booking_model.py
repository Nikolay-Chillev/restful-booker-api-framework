import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class BookingDates(BaseModel):
    checkin: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(..., description="Check-out date in YYYY-MM-DD format")

    @field_validator("checkin", "checkout")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Accept YYYY-MM-DD or reasonable date strings from the API."""
        if v and re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v
        # API sometimes returns dates in other formats — accept but log
        return v


class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: Optional[str] = None


class BookingResponse(BaseModel):
    bookingid: int
    booking: Booking


class BookingId(BaseModel):
    bookingid: int
