from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    id: str
    access_token: str
    refresh_token: str
    expires_in: int
    session_id: str
    pfp: Optional[str] = None

class UserPublic(BaseModel):
    id: str
    pfp: Optional[str] = None

    class Config:
        orm_mode = True