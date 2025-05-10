from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import models, schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import base64
import hashlib
import secrets
from models import OAuthSession, Users
from fastapi.responses import RedirectResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

API_URL = os.getenv("URL")
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Create table on start up
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=engine)


# Auth
@app.get("/oauth")
async def oauth_login(db: Session = Depends(get_db)):

    # Generate token for oauth
    user_session = generate_session_token()
    oauth_state = generate_state() # TODO store in frontend
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Store values
    store_oauth_session(db, user_session, oauth_state, code_verifier)

    # Redirect user
    auth_url = (
        f"https://myanimelist.net/v1/oauth2/authorize"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&state={oauth_state}&redirect_uri={API_URL}oauth/callback"
        f"&code_challenge={code_challenge}&code_challenge_method=plain"
    )

    return RedirectResponse(auth_url)

# Store the Auth session
def store_oauth_session(db: Session, session_id: str, state: str, code_verifier: str):
    oauth = OAuthSession(
        session_id=session_id,
        oauth_state=state,
        code_verifier=code_verifier
    )
    db.add(oauth)
    db.commit()

# Generate random state
def generate_state(length: int = 32) -> str:
    import secrets
    return secrets.token_urlsafe(length)[:length]

# Generate a session token
def generate_session_token(length: int = 64) -> str:
    token = secrets.token_urlsafe(length)
    return token[:length]

# Generate Code Verifier
def generate_code_verifier(length: int = 128) -> str:
    verifier = secrets.token_urlsafe(length)
    return verifier[:128]

# Generate Code Challenge
def generate_code_challenge(code_verifier: str) -> str:
    sha256 = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(sha256).decode("utf-8").rstrip("=")
    return challenge