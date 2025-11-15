from fastapi import FastAPI, Header, Depends, HTTPException, Body
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

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# --- JWT Schutz ---
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Kein Token")
    try:
        token = authorization.split(" ")[1]
        user = supabase.auth.get_user(token)
        return user.user
    except:
        raise HTTPException(401, "Ungültiges Token")

# --- Auth Endpoints ---
@app.post("/register")
def register(email: str = Body(...), password: str = Body(...), name: str = Body(...), dog_name: str = Body(...)):
    try:
        auth_res = supabase.auth.sign_up({"email": email, "password": password})
        if auth_res.user:
            supabase.table("users").insert({
                "id": auth_res.user.id,
                "email": email,
                "name": name,
                "dog_name": dog_name
            }).execute()
            return {"message": "Registrierung erfolgreich!", "user_id": auth_res.user.id}
        else:
            return {"error": "Registrierung fehlgeschlagen"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    try:
        auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {
            "access_token": auth_res.session.access_token,
            "user_id": auth_res.user.id,
            "email": auth_res.user.email
        }
    except Exception as e:
        return {"error": "Login fehlgeschlagen: " + str(e)}

# --- Geschützter Test-Insert (ersetzt den alten!) ---
@app.get("/me")
def get_me(current_user = Depends(get_current_user)):
    try:
        user_data = supabase.table("users").select("*").eq("id", current_user.id).execute()
        if user_data.data:
            return user_data.data[0]
        else:
            return {"error": "Nutzer nicht in DB"}
    except Exception as e:
        return {"error": str(e)}

# --- Öffentliche Endpoints ---
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