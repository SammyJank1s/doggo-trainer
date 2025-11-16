import streamlit as st
import requests
import json

# --- Konfiguration ---
BACKEND_URL = st.secrets["BACKEND_URL"]

# --- Session State ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# --- Funktionen ---
def login(email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user = data
            st.success("Login erfolgreich!")
            st.rerun()
        else:
            st.error(f"Login fehlgeschlagen: {response.json().get('error', 'Unbekannt')}")
    except Exception as e:
        st.error(f"Fehler: {e}")

def get_user_data():
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{BACKEND_URL}/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Konnte Nutzerdaten nicht laden")
            return None
    except:
        return None

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

# --- UI ---
st.title("Doggo Trainer")

if not st.session_state.token:
    # --- LOGIN FORM ---
    st.header("Anmelden")
    with st.form("login_form"):
        email = st.text_input("E-Mail")
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Einloggen")
        if submit:
            login(email, password)

    st.markdown("---")
    st.write("Noch kein Konto?")
    with st.expander("Registrieren"):
        with st.form("register_form"):
            reg_email = st.text_input("E-Mail", key="reg_email")
            reg_password = st.text_input("Passwort", type="password", key="reg_password")
            reg_name = st.text_input("Dein Name", key="reg_name")
            reg_dog = st.text_input("Hundename", key="reg_dog")
            reg_submit = st.form_submit_button("Registrieren")
            if reg_submit:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/register",
                        json={
                            "email": reg_email,
                            "password": reg_password,
                            "name": reg_name,
                            "dog_name": reg_dog
                        }
                    )
                    if response.status_code == 200:
                        st.success("Registriert! Jetzt einloggen.")
                    else:
                        st.error(response.json().get("error", "Fehler"))
                except Exception as e:
                    st.error(f"Fehler: {e}")

else:
    # --- DASHBOARD ---
    st.sidebar.success(f"Eingeloggt als {st.session_state.user['email']}")
    if st.sidebar.button("Abmelden"):
        logout()

    st.header(f"Willkommen, {st.session_state.user['email']}!")
    
    user_data = get_user_data()
    if user_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Hundename", user_data.get("dog_name", "Unbekannt"))
        with col2:
            st.metric("Level", user_data.get("level", 1))
        
        st.write("### Dein Fortschritt")
        st.progress(user_data.get("points", 0) / 100)
        st.write(f"**{user_data.get('points', 0)} XP** – Nächstes Level bei 100 XP")

    st.info("Mehr Features (Aufgaben, Badges) kommen in TAG 4!")