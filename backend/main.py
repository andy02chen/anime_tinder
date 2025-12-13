from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, Cookie, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.anime import User, OAuthRequest, JWTToken

import secrets
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
import httpx

import jwt

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

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
SECRET_KEY = os.getenv("SECRET_KEY")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

################## OAUTH ################## 

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
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    message: str | None = Query(None),
    session: Session = Depends(get_session)
):

    # --- USER DENIED ---
    if error:
        return RedirectResponse(
            "http://127.0.0.1:5173/login?error=cancelled",
            status_code=303
        )

    # --- MISSING PARAMS ---
    if code is None or state is None:
        return RedirectResponse(
            "http://127.0.0.1:5173/login?error=missing_params",
            status_code=303
        )

    # --- STATE VALIDATION ---
    oauth_request = session.exec(
        select(OAuthRequest).where(OAuthRequest.state == state)
    ).first()

    if not oauth_request:
        return RedirectResponse(
            "http://127.0.0.1:5173/login?error=invalid_state",
            status_code=303
        )

    # --- TOO LONG SINCE INITIATION ---
    created_at = oauth_request.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    time_elapsed = datetime.now(timezone.utc) - created_at
    if time_elapsed > timedelta(minutes=10):
        # Clean up expired OAuthRequest
        session.delete(oauth_request)
        session.commit()

        return RedirectResponse(
            "http://127.0.0.1:5173/login?error=long_wait",
            status_code=303
        )

    # --- EXCHANGE CODE ---
    result = await exchange_code_for_token(code, oauth_request.code_verifier)

    if result.get("error"):
        return RedirectResponse(
            f"http://127.0.0.1:5173/login?error=mal_{result['error']}",
            status_code=303
        )

    # --- SUCCESS FLOW ---
    access_token = result["access_token"]
    refresh_token = result["refresh_token"]
    expires_at = result["expires_at"]

    user = await sync_mal_user(session, access_token, refresh_token, expires_at)

    session.add(user)
    session.commit()
    session.refresh(user)

    # Clean up OAuthRequest
    session.delete(oauth_request)
    session.commit()

    jwt_access_token = create_jwt_access_token(user.id)
    jwt_refresh_token = create_refresh_token()

    store_refresh_token(session, user_id=user.id, refresh_token=jwt_refresh_token)

    response = RedirectResponse("http://127.0.0.1:5173/home", status_code=303)
    set_refresh_token_cookie(response, jwt_refresh_token)

    return response


################## API ##################

@app.get("/api/session")
def get_session_info(
    response: Response,
    session: Session = Depends(get_session),
    refresh_token: str = Cookie(None),
    access_token: str = Cookie(None)
):
    if access_token:
        payload = verify_jwt(access_token)
        if payload:
            user = session.get(User, payload["sub"])
            if user:
                return {
                    "authenticated": True,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                    }
                }

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token"
        )

    token = get_refresh_token(session, refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # issue new short-lived access token
    new_access_token = create_jwt_access_token(token.user_id)

    # store it in a cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=False,   # or True if backend-only
        secure=True,
        samesite="Lax",
        max_age=15 * 60,  # 15 minutes
    )

    return {
        "authenticated": True,
        "user": {
            "id": token.user.id,
            "username": token.user.username,
        }
    }


def get_refresh_token(session: Session, refresh_token: str):
    token = session.exec(
        select(JWTToken)
        .where(JWTToken.refresh_token == refresh_token)
        .where(JWTToken.revoked == False)
        .where(JWTToken.expires_at > datetime.utcnow())
    ).first()

    return token

################### Pages ##################

@app.get("/api/user")
def get_newuser(session: Session = Depends(get_session), access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = verify_jwt(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = session.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check if new user
    if user.new_user:
        return {
            "is_new_user": True
        }

    return {
        "is_new_user": False
    }

@app.get("/api/onboarding")
def onboarding():
    return {
        "message": "New user onboarding step"
    }

################## Token Management ##################

# Verify JWT access token
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

#  Function for storing refresh token in HttpOnly cookie
def set_refresh_token_cookie(response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
    )
    return response


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def create_jwt_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def store_refresh_token(
    session: Session,
    user_id: int, 
    refresh_token: str, 
    lifetime_days: int = 30):

    expires_at = datetime.utcnow() + timedelta(days=lifetime_days)

    token_entry = JWTToken(
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
        revoked=False
    )

    session.add(token_entry)
    session.commit()
    session.refresh(token_entry)

    return token_entry

################## User Syncing with MAL ################## 

async def sync_mal_user(session: Session, access_token: str, refresh_token: str, expires_at: int):
    # 1. Fetch MAL user profile
    profile = await fetch_mal_user(access_token)
    
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

################## Generating ################## 

def generate_code_verifier():
    return secrets.token_urlsafe(64)

def generate_code_challenge(code_verifier: str):
    return code_verifier

def generate_state():
    return secrets.token_urlsafe(32)