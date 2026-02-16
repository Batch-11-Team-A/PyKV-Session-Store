import threading
import time
import json
import os

active_sessions = {}
session_lock = threading.Lock()
SESSION_FILE = "sessions.json"


# -------- ENSURE JSON FILE EXISTS --------
def ensure_file():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            json.dump({}, f)


# -------- SAVE TO JSON --------
def save_sessions():
    with open(SESSION_FILE, "w") as f:
        json.dump(active_sessions, f, indent=4)


# -------- LOAD FROM JSON --------
def load_sessions():
    global active_sessions
    ensure_file()
    with open(SESSION_FILE, "r") as f:
        try:
            active_sessions = json.load(f)
        except:
            active_sessions = {}


# -------- CLEAN EXPIRED SESSIONS --------
def cleanup_expired_sessions():
    while True:
        time.sleep(30)
        with session_lock:
            expired_tokens = [
                token for token, session in active_sessions.items()
                if time.time() > session["expires_at"]
            ]

            for token in expired_tokens:
                del active_sessions[token]

            if expired_tokens:
                save_sessions()


# -------- CREATE SESSION --------
def create_session(session_token, user_data, ttl=900):  # 15 min
    with session_lock:
        active_sessions[session_token] = {
            "user_data": user_data,
            "created_at": time.time(),
            "expires_at": time.time() + ttl
        }
        save_sessions()


# -------- GET SESSION --------
def get_session(session_token):
    with session_lock:
        session = active_sessions.get(session_token)

        if session is None:
            return None

        if time.time() > session["expires_at"]:
            del active_sessions[session_token]
            save_sessions()
            return None

        remaining = int(session["expires_at"] - time.time())

        return {
            "user_data": session["user_data"],
            "remaining_seconds": remaining
        }


# -------- DELETE SESSION --------
def delete_session(session_token):
    with session_lock:
        if session_token in active_sessions:
            del active_sessions[session_token]
            save_sessions()


# On server start
load_sessions()

# Start background cleaner
cleaner_thread = threading.Thread(target=cleanup_expired_sessions, daemon=True)
cleaner_thread.start()