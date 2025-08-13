from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    user_input: str

class ChatResponse(BaseModel):
    status: str
    response: str
    