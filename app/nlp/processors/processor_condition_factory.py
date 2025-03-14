import re
from typing import Callable, Dict, List, Any
from app.nlp.constants import (
    UPDATE_COMMANDS,
    UPDATE_BOOKING_WITH_TIME_PATTERN,
)
from app.nlp.utils.intent_recognizer import IntentRecognizer


class ProcessorConditionFactory:
    @staticmethod
    def is_update_booking_command(text: str) -> bool:
        return any(command in text.lower() for command in UPDATE_COMMANDS)

    @staticmethod
    def is_update_booking_pattern(text: str) -> bool:
        return bool(re.search(UPDATE_BOOKING_WITH_TIME_PATTERN, text.lower()))

    @staticmethod
    def is_awaiting_context_item(context: Dict[str, Any], key: str) -> Callable[[str], bool]:
        return lambda text: context.get(key, False)

    @staticmethod
    def create_intent_condition(intent_method: Callable[[str], bool]) -> Callable[[str], bool]:
        return intent_method

    @staticmethod
    def create_condition_handlers(context: Dict[str, Any],
                                  intent_recognizer: IntentRecognizer) -> List[Dict]:
        return [
            {
                "condition": ProcessorConditionFactory.is_update_booking_command,
                "handler": "_handle_update_booking_command"
            },
            {
                "condition": ProcessorConditionFactory.is_update_booking_pattern,
                "handler": "_handle_update_booking_pattern"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_date"),
                "handler": "_handle_awaiting_date"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_time"),
                "handler": "_handle_awaiting_time"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_ampm"),
                "handler": "_handle_awaiting_ampm"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_technician"),
                "handler": "_handle_awaiting_technician"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_booking_id_for_update"),
                "handler": "_handle_awaiting_booking_id_for_update"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_booking_id_for_cancel"),
                "handler": "_handle_awaiting_booking_id_for_cancel"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "awaiting_specialty"),
                "handler": "_handle_awaiting_specialty"
            },
            {
                "condition": ProcessorConditionFactory.is_awaiting_context_item(context, "updating_booking"),
                "handler": "_handle_updating_booking"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_greeting),
                "handler": "_handle_greeting"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_booking_id_inquiry),
                "handler": "_handle_booking_id_inquiry"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_specific_booking_inquiry),
                "handler": "_handle_specific_booking_inquiry"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_list_bookings_request),
                "handler": "_handle_list_bookings"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_cancellation_request),
                "handler": "_handle_cancellation"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_update_request),
                "handler": "_handle_update"
            },
            {
                "condition": ProcessorConditionFactory.create_intent_condition(intent_recognizer.is_booking_request),
                "handler": "_handle_booking"
            }
        ]
