import streamlit as st
from google import genai
import os

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
    div[data-testid="stExpander"] { border: 1px solid #30363D; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- API SETUP (NEW SDK) ---
try:
    # Try getting key from Streamlit Secrets first
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Fallback to local environment variable
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ SYSTEM ALERT: API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize the new Client
client = genai.Client(api_key=api_key)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ COMMAND CENTER")
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
    st.divider()
    st.caption("System Status: **ONLINE**")

# --- MAIN APP ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

if st.button("GENERATE NEW SCENARIO"):
    with st.spinner("Initializing Neural Network..."):
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
        
        try:
            # NEW SDK CALL SYNTAX
            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt
            )
            st.session_state.current_question = response.text
        except Exception as e:
            # Fallback to stable model if Flash fails
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash', 
                    contents=prompt
                )
                st.session_state.current_question = response.text
            except Exception as e2:
                st.error(f"Connection Failed: {str(e2)}")

# --- DISPLAY ---
if "current_question" in st.session_state and st.session_state.current_question:
    try:
        parts = st.session_state.current_question.split("---")
        st.markdown(parts[0])
        with st.expander("REVEAL OFFICIAL ANSWER"):
            st.markdown(parts[1] if len(parts) > 1 else "Check raw output.")
    except:
        st.markdown(st.session_state.current_question)
