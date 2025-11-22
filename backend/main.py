from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.anime import User, OAuthRequest, UserToken

import secrets
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from urllib.parse import urlencode

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

@app.get('/oauth')
async def redirect_to_mal_oauth():
    # Generate and store code_verifier and code_challenge
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state=generate_state()

    # Store code_verifier in the database
    with Session(engine) as db:
        oauth_request = OAuthRequest(
            code_verifier=code_verifier,
            state=state,
            created_at=datetime.now(timezone.utc) 
        )
        db.add(oauth_request)
        db.commit()
        db.refresh(oauth_request)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "plain",
        "state": state
    }
    auth_url = f"https://myanimelist.net/v1/oauth2/authorize?{urlencode(params)}"

    # Redirect user to MyAnimeList OAuth page
    return RedirectResponse(auth_url)

@app.get('/oauth/callback')
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...)
):
    return {"code": code, "state": state}

# Generating
def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier: str):
    return code_verifier

def generate_state():
    return secrets.token_urlsafe(16)