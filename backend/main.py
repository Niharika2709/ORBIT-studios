import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ORBIT Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_seed():
    with open("seed.json", encoding="utf-8") as f:
        return json.load(f)

STATE = load_seed()  # in-memory for now; SQLite comes next

@app.get("/state")
def get_state():
    return STATE

@app.post("/reset")
def reset():
    global STATE
    STATE = load_seed()
    return STATE