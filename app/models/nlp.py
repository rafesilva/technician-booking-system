from pydantic import BaseModel


class NLPRequest(BaseModel):
    text: str
    session_id: str = None


class NLPResponse(BaseModel):
    message: str
