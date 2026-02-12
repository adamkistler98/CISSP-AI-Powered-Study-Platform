import streamlit as st
import requests
import json
import os
import random
import time

st.set_page_config(
    page_title="CISSP Exam Simulator",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL STYLING (Pearson VUE Style) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Arial', sans-serif;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0056b3;
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #004494;
        color: white;
    }

    /* Headers */
    h1 { color: #2c3e50; font-size: 2rem; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    h2, h3 { color: #2c3e50; }

    /* Question Box */
    .question-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }

    /* Answer Area */
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- ROBUST BACKUP DATABASE (Standard Exam Questions) ---
BACKUP_DB = [
    {"type": "Multiple Choice", "text": "**Scenario:** A security architect is designing a solution for a company that requires strict separation of duties (SoD) for its cryptographic key management lifecycle.\n\n**Question:** Which of the following concepts BEST addresses this requirement?\n\n**Options:**\nA) Split Knowledge\nB) Key Escrow\nC) M of N Control\nD) Dual Control\n---\n**Correct Answer:** A\n**Explanation:** Split Knowledge requires that the knowledge of a key be split among multiple individuals so that no single person knows the entire key."},
    {"type": "Multiple Choice", "text": "**Scenario:** During a disaster recovery audit, the GRC team notes that the organization has a low tolerance for data loss but can tolerate a longer recovery time for non-critical systems. Transaction logs are backed up every 5 minutes.\n\n**Question:** Which metric is MOST likely being prioritized?\n\n**Options:**\nA) RTO (Recovery Time Objective)\nB) RPO (Recovery Point Objective)\nC) MTD (Maximum Tolerable Downtime)\nD) MTBF (Mean Time Between Failures)\n---\n**Correct Answer:** B\n**Explanation:** RPO defines the maximum amount of data (measured in time) that the organization is willing to lose."},
    {"type": "Multiple Choice", "text": "**Scenario:** An organization is implementing a mandatory access control (MAC) system based on the Bell-LaPadula model. A user with 'Secret' clearance attempts to read a document classified as 'Top Secret'.\n\n**Question:** Which property prevents this action?\n\n**Options:**\nA) Simple Security Property (No Read Up)\nB) *-Property (No Write Down)\nC) Strong Star Property\nD) Discretionary Access Property\n---\n**Correct Answer:** A\n**Explanation:** The Simple Security Property (ss-property) states 'No Read Up'. A subject at a lower security level cannot read an object at a higher security level."},
    {"type": "True/False", "text": "**Scenario:** An organization uses a warm site for disaster recovery.\n\n**Question:** True or False: A warm site contains fully operational hardware and real-time data replication.\n---\n**Correct Answer:** False\n**Explanation:** This describes a 'Hot Site'. A warm site has hardware but requires data restoration and configuration."},
    {"type": "Multiple Choice", "text": "**Scenario:** You are configuring a firewall rule set. You want to ensure that any traffic not explicitly allowed is blocked.\n\n**Question:** What is this security principle called?\n\n**Options:**\nA) Implicit Deny\nB) Explicit Allow\nC) Stateful Inspection\nD) Least Privilege\n---\n**Correct Answer:** A\n**Explanation:** Implicit Deny ensures that if a condition is not met (not on the allow list), the request is rejected by default."},
    {"type": "Executive Brief", "text": "**Scenario:** The Chief Information Security Officer (CISO) asks for a brief on the primary vulnerability of the Data Encryption Standard (DES).\n\n**Question:** What is the primary weakness of DES?\n---\n**Correct Answer:** Key Length (56-bit)\n**Explanation:** The 56-bit key space is too small for modern computing power and can be brute-forced in a very short time."},
    {"type": "Multiple Choice", "text": "**Scenario:** Assessing a SaaS (Software as a Service) provider. Who is responsible for patching the underlying Guest Operating System?\n\n**Options:**\nA) The Customer\nB) The Provider\nC) Shared Responsibility\nD) The Auditor\n---\n**Correct Answer:** B\n**Explanation:** In a SaaS model, the provider manages the entire stack, including the application, data (storage), OS, and hardware."},
]

# --- API SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Check_green_icon.svg/1024px-Check_green_icon.svg.png", width=50)
    st.title("Exam Controls")
    
    domain = st.selectbox("Domain:", [
        "1. Security & Risk Management", 
        "2. Asset Security", 
        "3. Security Architecture & Engineering", 
        "4. Communication & Network Security", 
        "5. Identity & Access Management (IAM)", 
        "6. Security Assessment & Testing", 
        "7. Security Operations", 
        "8. Software Development Security"
    ])
    
    difficulty = st.select_slider("Difficulty Level:", 
        options=["Associate", "Professional", "Expert"])
        
    q_type = st.selectbox("Question Type:", ["Multiple Choice", "True/False", "Executive Brief"])
    
    st.divider()
    st.caption("v2.0.4 | Stable Build")

# --- GENERATION LOGIC ---
def get_question():
    # 1. Try API First (Live Generation)
    if API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            prompt_map = {
                "Multiple Choice": "Format: Scenario + Question + 4 Options (A-D).",
                "True/False": "Format: Scenario + Statement + True/False Options.",
                "Executive Brief": "Format: Scenario + Open Ended Question."
            }
            
            prompt = f"""
            Act as a professional CISSP exam writer.
            Create a formal {difficulty} level question for the domain: {domain}.
            Type: {q_type}.
            {prompt_map[q_type]}
            
            Strict Output Format:
            **Scenario:** [Text]
            **Question:** [Text]
            **Options:** [List]
            ---
            **Correct Answer:** [Answer]
            **Explanation:** [Formal explanation citing standard principles]
            """
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            pass 
            
    # 2. Backup Logic (Silent Failover)
    # If API fails or is limited, we just grab a relevant question from the DB silently.
    filtered_db = [q for q in BACKUP_DB if q['type'] == q_type]
    if not filtered_db: filtered_db = BACKUP_DB 
    
    selection = random.choice(filtered_db)
    return selection['text']

# --- MAIN INTERFACE ---
st.title("CISSP / CISM Practice Exam")
st.markdown("Select your domain and difficulty from the sidebar to begin.")

if st.button("Generate New Question"):
    with st.spinner("Loading question..."):
        time.sleep(0.5) 
        st.session_state.current_question = get_question()

# --- DISPLAY ---
if "current_question" in st.session_state:
    try:
        parts = st.session_state.current_question.split("---")
        
        # Display Question
        st.markdown(f"<div class='question-box'>{parts[0]}</div>", unsafe_allow_html=True)
        
        # Display Answer
        with st.expander("Show Answer & Explanation"):
            st.markdown(parts[1] if len(parts) > 1 else "Error loading explanation.")
            
    except:
        st.write(st.session_state.current_question)
