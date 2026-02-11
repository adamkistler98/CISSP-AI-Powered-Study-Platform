import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CyberPrep AI | CISSP Architect",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING (Dark Mode Optimization) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #262730;
        color: #ffffff;
        border: 1px solid #4B4B4B;
    }
    .stButton>button:hover {
        border-color: #00FF00;
        color: #00FF00;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #30363D;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
# Try to get key from Streamlit Secrets (Cloud) or Environment (Local)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ SYSTEM ALERT: API Key missing. Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- SESSION STATE ---
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ COMMAND CENTER")
    st.caption("CISSP | CCSP | CISM Prep")
    
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
    
    difficulty = st.select_slider(
        "Simulation Difficulty",
        options=["Associate", "Professional", "Chief Architect"]
    )
    
    st.divider()
    st.info(f"Mode: **{difficulty}**\n\nSystem Status: **ONLINE**")

# --- MAIN APP LOGIC ---
st.title("CYBERPREP // AI")
st.markdown("### GRC & Security Architecture Simulator")

def generate_scenario():
    with st.spinner("Initializing Neural Network... Analyzing Compliance Standards..."):
        prompt = f"""
        Act as a strict CISSP exam board creator. 
        Create a {difficulty}-level scenario question for the domain: {selected_domain}.
        
        The question must require critical thinking, not just memorization.
        Include references to specific NIST SP 800-series or ISO 27001 controls where relevant.
        
        Format the output exactly like this:
        **SCENARIO:** [The scenario text]
        
        **QUESTION:** [The question text]
        
        **OPTIONS:**
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        
        ---
        **CORRECT ANSWER:** [Option Letter]
        **EXPLANATION:** [Detailed justification explaining why the wrong answers are wrong, citing standards]
        """
        
        try:
            response = model.generate_content(prompt)
            st.session_state.current_question = response.text
        except Exception as e:
            st.error(f"API Connection Failed: {e}")

if st.button("GENERATE NEW SCENARIO"):
    generate_scenario()

# --- DISPLAY AREA ---
if st.session_state.current_question:
    # We split the response to hide the answer initially
    # This assumes the AI follows the format "---" requested in the prompt
    try:
        parts = st.session_state.current_question.split("---")
        question_part = parts[0]
        answer_part = parts[1] if len(parts) > 1 else "Analysis generation failed. Check raw output."
        
        st.markdown("---")
        st.markdown(question_part)
        
        st.markdown("### 🔐 Decryption Key")
        with st.expander("REVEAL OFFICIAL ANSWER & ANALYSIS"):
            st.markdown(answer_part)
            
    except Exception:
        st.warning("Raw Output (Parsing failed but data is valid):")
        st.write(st.session_state.current_question)

else:
    st.markdown("""
    <div style="text-align: center; color: #555; margin-top: 50px;">
        AWAITING INPUT...<br>
        SELECT DOMAIN AND INITIALIZE SCENARIO
    </div>
    """, unsafe_allow_html=True)
