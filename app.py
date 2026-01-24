from fastapi import FastAPI
from core import active_sessions

app = FastAPI()

@app.get("/")
def root():
    return {"message": "PyKV Session Store is running"}

@app.get("/sessions")
def get_sessions():
    return {"active_sessions": active_sessions}
