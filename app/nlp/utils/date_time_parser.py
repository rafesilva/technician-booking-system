import re
from datetime import datetime, timedelta, time
from typing import Tuple, Optional, Union
from app.nlp.constants import (
    DATE_PATTERNS,
    MONTH_NAMES,
    TIME_PATTERNS,
    SIMPLE_DIGIT_PATTERN,
    MONTH_DAY_PATTERN,
    TIME_WITHOUT_AMPM_PATTERN,
    DATE_PATTERNS_EXTENDED
)


class DateTimeParser:
    @staticmethod
    def parse_date(text: str) -> Tuple[Optional[datetime.date], Optional[str]]:
        text = text.lower().strip()
        today = datetime.now().date()
        full_month_match = re.fullmatch(r'([a-z]+)\s+(\d{1,2})$', text.lower())
        if full_month_match:
            month_name, day = full_month_match.groups()
            day = int(day)
            for i, month in enumerate(MONTH_NAMES):
                if month_name == month or month_name == month + 's':
                    month_index = i + 1
                    year = today.year
                    try:
                        date_obj = datetime(year, month_index, day).date()
                        return date_obj, f"{month_name.capitalize()} {day}"
                    except ValueError:
                        pass
        date_time_split = text
        for pattern in TIME_PATTERNS:
            time_match = re.search(pattern, text)
            if time_match:
                time_start = time_match.start()
                date_time_split = text[:time_start].strip()
                break
        if "today" in date_time_split:
            return today, "today"
        if "tomorrow" in date_time_split:
            tomorrow = today + timedelta(days=1)
            return tomorrow, "tomorrow"
        if "day after tomorrow" in date_time_split:
            day_after_tomorrow = today + timedelta(days=2)
            return day_after_tomorrow, "day after tomorrow"
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday"]
        for i, day in enumerate(days):
            if day in date_time_split:
                today_weekday = today.weekday()
                target_weekday = i
                days_ahead = (target_weekday - today_weekday) % 7
                if days_ahead == 0:
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
                return target_date, f"next {day}"
        month_day_patterns = [
            r'([a-zA-Z]+)\s+(\d{1,2})',
            r'([a-zA-Z]+)\.?\s+(\d{1,2})',
        ]
        for pattern in month_day_patterns:
            month_day_match = re.search(pattern, date_time_split)
            if month_day_match:
                month_name, day = month_day_match.groups()
                day = int(day)
                for i, month in enumerate(MONTH_NAMES):
                    if month_name.lower().startswith(month) or month.startswith(month_name.lower()):
                        month_index = i + 1
                        year = today.year
                        try:
                            date_obj = datetime(year, month_index, day).date()
                            month_full = MONTH_NAMES[month_index-1].capitalize()
                            return date_obj, f"{month_full} {day}"
                        except ValueError:
                            pass
        match = re.search(MONTH_DAY_PATTERN, date_time_split)
        if match:
            month_name, day = match.groups()
            day = int(day)
            for i, month in enumerate(MONTH_NAMES):
                if month_name.startswith(month) or month.startswith(month_name):
                    month_index = i + 1
                    year = today.year
                    try:
                        date_obj = datetime(year, month_index, day).date()
                        return date_obj, f"{month_name.capitalize()} {day}"
                    except ValueError:
                        pass
        for i, month in enumerate(MONTH_NAMES):
            if month in date_time_split.lower():
                month_pos = date_time_split.lower().find(month)
                rest_of_text = date_time_split.lower()[month_pos + len(month):].strip()
                day_match = re.search(r'(\d{1,2})', rest_of_text)
                if day_match:
                    day = int(day_match.group(1))
                    month_index = i + 1
                    year = today.year
                    try:
                        date_obj = datetime(year, month_index, day).date()
                        return date_obj, f"{month.capitalize()} {day}"
                    except ValueError:
                        pass
        for pattern in DATE_PATTERNS_EXTENDED:
            match = re.search(pattern, date_time_split)
            if match:
                try:
                    if pattern == DATE_PATTERNS_EXTENDED[0]:
                        day, month, year = match.groups()
                        day = int(day)
                        month = int(month)
                        year = int(year)
                        if year < 100:
                            year += 2000
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{day}/{month}/{year}"
                    elif pattern == DATE_PATTERNS_EXTENDED[1]:
                        day, month_name, year = match.groups()
                        day = int(day)
                        for i, month in enumerate(MONTH_NAMES):
                            if month_name.lower().startswith(month) or month.startswith(month_name.lower()):
                                month_index = i + 1
                                if year is None:
                                    year = today.year
                                else:
                                    year = int(year)
                                if year < 100:
                                    year += 2000
                                date_obj = datetime(year, month_index, day).date()
                                return date_obj, f"{day} {month_name} {year}"
                    elif pattern == DATE_PATTERNS_EXTENDED[2]:
                        year, month, day = match.groups()
                        year = int(year)
                        month = int(month)
                        day = int(day)
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{year}-{month}-{day}"
                    elif pattern == DATE_PATTERNS_EXTENDED[3]:
                        month_name, day, year = match.groups()
                        day = int(day)
                        year = int(year)
                        for i, month in enumerate(MONTH_NAMES):
                            if month_name.lower().startswith(month) or month.startswith(month_name.lower()):
                                month_index = i + 1
                                date_obj = datetime(year, month_index, day).date()
                                return date_obj, f"{month_name} {day}, {year}"
                except (ValueError, IndexError):
                    pass
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern == DATE_PATTERNS[0]:
                        day, month, year = match.groups()
                        day = int(day)
                        month = int(month)
                        year = int(year)
                        if year < 100:
                            year += 2000
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{day}/{month}/{year}"
                    elif pattern == DATE_PATTERNS[2]:
                        year, month, day = match.groups()
                        year = int(year)
                        month = int(month)
                        day = int(day)
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{year}-{month}-{day}"
                    elif pattern == DATE_PATTERNS[5]:
                        month_name, day, year = match.groups()
                        day = int(day)
                        year = int(year)
                        month = MONTH_NAMES.index(month_name.lower()) + 1
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{month_name} {day}, {year}"
                    else:
                        day, month_name, year = match.groups()
                        day = int(day)
                        month = MONTH_NAMES.index(month_name.lower()) + 1
                        if year is None:
                            year = today.year
                        else:
                            year = int(year)
                        if year < 100:
                            year += 2000
                        date_obj = datetime(year, month, day).date()
                        return date_obj, f"{day} {month_name} {year}"
                except (ValueError, IndexError):
                    pass
        return None, None

    @staticmethod
    def parse_time(text: str, booking_date: Optional[datetime]
                   = None) -> Tuple[Union[Tuple[int, int], datetime], str]:
        text = text.lower().strip()
        for month_name in MONTH_NAMES:
            if month_name in text:
                month_day_match = re.search(MONTH_DAY_PATTERN, text)
                if month_day_match:
                    text = text[month_day_match.end():].strip()
                    break
        single_digit_match = re.fullmatch(r'(\d{1,2})$', text)
        if single_digit_match:
            hour = int(single_digit_match.group(1))
            minute = 0
            if 5 <= hour <= 8:
                am_pm = "PM"
                display_hour = hour
                if am_pm == "PM" and hour < 12:
                    hour += 12
                time_desc = f"{display_hour}:{minute:02d} {am_pm}"
                if booking_date:
                    if hasattr(booking_date, 'hour'):
                        result_dt = booking_date.replace(hour=hour, minute=minute)
                    else:
                        result_dt = datetime.combine(booking_date, time(hour, minute))
                    return result_dt, time_desc
                else:
                    return (hour, minute), time_desc
            else:
                return None, None
        if text.strip() == "morning":
            hour = 9
            minute = 0
            time_desc = "9:00 AM"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
        elif text.strip() == "afternoon":
            hour = 12
            minute = 0
            time_desc = "12:00 PM"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
        elif text.strip() == "evening":
            hour = 18
            minute = 0
            time_desc = "6:00 PM"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
        elif text.strip() == "night":
            hour = 20
            minute = 0
            time_desc = "8:00 PM"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
        standalone_minutes_match = re.match(r'^:(\d{1,2})$', text.strip())
        if standalone_minutes_match:
            minute = int(standalone_minutes_match.group(1))
            hour = 0
            time_desc = f"{hour}:{minute:02d}"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
            else:
                return (hour, minute), time_desc
        am_pm_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
        if am_pm_match:
            hour = int(am_pm_match.group(1))
            minute = int(am_pm_match.group(2) or 0)
            am_pm = am_pm_match.group(3)
            if am_pm == "pm" and hour < 12:
                hour += 12
            elif am_pm == "am" and hour == 12:
                hour = 0
            time_desc = f"{hour % 12 or 12}:{minute:02d} {am_pm.upper()}"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
            else:
                return (hour, minute), time_desc
        period_match = re.search(
            r'(\d{1,2})(?::(\d{2}))?\s+(?:in the\s+|at\s+)?(morning|afternoon|evening|night)', text)
        if period_match:
            hour = int(period_match.group(1))
            minute = int(period_match.group(2) or 0)
            period = period_match.group(3)
            if period in ["afternoon", "evening", "night"] and hour < 12:
                hour += 12
            time_desc = f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
            if booking_date:
                if hasattr(booking_date, 'hour'):
                    result_dt = booking_date.replace(hour=hour, minute=minute)
                else:
                    result_dt = datetime.combine(booking_date, time(hour, minute))
                return result_dt, time_desc
            else:
                return (hour, minute), time_desc
        time_without_ampm = re.search(TIME_WITHOUT_AMPM_PATTERN, text.strip())
        if time_without_ampm:
            hour = int(time_without_ampm.group(1))
            minute = int(time_without_ampm.group(2) or 0)
            return None, None
        for pattern in TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern == TIME_PATTERNS[3]:
                        minute = int(match.group(1))
                        hour = 0
                        time_desc = f"{hour}:{minute:02d}"
                        if booking_date:
                            if hasattr(booking_date, 'hour'):
                                result_dt = booking_date.replace(
                                    hour=hour, minute=minute)
                            else:
                                result_dt = datetime.combine(
                                    booking_date, time(hour, minute))
                            return result_dt, time_desc
                        else:
                            return (hour, minute), time_desc
                    elif pattern == TIME_PATTERNS[6]:
                        minute = int(match.group(1))
                        hour = 0
                        time_desc = f"{hour}:{minute:02d}"
                        if booking_date:
                            if hasattr(booking_date, 'hour'):
                                result_dt = booking_date.replace(
                                    hour=hour, minute=minute)
                            else:
                                result_dt = datetime.combine(
                                    booking_date, time(hour, minute))
                            return result_dt, time_desc
                        else:
                            return (hour, minute), time_desc
                except (ValueError, IndexError):
                    continue
        return None, None

    @staticmethod
    def parse_date_time(text: str) -> Tuple[Optional[datetime], Optional[str]]:
        if "at" in text:
            parts = text.split("at")
            if len(parts) == 2:
                date_text = parts[0].strip()
                time_text = parts[1].strip()
                date_result, date_desc = DateTimeParser._parse_date_text(date_text)
                time_result, time_desc = DateTimeParser._extract_time_component(time_text)
                if date_result and time_result:
                    hour, minute = time_result if isinstance(
                        time_result, tuple) else (
                        time_result.hour, time_result.minute)
                    dt = datetime.combine(date_result, time(hour, minute))
                    return dt, f"{date_desc} at {time_desc}"
        combined_pattern = r'([a-zA-Z]+)\s+(\d{1,2})(?:\s+|,\s*|\s*)\s*(\d{1,2})(?::(\d{2}))?(?:\s*(am|pm))?'
        combined_match = re.search(combined_pattern, text.lower())
        if combined_match:
            month_name, day_str, hour_str, minute_str, am_pm = combined_match.groups()
            day = int(day_str)
            hour = int(hour_str)
            minute = 0 if not minute_str else int(minute_str)
            month = None
            for i, m_name in enumerate(MONTH_NAMES):
                if m_name in month_name.lower():
                    month = i + 1
                    break
            if month:
                year = datetime.now().year
                if not am_pm and 5 <= hour <= 8:
                    hour += 12
                    am_pm_str = "PM"
                    try:
                        dt = datetime(year, month, day, hour, minute)
                        month_name = MONTH_NAMES[month-1].capitalize()
                        display_hour = hour if hour <= 12 else hour - 12
                        if display_hour == 0:
                            display_hour = 12
                        time_desc = f"{display_hour}:{minute:02d} {am_pm_str}"
                        return dt, f"{month_name} {day} at {time_desc}"
                    except ValueError:
                        pass
                elif am_pm:
                    if am_pm.lower() == "pm" and hour < 12:
                        hour += 12
                    elif am_pm.lower() == "am" and hour == 12:
                        hour = 0
                    try:
                        dt = datetime(year, month, day, hour, minute)
                        month_name = MONTH_NAMES[month-1].capitalize()
                        display_hour = hour if hour <= 12 else hour - 12
                        if display_hour == 0:
                            display_hour = 12
                        am_pm_str = "AM" if hour < 12 else "PM"
                        time_desc = f"{display_hour}:{minute:02d} {am_pm_str}"
                        return dt, f"{month_name} {day} at {time_desc}"
                    except ValueError:
                        pass
                else:
                    return None, None
        day_month_time_match = re.search(
            r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{1,2}(?::\d{2})?(?:\s*[aApP][mM])?)', text)
        if day_month_time_match:
            day_str, month_str, time_str = day_month_time_match.groups()
            day = int(day_str)
            month = None
            for i, month_name in enumerate(MONTH_NAMES):
                if month_name in month_str.lower():
                    month = i + 1
                    break
            if month:
                year = datetime.now().year
                time_result, time_desc = DateTimeParser.parse_time(time_str)
                if time_result:
                    hour, minute = time_result if isinstance(
                        time_result, tuple) else (
                        time_result.hour, time_result.minute)
                    try:
                        dt = datetime(year, month, day, hour, minute)
                        month_name = MONTH_NAMES[month-1].capitalize()
                        return dt, f"{month_name} {day} at {time_desc}"
                    except ValueError:
                        pass
        date_result, date_desc = DateTimeParser.parse_date(text)
        time_result, time_desc = DateTimeParser.parse_time(text)
        if date_result and time_result:
            if isinstance(time_result, tuple):
                hour, minute = time_result
            else:
                hour, minute = time_result.hour, time_result.minute
            dt = datetime.combine(date_result, time(hour, minute))
            return dt, f"{date_desc} at {time_desc}"
        for month_name in MONTH_NAMES:
            if month_name in text.lower():
                month_day_match = re.search(MONTH_DAY_PATTERN, text.lower())
                if month_day_match:
                    month_str, day_str = month_day_match.groups()
                    day = int(day_str)
                    month = MONTH_NAMES.index(month_str) + 1
                    year = datetime.now().year
                    time_part = text[month_day_match.end():].strip()
                    if time_part:
                        time_match = re.search(TIME_PATTERNS[0], time_part)
                        if time_match:
                            hour = int(time_match.group(1))
                            minute = int(time_match.group(2) or 0)
                            am_pm = time_match.group(3)
                            if not am_pm:
                                if 1 <= hour <= 4 or 8 <= hour <= 11:
                                    am_pm = "pm"
                            if am_pm and am_pm.lower() == "pm" and hour < 12:
                                hour += 12
                            elif am_pm and am_pm.lower() == "am" and hour == 12:
                                hour = 0
                            display_hour = hour if hour <= 12 else hour - 12
                            if display_hour == 0:
                                display_hour = 12
                            am_pm_str = "AM" if hour < 12 else "PM"
                            time_desc = f"{display_hour}:{minute:02d} {am_pm_str}"
                            try:
                                dt = datetime(year, month, day, hour, minute)
                                return dt, f"{month_str.capitalize()} {day} at {time_desc}"
                            except ValueError:
                                pass
        return None, None

    @staticmethod
    def _parse_date_text(
            date_text: str) -> Tuple[Optional[datetime.date], Optional[str]]:
        return DateTimeParser.parse_date(date_text)

    @staticmethod
    def _extract_time_component(
            time_text: str) -> Tuple[Optional[Tuple[int, int]], Optional[str]]:
        return DateTimeParser.parse_time(time_text)
