"""
engine.py

Core session engine for PyKV.

This module manages user login sessions for a web application.
It stores active sessions in memory for fast access and ensures
thread-safe operations when multiple users access the system
at the same time.

Key responsibilities:
- Store active user sessions
- Prevent data corruption during concurrent access
- Automatically expire sessions using TTL
- Expose helper functions for persistence and recovery
"""

import threading
import time

# In-memory session storage
# Each session token maps to user-related data.
# Primary in-memory hash map for active user sessions
# Format: { "token_string": {"payload": {}, "timestamp": float, "expires": float} }

active_sessions = {}

# Lock to ensure only one thread modifies session data at a time
session_lock = threading.Lock()

# Create / Update session
def create_session(session_token, user_data, ttl=None):
    """
    Create a new user session or update an existing one.

    :parameter session_token: unique session identifier
    :parameter user_data: information related to the logged-in user
    :parameter ttl: session lifetime in seconds (optional)
    """
    with session_lock:
        current_time = time.time()
        expiry_time = current_time + ttl if ttl else None

        active_sessions[session_token] = {
            "user_data": user_data,
            "created_at": current_time,
            "expires_at": expiry_time
        }

# Fetch session
def get_session(session_token):
    """
    Retrieve user data for a given session token.
    Automatically removes expired sessions.

    :parameter session_token: unique session identifier
    :return: user data if session is valid, otherwise None
    """
    with session_lock:
        session = active_sessions.get(session_token)

        if not session:
            return None

       #check whether the session has expired
        if session["expires_at"] and time.time() > session["expires_at"]:
            del active_sessions[session_token]
            return None

        return session["user_data"]

# Remove session (logout)
def delete_session(session_token):
    """
    Remove a session explicitly (used during logout).

    :parameter session_token: unique session identifier
    """
    with session_lock:
        if session_token in active_sessions:
            del active_sessions[session_token]

# Persistence support
def export_sessions():
    """
    Provide a snapshot of all active sessions.
    Used by persistence layer to save data to disk.
    """
    with session_lock:
        return active_sessions.copy()


def import_sessions(saved_sessions):
    """
    Restore sessions from persistent storage during startup.

    :parameter saved_sessions: dictionary loaded from disk
    """
    with session_lock:
        active_sessions.clear()
        active_sessions.update(saved_sessions)

# Local check
if __name__ == "__main__":
    print("Starting PyKV session engine test...")

    create_session("token_123", {"user_id": 101}, ttl=5)
    print("Session fetch (valid):", get_session("token_123"))

    time.sleep(6)
    print("Session fetch (expired):", get_session("token_123"))

    create_session("token_456", {"user_id": 202})
    delete_session("token_456")
    print("Session fetch (deleted):", get_session("token_456"))

    print("Session engine test completed successfully.")
