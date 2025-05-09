from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models, schemas
from database import engine
from dotenv import load_dotenv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

# Create table on start up
@app.on_event("startup")
def startup():
    models.Base.metadata.create_all(bind=engine)

# Auth
@app.get("/oauth")
def oauth_login():


    return {"message": "Start OAuth"}


# Generate Code Verifier


# Generate Code Challenge
