from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from supabase import create_client
#Environment variablen laden
load_dotenv()

app = FastAPI(title="Doggo Trainer API", version="0.1.0")

supabase = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_ANON_KEY"))
#CORS erlauben (für Streamlit)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Später einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Doggo Trainer API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/test-db")
def test_db():
    try:
        data = supabase.table("users").select("*").limit(1).execute()
        return {"db_connected": True, "data": data.data}
    except Exception as e:
        return {"db_connected": False, "error": str(e)}