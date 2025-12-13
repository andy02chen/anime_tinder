from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    avatar: Optional[str] = None
    new_user: bool = Field(default=True)

    # MAL-related fields
    mal_id: Optional[int] = None
    mal_access_token: Optional[str] = None
    mal_refresh_token: Optional[str] = None
    mal_expires_at: Optional[datetime] = None

    # Relationship: one user → many JWT tokens
    jwt_tokens: List["JWTToken"] = Relationship(back_populates="user")


class OAuthRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code_verifier: str
    state: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JWTToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key linking to User.id
    user_id: int = Field(foreign_key="user.id")

    refresh_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revoked: bool = Field(default=False)

    # Relationship back to User
    user: Optional[User] = Relationship(back_populates="jwt_tokens")
