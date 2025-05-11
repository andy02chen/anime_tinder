from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from database import Base

class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    pfp: Mapped[str | None] = mapped_column(String, nullable=True)
    access_token: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)
    expires_in: Mapped[int] = mapped_column(Integer)
    session_id: Mapped[str] = mapped_column(String)

class OAuthSession(Base):
    __tablename__ = "oauth"

    session_id: Mapped[str] = mapped_column(String, unique=True)
    oauth_state: Mapped[str] = mapped_column(String, nullable=False, unique=True, primary_key=True)
    code_verifier: Mapped[str] = mapped_column(String, nullable=False)
