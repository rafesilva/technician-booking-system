from app.nlp.utils.date_time_parser import DateTimeParser
import unittest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


def test_standalone_minutes():
    parser = DateTimeParser()
    date_obj = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = parser.parse_time(":30", date_obj)
    print(f"Test ':30': {result}")
    assert result is not None
    time_dt, time_str = result
    assert time_dt.hour == 0
    assert time_dt.minute == 30
    result = parser.parse_time("30 minutes", date_obj)
    print(f"Test '30 minutes': {result}")
    if result:
        time_dt, time_str = result
        assert time_dt.minute == 30


def test_combined_time_formats():
    parser = DateTimeParser()
    date_obj = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = parser.parse_time("3:30 PM", date_obj)
    print(f"Test '3:30 PM': {result}")
    assert result is not None
    time_dt, time_str = result
    assert time_dt.hour == 15
    assert time_dt.minute == 30
    result = parser.parse_time("3:30 pm", date_obj)
    print(f"Test '3:30 pm': {result}")
    assert result is not None
    time_dt, time_str = result
    assert time_dt.hour == 15
    assert time_dt.minute == 30
    result = parser.parse_time("3:30PM", date_obj)
    print(f"Test '3:30PM': {result}")
    assert result is not None
    time_dt, time_str = result
    assert time_dt.hour == 15
    assert time_dt.minute == 30
    result = parser.parse_time("15:30", date_obj)
    print(f"Test '15:30': {result}")
    assert result == (
        None, None), "24-hour format should return (None, None) to prompt for AM/PM clarification"
    result = parser.parse_time("3:30 in the afternoon", date_obj)
    print(f"Test '3:30 in the afternoon': {result}")
    if result is not None:
        time_dt, time_str = result
        assert time_dt.hour == 15
        assert time_dt.minute == 30


if __name__ == "__main__":
    test_standalone_minutes()
    test_combined_time_formats()
