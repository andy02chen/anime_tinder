from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    avatar: str | None = None

class OAuthRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    code_verifier: str
    state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserToken(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    mal_access_token: str
    mal_refresh_token: str
    expires_at: datetime