from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str

class TokenPayload(BaseModel):
    user_id: Optional[str] = None 