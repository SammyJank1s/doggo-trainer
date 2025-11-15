from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Doggo Trainer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

@app.get("/")
def home():
    return {"message": "Doggo Trainer API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test-db")
def test_db():
    try:
        data = supabase.table("users").select("*").execute()
        return {"db_connected": True, "data": data.data}
    except Exception as e:
        return {"db_connected": False, "error": str(e)}

@app.post("/test-insert")
def test_insert():
    try:
        data = supabase.table("users").insert({
            "email": "test@hund.de",
            "name": "Max",
            "dog_name": "Bello"
        }).execute()
        return {"inserted": data.data}
    except Exception as e:
        return {"error": str(e)}

# Browser-freundlicher GET-Endpoint
@app.get("/test-insert")
def test_insert_get():
    return {
        "message": "This endpoint only accepts POST requests!",
        "how_to_test": "Use curl:",
        "command": "curl -X POST http://localhost:8000/test-insert"
    }