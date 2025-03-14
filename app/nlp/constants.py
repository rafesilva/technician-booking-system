from typing import Dict, List
MESSAGES = {
    "INVALID_DATE_FORMAT": "I couldn't understand that date. Please provide a valid date like 'tomorrow', 'next Monday', or 'July 15'.",
    "INVALID_TIME_FORMAT": "I couldn't understand that time. Please provide a valid time like '3:00 PM', '3:15 PM', '3:30', 'morning', or 'afternoon'.",
    "TIME_ERROR": "I couldn't understand that time. Please provide a valid time like '3:00 PM', '3:15 PM', '3:30 PM', 'morning', or 'afternoon'.",
    "NO_DATE_SELECTED": "No date selected for the booking.",
    "PAST_DATE": "That date is in the past. Please select a future date.",
    "NO_BOOKINGS": "You don't have any bookings.",
    "BOOKING_ERROR": "Sorry, there was an error creating your booking. Please try again.",
    "PROCESS_CANCELLED": "Process cancelled.",
    "BOOKING_PROCESS_CANCELLED": "Booking process cancelled.",
    "AMPM_PROMPT": "Is that {hour}:{minute:02d} AM or PM? Please specify 'AM' or 'PM'.",
    "SPECIALTY_PROMPT": "What type of technician do you need? (e.g., plumber, electrician, welder, gardener, carpenter, painter, HVAC)",
    "GREETING": "Hello! I can help you book a technician, check your bookings, or cancel a booking. How can I assist you today?",
    "UNCLEAR_REQUEST": "I'm not sure how to help with that. You can book a technician, check your bookings, or cancel a booking.",
    "REPEAT_REQUEST": "I didn't catch that. Could you please repeat?",
    "NO_TECHNICIANS": "Sorry, there are no available technicians. Please try a different specialty or time.",
    "DATE_PROMPT": "What date would you like to book the {specialty} for? (e.g., 'tomorrow', 'next Monday', 'July 15')",
    "TIME_PROMPT": "What time would you like to book the {specialty}? (e.g., '3 PM', '3:15 PM', 'morning', 'afternoon')",
    "UPDATE_TIME_PROMPT": "What time would you like to reschedule to? (e.g., '3 PM', '3:15 PM', 'morning', 'afternoon')",
    "UPDATE_DATE_PROMPT": "What day would you like to reschedule to? (e.g., 'tomorrow', 'next Monday', 'July 15')",
    "INVALID_AMPM_FORMAT": "I couldn't understand that. Please specify 'AM' or 'PM'.",
    "PROVIDE_BOOKING_ID_CANCEL": "Which booking would you like to cancel? Please provide the booking ID.",
    "PROVIDE_BOOKING_ID_UPDATE": "Which booking would you like to update? Please provide the booking ID.",
    "PROVIDE_VALID_BOOKING_ID": "Please provide a valid booking ID (a number).",
    "NO_BOOKING_FOUND": "No booking found with ID {booking_id}.",
    "CONFLICT_DETECTED": "There is already a booking at {time_description}. Would you like to schedule at a different time?",
    "DIFFERENT_TIME_PROMPT": "Please provide a different time for your {specialty} appointment.",
    "TECHNICIAN_SELECTION_PROMPT": "Please select a technician by number or name.",
    "TECHNICIAN_SELECTION_INVALID": "Please select a valid number between 1 and {num_technicians}.",
    "TECHNICIAN_NOT_FOUND": "I couldn't find a technician matching '{text}'. Please select a technician by number (1-{num_technicians}) or name.",
    "BOOKING_ISSUE": "Sorry, there was an issue with your booking. Please start over.",
    "UPDATE_ISSUE": "I'm not sure which booking you want to update. Please start over.",
    "UPDATE_NOT_FOUND": "I couldn't find booking {booking_id}. Please try again.",
    "UPDATE_CONFIRMATION": "Your booking has been updated from {old_time} to {new_time} with {technician_name} ({specialty}).",
    "BOOKING_CONFIRMATION": "Your booking with {technician_name} ({specialty}) is confirmed for {day_of_week}, {date_str} at {time_str}. Your booking ID is {booking_id}.",
    "CANCELLATION_CONFIRMATION": "Your booking with {technician_name} for {booking_time} has been cancelled.",
    "BOOKING_CANCELLED": "Your booking with {technician_name} for {booking_time} has been cancelled.",
    "TECHNICIAN_OPTIONS": "For {time_str}, we have the following {specialty}s available:\n\n{technician_list}\n\nPlease select a technician by number or name.",
    "TIME_SELECTION_CANCELLED": "Time selection cancelled.",
    "SPECIALTY_CHANGE_CONFIRMATION": "I've changed your booking to {article} {specialty} instead. {date_prompt}"
}
PROCESSOR_MESSAGES = {
    "PROVIDE_CANCEL_BOOKING_ID": "Please provide the booking ID you want to cancel.",
    "PROVIDE_UPDATE_BOOKING_ID": "Please provide the booking ID you want to update.",
    "GENERIC_TECHNICIAN_PROMPT": "Please specify what type of technician you need (e.g., plumber, electrician, welder, gardener, carpenter, painter, HVAC).",
    "PROVIDE_VALID_BOOKING_ID": "Please provide a valid booking ID (a number).",
    "UPDATE_START_OVER": "I'm not sure which booking you want to update. Please start over.",
    "UPDATE_NOT_FOUND": "I couldn't find booking {booking_id}. Please try again.",
    "UPDATE_UNCLEAR_INFO": "I'm not sure what information you're providing for the update. Please start over.",
    "NO_BOOKINGS_TO_UPDATE": "You don't have any bookings to update. Would you like to schedule a new appointment?",
    "BOOKING_CONFLICT": "There is already a booking at {time_description} with {technician_name} ({specialty}). Please choose a different time.",
    "BOOKING_UPDATED": "Your booking with {technician_name} has been updated from {old_date} at {old_time} to {new_date_str} at {new_time}.",
    "BOOKING_CANCELLED": "Your booking with {technician_name} for {booking_time} has been cancelled.",
    "UNCLEAR_HELP": "I'm not sure how to help with that. You can book a technician, check your bookings, or cancel a booking.",
    "UPDATE_BOOKING_PROMPT": "You're updating your booking with {technician_name} ({specialty}) currently scheduled for {booking_time}. What day would you like to reschedule to?"
}
DATE_TIME_FORMATS = {
    "BOOKING_TIME_DISPLAY": "%A, %B %d at %-I:%M %p",
    "TIME_ONLY_DISPLAY": "%-I:%M %p",
    "DATE_ONLY_DISPLAY": "%A, %B %d",
    "DATETIME_WITH_DAY": "%A, %B %d at %-I:%M %p",
    "DATETIME_WITHOUT_DAY": "%B %d at %-I:%M %p",
    "TIME_ONLY_FORMAT": "%-I:%M %p",
    "DAY_OF_WEEK_FORMAT": "%A",
    "DATE_ONLY_FORMAT": "%B %d"
}
NEGATIVE_RESPONSES = ["no", "n", "nope", "nevermind"]
CANCEL_TERMS = ["cancel", "nevermind", "cancellation"]
TECHNICIANS: Dict[str, List[str]] = {
    "Plumber": ["Nicolas Woollett", "John Pipe", "Sarah Waters"],
    "Electrician": ["Franky Flay", "Emma Volt", "Michael Wire"],
    "Welder": ["Griselda Dickson", "Mark Steel", "Lisa Torch"],
    "Gardener": ["Peter Green", "Rose Bush", "Tom Lawn"],
    "Carpenter": ["Woody Oak", "Jane Hammer", "Sam Nail"],
    "Painter": ["Pablo Brush", "Frida Color", "Vincent Wall"],
    "HVAC": ["Cool Breeze", "Warm Current", "Air Flow"],
    "General Repairs": ["Fix It Felix", "Handy Mandy", "Repair Randy"],
    "Technician": ["Alex Fix", "Samantha Tool", "Jamie Repair"]
}
SPECIALTY_TERMS: Dict[str, List[str]] = {
    "Plumber": ["plumbing", "pipe", "leak", "toilet", "sink", "faucet", "drain", "water heater"],
    "Electrician": ["electrical", "wiring", "circuit", "power", "outlet", "light", "switch", "breaker"],
    "Gardener": ["garden", "lawn", "plant", "tree", "shrub", "mow", "trim", "landscape"],
    "Carpenter": ["wood", "cabinet", "furniture", "door", "window", "shelf", "deck", "floor", "carpentry"],
    "Painter": ["paint", "wall", "ceiling", "color", "stain", "varnish", "brush", "roller"],
    "Welder": ["weld", "metal", "steel", "iron", "fabricate", "join", "solder", "forge"],
    "HVAC": ["heating", "cooling", "air conditioning", "ventilation", "ac", "furnace", "thermostat", "duct"],
    "General Repairs": ["repair", "fix", "maintenance", "handyman", "general", "broken"]
}
FUZZY_SPECIALTY_MATCHES: Dict[str, List[str]] = {
    "Plumber": ["plumb", "plumr", "pluber", "plumer"],
    "Electrician": ["electr", "electri", "lectric", "lectri", "electrcian"],
    "Welder": ["weld", "weldr", "weld"],
    "Gardener": ["garden", "gardn", "gardner"],
    "Carpenter": ["carpent", "carpentr"],
    "Painter": ["paint", "paintr"],
    "HVAC": ["hvac", "ac", "heating", "cooling"]
}
BOOKING_KEYWORDS = [
    "book", "schedule", "appointment", "reserve", "make a booking",
    "make an appointment", "need a", "want a", "looking for a", "i need a"
]
INQUIRY_KEYWORDS = ["what", "tell me", "show", "give me"]
ID_KEYWORDS = ["id", "number", "booking id", "appointment id", "reference"]
CANCEL_KEYWORDS = ["cancel", "delete", "remove", "cancellation"]
UPDATE_KEYWORDS = ["update", "change", "modify", "reschedule"]
BOOKING_REFERENCE_KEYWORDS = ["booking", "appointment", "reservation"]
LIST_KEYWORDS = [
    "list",
    "show",
    "view",
    "see",
    "get",
    "display",
    "what are",
    "check",
    "my"]
BOOKING_PLURAL_KEYWORDS = [
    "booking",
    "bookings",
    "appointment",
    "appointments",
    "reservation",
    "reservations",
    "schedule"]
LIST_BOOKINGS_EXACT_MATCHES = [
    "my bookings", "list my bookings", "show my bookings", "check bookings",
    "show bookings", "list bookings", "check my bookings", "view bookings",
    "view my bookings", "get my bookings", "see my bookings", "display bookings",
    "display my bookings", "what are my bookings"
]
GREETING_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "greetings",
    "good morning",
    "good afternoon",
    "good evening"]
DAYS_OF_WEEK = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6
}
MONTHS = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12
}
SPECIAL_TIMES = {
    "noon": (12, "12:00 PM"),
    "midnight": (0, "12:00 AM"),
    "0:00": (0, "12:00 AM"),
    "24:00": (0, "12:00 AM")
}
TIME_PERIODS = {
    "morning": (9, "9:00 AM"),
    "afternoon": (14, "2:00 PM"),
    "evening": (18, "6:00 PM"),
    "night": (20, "8:00 PM")
}
TECHNICIAN_TYPES = [
    "plumber",
    "electrician",
    "welder",
    "gardener",
    "carpenter",
    "painter",
    "hvac"]
NON_OFFERED_SPECIALTIES = [
    "chef",
    "doctor",
    "lawyer",
    "teacher",
    "driver",
    "mechanic",
    "cleaner"]
DEFAULT_USER_CONTEXT = {
    "last_booking_id": None,
    "last_specialty": None,
    "last_technician": None,
    "booking_in_progress": False,
    "awaiting_date": False,
    "awaiting_time": False,
    "awaiting_technician": False,
    "available_technicians": None,
    "conflict_detected": False,
    "temp_booking_date": None,
    "awaiting_service": False,
    "updating_booking": False,
    "update_booking_id": None,
    "awaiting_ampm": False,
    "temp_booking_hour": None,
    "temp_booking_minute": None,
    "awaiting_booking_id_for_update": False,
    "awaiting_booking_id_for_cancel": False,
    "awaiting_specialty": False,
    "specialty": None,
    "awaiting_update_time": False,
    "updating_booking_id": None,
    "is_test_booking": False
}
UPDATE_COMMANDS = [
    "update booking",
    "change booking",
    "reschedule booking",
    "modify booking",
    "update appointment",
    "change appointment",
    "reschedule appointment",
    "modify appointment",
    "update my booking",
    "change my booking",
    "reschedule my booking",
    "modify my booking",
    "update my appointment",
    "change my appointment",
    "reschedule my appointment",
    "modify my appointment"
]
VALID_SPECIALTIES = [
    "Plumber",
    "Electrician",
    "Welder",
    "Gardener",
    "Carpenter",
    "Painter",
    "HVAC",
    "Technician"]
DEFAULT_SPECIALTY = "Technician"
DEFAULT_PLUMBER_SPECIALTY = "Plumber"
TECHNICIAN_SELECTION_FORMAT = "For {time_str}, we have the following {specialty}s available:\n\n"
TECHNICIAN_SELECTION_SUFFIX = "\nPlease select a technician by number or name."
TECHNICIAN_OPTION_LINE_FORMAT = "{index}. {technician}\n"
SPECIALTY_CHANGE_CONFIRMATION = "I've changed your booking to {article} {specialty} instead. {date_prompt}"
UNSUPPORTED_SPECIALTY_MESSAGE = "I'm sorry, we don't offer that type of technician. We have plumbers, electricians, welders, gardeners, carpenters, painters, and HVAC technicians."
AM_RESPONSE = "am"
PM_RESPONSE = "pm"
AMPM_PROMPT_FORMAT = "Is that {hour}:{minute:02d} AM or PM? Please specify 'AM' or 'PM'."
BOOKINGS_LIST_HEADER = "Your bookings:\n\n"
BOOKING_DISPLAY_FORMAT = "Booking #{id}: {specialty} with {technician_name} at {booking_time}"
SIMPLE_DIGIT_PATTERN = r'\d+'
MONTH_DAY_PATTERN = r'(january|jan|february|feb|march|mar|april|apr|may|june|jun|july|jul|august|aug|september|sep|sept|october|oct|november|nov|december|dec)\s+(\d{1,2})'
DATE_PATTERNS = [
    r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?',
    r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
    r'(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{2,4}))?',
    r'(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(\w+)(?:,?\s+(\d{2,4}))?',
    r'(\d{1,2})(?:st|nd|rd|th)? (?:of )?([a-zA-Z]+)(?: (\d{2,4}))?',
    r'([a-zA-Z]+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})'
]
TIME_PATTERNS = [
    r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)',
    r'(\d{1,2}):(\d{2})',
    r'(\d{1,2})(?::(\d{2}))?\s+(?:in the\s+)?(morning|afternoon|evening|night)',
    r':(\d{2})',
    r'(\d{1,2})(?::(\d{2}))?(?:\s*o\'?clock)?(?:\s*(am|pm))?',
    r'(\d{1,2})(?::(\d{2}))?(?:\s*hrs)',
    r'(\d{1,2})\s*minutes'
]
BOOKING_ID_PATTERN = r'booking\s+(\d+)'
TIME_WITHOUT_AMPM_PATTERN = r'^(\d{1,2})(?::(\d{2}))?$'
ORDINAL_PATTERN = r'(?:the\s+)?(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th)'
NUMBER_SELECTION_PATTERN = r'(?:number|option|#|no\.?|choice)\s*(\d+)'
DIGIT_PATTERN = r'\d+'
UPDATE_BOOKING_PATTERN = r'(update|change|modify|reschedule)\s+(booking|appointment)(\s+\d+)?'
BOOKING_INQUIRY_PATTERNS = [
    r'(check|view|show|get|display|what is|details for)\s+(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)',
    r'(show|get|display)\s+(?:me\s+)?(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)',
    r'(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)(?:\s+details)?'
]
BOOKING_ID_EXTRACTION_PATTERN = r'(?:booking|appointment|id)[^\d]*(\d+)'
STANDALONE_NUMBER_PATTERN = r'\b(\d+)\b'
NEXT_DAY_PATTERN = r'next\s+(\w+)'
IN_PERIOD_PATTERN = r'(\d{1,2})(?::(\d{2}))?\s+in\s+the\s+(morning|afternoon|evening|night)'
AMPM_PATTERN = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)'
MILITARY_TIME_PATTERN = r'(\d{1,2}):(\d{2})(?!\s*[ap]m)'
MINUTES_PATTERN = r':(\d{2})'
PERIOD_PATTERN = r'(\d{1,2})(?::(\d{2}))?(?:\s+)(morning|afternoon|evening|night)'
DATE_TEXT_PATTERN = r'(today|tomorrow|day after tomorrow|next week|next month|monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun|\d{1,2}(?:st|nd|rd|th)?(?:\s+(?:of\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec))?(?:\s+\d{2,4})?|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
AT_TIME_PATTERN = r'at\s+(\d{1,2})(?::(\d{2}))?(?:\s*(am|pm))?'
TIME_TEXT_PATTERN = r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)|morning|afternoon|evening|night|\d{1,2}(?::\d{2})?)'
TIME_ONLY_PATTERN = r'(\d{1,2})(?::(\d{2}))?'
UPDATE_BOOKING_WITH_TIME_PATTERN = r'(?:change|update|reschedule|modify).*(?:booking|appointment).*(?:to|for|at|on).*'
BOOKING_ID_EXTRACTION_FROM_CONFIRMATION_PATTERN = r"booking ID is (\d+)"
SPECIFIC_BOOKING_INQUIRY_PATTERNS = [
    r'(check|view|show|get|display|what is|details for|what are the details for)\s+(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)',
    r'(show|get|display)\s+(?:me\s+)?(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)',
    r'(booking|appointment)(?:\s+|#|number|id\s+)?(\d+)(?:\s+details)?'
]
MONTH_NAMES = ["january", "february", "march", "april", "may", "june",
               "july", "august", "september", "october", "november", "december"]
DATE_PATTERNS_EXTENDED = [
    r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
    r'(\d{1,2})(?:st|nd|rd|th)? (?:of )?([a-zA-Z]+)(?: (\d{2,4}))?',
    r'(\d{4})-(\d{1,2})-(\d{1,2})',
    r'([a-zA-Z]+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})'
]
