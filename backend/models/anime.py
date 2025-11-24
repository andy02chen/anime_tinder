from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    avatar: str | None = None
    mal_id: int | None = None
    mal_access_token: str | None = None
    mal_refresh_token: str | None = None
    mal_expires_at: datetime | None = None


class OAuthRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code_verifier: str
    state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# class UserToken(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")
#     mal_access_token: str
#     mal_refresh_token: str
#     expires_at: datetime