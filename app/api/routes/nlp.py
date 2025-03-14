from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import colorama
from colorama import Fore, Style
from app.nlp.processors.natural_language_processor import NaturalLanguageProcessor
from app.nlp.utils.intent_recognizer import IntentRecognizer
colorama.init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)
router = APIRouter()
nlp_processor = NaturalLanguageProcessor()
session_contexts = {}
intent_recognizer = IntentRecognizer()


def log_chat_interaction(session_id: str, user_message: str, system_response: str):
    logger.info(f"\n{Fore.CYAN}{'=' * 50}")
    logger.info(f"{Fore.YELLOW}CHAT INTERACTION - {Fore.GREEN}Session: {session_id}")
    logger.info(f"{Fore.CYAN}{'-' * 50}")
    logger.info(f"{Fore.MAGENTA}User: {Style.RESET_ALL}{user_message}")
    logger.info(f"{Fore.BLUE}System: {Style.RESET_ALL}{system_response}")
    logger.info(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")


class NLPRequest(BaseModel):
    text: str
    session_id: str = None


class NLPResponse(BaseModel):
    message: str


class DebugResponse(BaseModel):
    contexts: dict


class IntentRequest(BaseModel):
    text: str


class IntentResponse(BaseModel):
    is_booking_request: bool
    is_update_request: bool
    is_cancellation_request: bool
    is_list_bookings_request: bool
    is_booking_id_inquiry: bool
    is_greeting: bool


@router.post("/process", response_model=NLPResponse)
async def process_text(request: NLPRequest) -> NLPResponse:
    try:
        request_processor = NaturalLanguageProcessor()
        text = request.text.strip().lower()
        if request.session_id:
            if request.session_id not in session_contexts:
                session_contexts[request.session_id] = {}
            for key, value in session_contexts[request.session_id].items():
                request_processor.user_context[key] = value
        else:
            logger.info("No session_id provided, using empty context")
        response = request_processor.process_input(text)
        log_chat_interaction(
            session_id=request.session_id or "no_session",
            user_message=request.text,
            system_response=response
        )
        local_intent_recognizer = IntentRecognizer()
        if local_intent_recognizer.is_list_bookings_request(text):
            if request.session_id:
                session_contexts[request.session_id] = request_processor.user_context.copy()
            return NLPResponse(message=response)
        if "has been updated to" in response.lower() and request.session_id:
            if request.session_id in session_contexts:
                del session_contexts[request.session_id]
            session_contexts[request.session_id] = {"last_booking_id": None}
            return NLPResponse(message=response)
        if request.session_id:
            session_contexts[request.session_id] = request_processor.user_context.copy()
        return NLPResponse(message=response)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/contexts", response_model=DebugResponse)
async def get_contexts() -> DebugResponse:
    return DebugResponse(contexts=session_contexts)


@router.get("/debug/reset-context/{session_id}")
async def reset_context(session_id: str) -> NLPResponse:
    if session_id in session_contexts:
        del session_contexts[session_id]
        session_contexts[session_id] = {}
        return NLPResponse(message=f"Context for session {session_id} has been reset")
    else:
        return NLPResponse(message=f"No context found for session {session_id}")


@router.post("/debug/test-intent", response_model=IntentResponse)
async def test_intent(request: IntentRequest) -> IntentResponse:
    return IntentResponse(
        is_booking_request=intent_recognizer.is_booking_request(request.text),
        is_update_request=intent_recognizer.is_update_request(request.text),
        is_cancellation_request=intent_recognizer.is_cancellation_request(request.text),
        is_list_bookings_request=intent_recognizer.is_list_bookings_request(
            request.text),
        is_booking_id_inquiry=intent_recognizer.is_booking_id_inquiry(request.text),
        is_greeting=intent_recognizer.is_greeting(request.text)
    )
