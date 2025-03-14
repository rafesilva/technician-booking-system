from typing import Dict, Optional
from app.nlp.constants import (
    MESSAGES,
    UNSUPPORTED_SPECIALTY_MESSAGE,
    VALID_SPECIALTIES,
    NON_OFFERED_SPECIALTIES
)
from app.nlp.managers.user_context_manager import UserContextManager
from app.nlp.utils.booking_data_extractor import BookingDataExtractor


class SpecialtyService:
    @staticmethod
    def handle_specialty_input(user_context: Dict, text: str) -> str:
        specialty = BookingDataExtractor.extract_specialty(text)
        if specialty:
            UserContextManager.set_temp_specialty(user_context, specialty)
            UserContextManager.set_awaiting_date(user_context)
            return MESSAGES["DATE_PROMPT"].format(specialty=specialty)
        text_lower = text.lower()
        for non_offered in NON_OFFERED_SPECIALTIES:
            if non_offered in text_lower:
                return UNSUPPORTED_SPECIALTY_MESSAGE
        return MESSAGES["SPECIALTY_PROMPT"]

    @staticmethod
    def check_and_handle_specialty_change(user_context: Dict, text: str) -> Optional[str]:
        text_lower = text.lower()
        if ("actually" in text_lower or "need" in text_lower or
                "want" in text_lower or "not a" in text_lower) and any(
                specialty in text_lower for specialty in VALID_SPECIALTIES):
            new_specialty = BookingDataExtractor.extract_specialty(text)
            current_specialty = user_context.get('temp_booking_specialty', '').lower()
            if new_specialty and new_specialty.lower() != current_specialty:
                UserContextManager.change_specialty_and_reset_to_date(
                    user_context, new_specialty)
                article = "an" if new_specialty[0].lower() in "aeiou" else "a"
                return MESSAGES["SPECIALTY_CHANGE_CONFIRMATION"].format(
                    article=article,
                    specialty=new_specialty,
                    date_prompt=MESSAGES['DATE_PROMPT'].format(specialty=new_specialty)
                )
        return None
