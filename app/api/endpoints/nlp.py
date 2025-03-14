from fastapi import APIRouter
from typing import Dict, Any
from app.models.nlp import NLPRequest, NLPResponse
from app.nlp.processor import NaturalLanguageProcessor
router = APIRouter()
session_contexts = {}


@router.post("/process", response_model=NLPResponse)
def process_nlp_request(request: NLPRequest):
    processor = NaturalLanguageProcessor()
    session_id = request.session_id
    if session_id not in session_contexts:
        session_contexts[session_id] = {}
    response = processor.process_input(request.text, session_contexts[session_id])
    return {"message": response}


@router.get("/debug/reset-context/{session_id}")
def reset_context(session_id: str):
    if session_id in session_contexts:
        session_contexts[session_id] = {}
    return {"status": "Context reset"}


@router.get("/debug/context/{session_id}", response_model=Dict[str, Any])
def get_session_context(session_id: str):
    if session_id not in session_contexts:
        return {"error": "Session not found"}
    return session_contexts[session_id]
