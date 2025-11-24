from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.anime import User, OAuthRequest

import secrets
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
import httpx

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
        state: str = Query(...),
        session: Session = Depends(get_session)
    ):

    oauth_request = session.exec(select(OAuthRequest).where(OAuthRequest.state == state)).first()
    if not oauth_request:
        return {"error": "Invalid state"}

    result = await exchange_code_for_token(code, oauth_request.code_verifier)

    if result.get("error"):
        return {"error": result["error"]}

    access_token = result["access_token"]
    refresh_token = result["refresh_token"]
    expires_at = result["expires_at"]

    user = await sync_mal_user(session, access_token, refresh_token, expires_at)

    session.add(user)
    session.commit()
    session.refresh(user)

    # Delete the OAuthRequest after successful login
    session.delete(oauth_request)
    session.commit()

    return {"message": "Login successful"}

async def sync_mal_user(session: Session, access_token: str, refresh_token: str, expires_at: int):
    # 1. Fetch MAL user profile
    profile = await fetch_mal_user(access_token)
    print(profile)
    
    # 2. Use MAL ID to identify unique users
    mal_id = profile["id"]
    
    user = session.exec(select(User).where(User.mal_id == mal_id)).first()
    
    if user:
        # update existing user
        user.mal_access_token = access_token
        user.mal_refresh_token = refresh_token
        user.mal_expires_at = expires_at
        user.avatar = profile.get("picture")
        user.username = profile.get("name")
    else:
        # create new
        user = User(
            mal_id=mal_id,
            username=profile.get("name"),
            avatar=profile.get("picture"),
            mal_access_token=access_token,
            mal_refresh_token=refresh_token,
            mal_expires_at=expires_at,
        )
        session.add(user)

    session.commit()
    session.refresh(user)
    return user

async def fetch_mal_user(access_token: str):
    url = "https://api.myanimelist.net/v2/users/@me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)

        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Failed to fetch user profile from MAL")

        return resp.json()

async def exchange_code_for_token(code: str, code_verifier: str):
    url="https://myanimelist.net/v1/oauth2/token"
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data)

        if resp.status_code != 200:
            return {
                "error": True,
                "status": resp.status_code,
                "body": resp.json()
            }

        token_data = resp.json()

        return {
            "error": False,
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])
        }

# Generating
def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier: str):
    return code_verifier

def generate_state():
    return secrets.token_urlsafe(32)