"""
app.py

API layer for PyKV session engine.
This module exposes REST endpoints for login, session validation,
and logout, allowing external clients to interact with the
in-memory session store through HTTP.
"""

from fastapi import FastAPI
import uuid

# Import engine functions (THIS is the connection)
from engine import create_session, get_session, delete_session

app = FastAPI()

# LOGIN → create session
@app.post("/login")
def login(username: str):
    session_token = str(uuid.uuid4())

    user_data = {
        "username": username
    }

    # Create session with TTL = 300 seconds (5 minutes)
    create_session(session_token, user_data, ttl=300)

    return {
        "message": "Login successful",
        "session_token": session_token
    }

# GET SESSION → check if user is logged in
@app.get("/session/{session_token}")
def fetch_session(session_token: str):
    data = get_session(session_token)

    if data is None:
        return {"error": "Session expired or not found"}

    return data

# LOGOUT → delete session
@app.delete("/logout/{session_token}")
def logout(session_token: str):
    delete_session(session_token)
    return {"message": "Logged out successfully"}