from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TimeResult:
    success: bool
    message: Optional[str] = None
    booking_time: Optional[datetime] = None
    time_description: Optional[str] = None
    error_code: Optional[str] = None
