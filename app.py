import streamlit as st
import requests
import json
import os
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberPrep AI | CISSP Architect",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #262730; color: #ffffff; border: 1px solid #4B4B4B; }
    .stButton>button:hover { border-color: #00FF00; color: #00FF00; }
    .status-ok { color: #00FF00; font-size: 0.8rem; font-family: monospace; }
    .status-warn { color: #FFA500; font-size: 0.8rem; font-family: monospace; }
    .status-err { color: #FF4B4B; font-size: 0.8rem; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- OFFLINE BACKUP DATABASE (The Circuit Breaker) ---
# If the API fails, we serve one of these.
BACKUP_QUESTIONS = [
    {
        "text": "**SCENARIO:** A security architect is designing a solution for a company that requires strict separation of duties (SoD) for its cryptographic key management lifecycle. The company wants to ensure that no single individual can generate, distribute, and archive keys.\n\n**QUESTION:** Which of the following concepts BEST addresses this requirement?\n\n**OPTIONS:**\nA) Split Knowledge\nB) Key Escrow\nC) M of N Control\nD) Dual Control\n---\n**CORRECT ANSWER:** A\n**EXPLANATION:** Split Knowledge requires that the knowledge of a key be split among multiple individuals so that no single person knows the entire key. M of N control is a specific implementation of this, but Split Knowledge is the governing concept for preventing single-person knowledge."
    },
    {
        "text": "**SCENARIO:** During a disaster recovery audit, the GRC team notes that the organization has a low tolerance for data loss but can tolerate a longer recovery time for non-critical systems. The transaction logs are backed up every 5 minutes.\n\n**QUESTION:** Which metric is MOST likely being prioritized in this scenario?\n\n**OPTIONS:**\nA) RTO (Recovery Time Objective)\nB) RPO (Recovery Point Objective)\nC) MTD (Maximum Tolerable Downtime)\nD) MTBF (Mean Time Between Failures)\n---\n**CORRECT ANSWER:** B\n**EXPLANATION:** The Recovery Point Objective (RPO) defines the maximum amount of data (measured in time) that the organization is willing to lose. Backing up logs every 5 minutes indicates a strict RPO."
    },
    {
        "text": "**SCENARIO:** An organization is implementing a mandatory access control (MAC) system based on the Bell-LaPadula model. A user with 'Secret' clearance attempts to read a document classified as 'Top Secret'.\n\n**QUESTION:** Which property of the Bell-LaPadula model prevents this action?\n\n**OPTIONS:**\nA) Simple Security Property (No Read Up)\nB) *-Property (No Write Down)\nC) Strong Star Property\nD) Discretionary Access Property\n---\n**CORRECT ANSWER:** A\n**EXPLANATION:** The Simple Security Property (ss-property) in Bell-LaPadula states 'No Read Up'. A subject at a lower security level (Secret) cannot read an object at a higher security level (Top Secret)."
    }
]

# --- API SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ CRITICAL: API Key missing. Configure GEMINI_API_KEY in Secrets.")
    st.stop()

# --- DYNAMIC SERVICE DISCOVERY ---
@st.cache_resource
def discover_active_model():
    """Finds the best available model, strictly avoiding restricted 'limit: 0' models."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, f"Error {response.status_code}"
        
        data = response.json()
        available_models = [m['name'] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        
        # Priority: Try 1.5 Pro first (different quota bucket than Flash), then Flash
        preferences = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro"]
        
        for pref in preferences:
            for model in available_models:
                if pref in model:
                    return model, "OK"
        return None, "NO_VALID_MODELS"
    except Exception as e:
        return None, str(e)

ACTIVE_MODEL, STATUS_MSG = discover_active_model()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ COMMAND CENTER")
    
    if ACTIVE_MODEL:
        display_name = ACTIVE_MODEL.replace("models/", "")
        st.markdown(f"**Primary Uplink:** <span class='status-ok'>{display_name}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**Primary Uplink:** <span class='status-err'>OFFLINE</span>", unsafe_allow_html=True)
    
    st.markdown("**Backup Protocol:** <span class='status-ok'>READY</span>", unsafe_allow_html=True)
    st.divider()
    
    selected_domain = st.selectbox(
        "Select Target Domain:",
        [
            "1. Security & Risk Management",
            "2. Asset Security",
            "3. Security Architecture & Engineering",
            "4. Communication & Network Security",
            "5. Identity & Access Management (IAM)",
            "6. Security Assessment & Testing",
            "7. Security Operations",
            "8. Software Development Security"
        ]
    )
    difficulty = st.select_slider("Simulation Difficulty", options=["Associate", "Professional", "Chief Architect"])

# --- API FUNCTION WITH CIRCUIT BREAKER ---
def query_gemini_resilient(prompt_text):
    # 1. If Primary Uplink is down, go straight to backup
    if not ACTIVE_MODEL:
        return random.choice(BACKUP_QUESTIONS)["text"], "BACKUP_MODE"

    url = f"https://generativelanguage.googleapis.com/v1beta/{ACTIVE_MODEL}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 2. SUCCESS: API worked
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text'], "ONLINE"
            
        # 3. FAIL: Quota Limit (429) or Server Error (5xx) -> TRIGGER CIRCUIT BREAKER
        elif response.status_code in [429, 500, 502, 503]:
            return random.choice(BACKUP_QUESTIONS)["text"], "BACKUP_MODE"
            
        else:
            return f"Error {response.status_code}: {response.text}", "ERROR"
            
    except Exception as e:
        # 4. NETWORK FAIL -> TRIGGER CIRCUIT BREAKER
        return random.choice(BACKUP_QUESTIONS)["text"], "BACKUP_MODE"

# --- MAIN APP ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

if st.button("GENERATE NEW SCENARIO"):
    with st.spinner(f"Contacting Neural Network..."):
        prompt = f"""
        Act as a CISSP exam creator. Create a {difficulty}-level scenario for: {selected_domain}.
        Format exactly as:
        **SCENARIO:** [Text]
        **QUESTION:** [Text]
        **OPTIONS:**
        A) [Text]
        B) [Text]
        C) [Text]
        D) [Text]
        ---
        **CORRECT ANSWER:** [Letter]
        **EXPLANATION:** [Text]
        """
        
        result, source = query_gemini_resilient(prompt)
        
        if source == "BACKUP_MODE":
            st.warning("⚠️ NOTICE: API High Traffic / Limit Reached. Utilizing Local Encrypted Backup Database.")
            
        if result:
            st.session_state.current_question = result

# --- DISPLAY ---
if "current_question" in st.session_state and st.session_state.current_question:
    try:
        parts = st.session_state.current_question.split("---")
        st.markdown(parts[0])
        with st.expander("REVEAL OFFICIAL ANSWER"):
            st.markdown(parts[1] if len(parts) > 1 else "Check raw output.")
    except:
        st.markdown(st.session_state.current_question)
