from sqlalchemy import Column, Integer, String, Float
from database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    pfp = Column(String, nullable=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_in = Column(Integer)
    session_id = Column(String)