import re
from typing import Optional
from app.nlp.constants import (
    TECHNICIANS,
    SPECIALTY_TERMS,
    FUZZY_SPECIALTY_MATCHES,
    TECHNICIAN_TYPES,
    BOOKING_ID_EXTRACTION_PATTERN,
    STANDALONE_NUMBER_PATTERN
)


class BookingDataExtractor:
    @staticmethod
    def extract_specialty(text: str) -> Optional[str]:
        text_lower = text.lower()
        if "technician" in text_lower and not any(
                specific in text_lower for specific in TECHNICIAN_TYPES):
            return None
        change_phrases = ["actually", "need", "want", "not a"]
        if any(phrase in text_lower for phrase in change_phrases):
            for specialty in TECHNICIANS.keys():
                specialty_lower = specialty.lower()
                if specialty_lower in text_lower:
                    if specialty_lower == "technician":
                        continue
                    not_pattern = rf'not\s+a\s+{specialty_lower}'
                    not_match = re.search(not_pattern, text_lower)
                    if not_match:
                        continue
                    return specialty
        for specialty in TECHNICIANS.keys():
            if specialty.lower() in text_lower:
                if specialty.lower() == "technician":
                    continue
                if "need" in text_lower or "want" in text_lower:
                    need_pos = max(text_lower.find("need"), text_lower.find("want"))
                    if need_pos != -1 and text_lower.find(specialty.lower()) > need_pos:
                        return specialty
                return specialty
        for specialty, terms in SPECIALTY_TERMS.items():
            for term in terms:
                if term in text_lower:
                    return specialty
        for specialty, fuzzy_terms in FUZZY_SPECIALTY_MATCHES.items():
            for term in fuzzy_terms:
                if term in text_lower:
                    return specialty
        return None

    @staticmethod
    def extract_booking_id(text: str) -> Optional[int]:
        match = re.search(BOOKING_ID_EXTRACTION_PATTERN, text.lower())
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        match = re.search(STANDALONE_NUMBER_PATTERN, text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
        return None
