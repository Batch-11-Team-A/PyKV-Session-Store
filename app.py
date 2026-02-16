from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from engine import create_session, get_session, delete_session, active_sessions
import time

app = FastAPI()

# Serve frontend folder
app.mount("/FRONTEND", StaticFiles(directory="FRONTEND"), name="FRONTEND")


# -------- HOME PAGE --------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("FRONTEND/index.html", "r", encoding="utf-8") as f:
        return f.read()


session_counter = 0


# -------- LOGIN (CREATE SESSION) --------
@app.post("/login")
def login(username: str = Form(...)):
    global session_counter
    session_counter += 1

    token = f"session_{session_counter}"

    # 15 minutes session
    create_session(token, {"username": username}, ttl=900)

    return {"session_token": token}


# -------- GET SINGLE SESSION --------
@app.get("/session/{token}")
def get_session_api(token: str):
    session = get_session(token)

    if not session:
        return {"error": "Session expired"}

    return session


# -------- LOGOUT --------
@app.delete("/logout/{token}")
def logout(token: str):
    delete_session(token)
    return {"message": "Logged out successfully"}


# -------- ADMIN PANEL - VIEW ALL SESSIONS --------
@app.get("/all-sessions")
def view_all_sessions():
    sessions_data = {}

    for token, session in active_sessions.items():

        remaining = int(session["expires_at"] - time.time())

        sessions_data[token] = {
            "username": session["user_data"]["username"],
            "remaining_seconds": remaining if remaining > 0 else 0,
            "status": "Active" if remaining > 0 else "Expired"
        }

    return sessions_data
