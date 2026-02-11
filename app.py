import streamlit as st
import requests
import json
import os
import random
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="STRATAGEM | GRC Intel",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STEALTH MODE LOGIC ---
if "stealth_mode" not in st.session_state:
    st.session_state.stealth_mode = False

def toggle_stealth():
    st.session_state.stealth_mode = not st.session_state.stealth_mode

# --- CUSTOM CSS (Dynamic) ---
if st.session_state.stealth_mode:
    # BORING MODE (Looks like server logs)
    st.markdown("""
    <style>
        .stApp { background-color: #f0f2f6; color: #333; font-family: monospace; }
        .stButton>button { background-color: #e0e0e0; color: #000; border: 1px solid #ccc; }
        .highlight { color: #000; font-weight: bold; }
        .status-ok { color: green; }
        .status-err { color: red; }
    </style>
    """, unsafe_allow_html=True)
else:
    # COOL CYBER MODE
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #00FF41; font-family: 'Courier New', monospace; }
        .stButton>button { width: 100%; border-radius: 0px; background-color: #000; color: #00FF41; border: 1px solid #00FF41; }
        .stButton>button:hover { background-color: #003300; box-shadow: 0 0 10px #00FF41; }
        .stSelectbox, .stSlider { color: #00FF41; }
        div[data-testid="stExpander"] { border: 1px solid #00FF41; border-radius: 0px; background-color: #000; }
        h1, h2, h3 { color: #FAFAFA; text-shadow: 0 0 5px #00FF41; }
        .status-ok { color: #00FF41; }
        .status-err { color: #FF0000; }
    </style>
    """, unsafe_allow_html=True)

# --- EXPANDED LOCAL DATABASE (The "Offline" Fix) ---
# Now contains 15+ questions so "Backup Mode" isn't boring.
BACKUP_DB = [
    {"type": "Multiple Choice", "text": "**SCENARIO:** SoD requires separation of cryptographic key duties.\n**QUESTION:** Which concept BEST addresses this?\n**OPTIONS:**\nA) Split Knowledge\nB) Key Escrow\nC) M of N Control\nD) Dual Control\n---\n**CORRECT:** A\n**WHY:** Split Knowledge ensures no single person knows the whole key."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** Logs are backed up every 5 minutes.\n**QUESTION:** Which metric is prioritized?\n**OPTIONS:**\nA) RTO\nB) RPO\nC) MTD\nD) MTBF\n---\n**CORRECT:** B\n**WHY:** RPO defines data loss tolerance (time)."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** User with 'Secret' clearance tries to read 'Top Secret'.\n**QUESTION:** Bell-LaPadula property preventing this?\n**OPTIONS:**\nA) Simple Security (No Read Up)\nB) *-Property (No Write Down)\nC) Strong Star\nD) Discretionary Access\n---\n**CORRECT:** A\n**WHY:** Simple Security Property forbids reading up."},
    {"type": "True/False", "text": "**SCENARIO:** An organization uses a warming site for DR.\n**QUESTION:** True or False: A warm site contains fully operational hardware and real-time data replication.\n---\n**CORRECT:** False\n**WHY:** That describes a 'Hot Site'. A warm site has hardware but requires data restoration."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** Implementing OAuth 2.0 for API security.\n**QUESTION:** Which grant type is BEST for a mobile app without a backend server?\n**OPTIONS:**\nA) Authorization Code\nB) Implicit\nC) Client Credentials\nD) PKCE\n---\n**CORRECT:** D (PKCE)\n**WHY:** Authorization Code with PKCE is the modern standard for public clients (mobile apps) to prevent interception."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** Configuring a firewall. You want to block all traffic that is not explicitly allowed.\n**QUESTION:** What is this principle called?\n**OPTIONS:**\nA) Implicit Deny\nB) Explicit Allow\nC) Statefull Inspection\nD) Least Privilege\n---\n**CORRECT:** A\n**WHY:** Implicit Deny ensures anything not on the list is blocked by default."},
    {"type": "Executive Brief", "text": "**SCENARIO:** The CEO asks why we need to move from DES to AES encryption.\n**QUESTION:** In one sentence, what is the primary vulnerability of DES?\n---\n**CORRECT:** Key space is too small (56-bit).\n**WHY:** DES can be brute-forced in hours due to short key length. AES uses 128/256-bit keys."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** Assessing a cloud provider (SaaS). Who is responsible for patching the Guest OS?\n**OPTIONS:**\nA) The Customer\nB) The Provider\nC) Shared\nD) The Auditor\n---\n**CORRECT:** B\n**WHY:** In SaaS, the provider manages everything up to the application layer, including the OS."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** A hacker uses a 'Pass the Hash' attack.\n**QUESTION:** Which protocol is primarily vulnerable to this?\n**OPTIONS:**\nA) Kerberos\nB) NTLM\nC) SAML\nD) OIDC\n---\n**CORRECT:** B\n**WHY:** NTLM does not salt the hash, allowing attackers to replay it without cracking it."},
    {"type": "True/False", "text": "**SCENARIO:** You are conducting a Black Box penetration test.\n**QUESTION:** True or False: You are provided with full network diagrams and source code.\n---\n**CORRECT:** False\n**WHY:** Black Box means zero prior knowledge. White Box provides diagrams/code."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** Implementing a DLP solution to stop credit card data exfiltration.\n**QUESTION:** Looking for the pattern '4xxx-xxxx-xxxx-xxxx' is an example of?\n**OPTIONS:**\nA) Regular Expression (Regex) Matching\nB) Exact File Matching\nC) Fingerprinting\nD) Heuristic Analysis\n---\n**CORRECT:** A\n**WHY:** Regex finds patterns. Exact matching looks for specific file hashes."},
    {"type": "Multiple Choice", "text": "**SCENARIO:** A developer wants to ensure code integrity before deployment.\n**QUESTION:** Which tool is best?\n**OPTIONS:**\nA) Code Signing\nB) TLS\nC) Hashing\nD) Obfuscation\n---\n**CORRECT:** A\n**WHY:** Code Signing uses a digital signature to prove identity and integrity."},
]

# --- API SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    API_KEY = os.getenv("GEMINI_API_KEY")

# --- SIDEBAR ---
with st.sidebar:
    st.title("📡 INTEL FEED")
    
    # Stealth Toggle
    st.toggle("STEALTH MODE (BOSS KEY)", value=st.session_state.stealth_mode, on_change=toggle_stealth)
    
    st.divider()
    
    # Controls
    domain = st.selectbox("Domain:", [
        "1. Security & Risk Management", "2. Asset Security", 
        "3. Security Architecture", "4. Network Security", 
        "5. IAM", "6. Assessment & Testing", 
        "7. Sec Operations", "8. Software Sec"
    ])
    
    difficulty = st.select_slider("Threat Level:", 
        options=["Script Kiddie", "Professional", "CISO", "Nation State Actor"])
        
    q_type = st.selectbox("Format:", ["Multiple Choice", "True/False", "Executive Brief"])
    
    st.divider()
    
    # Connection Status
    if API_KEY:
        st.caption("Uplink: **ENCRYPTED**")
    else:
        st.error("Uplink: **MISSING KEYS**")

# --- GENERATION LOGIC ---
def get_intel():
    # 1. Try API First
    if API_KEY:
        try:
            # We force 1.5 Flash (Highest Free Quota)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            prompt_map = {
                "Multiple Choice": "Format: Question + 4 Options (A-D) + Answer/Explanation.",
                "True/False": "Format: Statement + True/False Options + Correct Answer.",
                "Executive Brief": "Format: Scenario + Open Ended Question + Model Answer."
            }
            
            prompt = f"""
            Role: CISSP Exam Proctor.
            Task: Create a unique {difficulty} difficulty question.
            Topic: {domain}.
            Type: {q_type}.
            {prompt_map[q_type]}
            
            Output strictly as:
            **SCENARIO:** [Text]
            **QUESTION:** [Text]
            **OPTIONS:** [List if applicable]
            ---
            **CORRECT:** [Answer]
            **WHY:** [Explanation with NIST/ISO reference]
            """
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text'], "LIVE_FEED"
        except:
            pass # Fail silently to backup
            
    # 2. Backup Logic (Circuit Breaker)
    # Filter DB by type to make it look smarter
    filtered_db = [q for q in BACKUP_DB if q['type'] == q_type]
    if not filtered_db: filtered_db = BACKUP_DB # Fallback to all if type match fails
    
    selection = random.choice(filtered_db)
    return selection['text'], "LOCAL_CACHE"

# --- MAIN INTERFACE ---
if st.session_state.stealth_mode:
    st.header("SYSTEM LOGS: /var/log/audit.d")
else:
    st.title("STRATAGEM // GRC NEXUS")
    st.markdown("### 🛡️ Adaptive Learning Architecture")

if st.button("INITIATE SEQUENCE" if not st.session_state.stealth_mode else "Refresh Logs"):
    with st.spinner("Decrypting..." if not st.session_state.stealth_mode else "Loading..."):
        # Artificial delay for drama (and to prevent double-clicking)
        time.sleep(0.5) 
        result, source = get_intel()
        st.session_state.current_intel = result
        st.session_state.source = source

# --- DISPLAY ---
if "current_intel" in st.session_state:
    # Source Indicator
    if not st.session_state.stealth_mode:
        if st.session_state.source == "LIVE_FEED":
            st.markdown("`<small style='color:#00FF41'>[●] LIVE SATELLITE FEED</small>`", unsafe_allow_html=True)
        else:
            st.markdown("`<small style='color:#FFA500'>[⚠] OFFLINE CACHE (API LIMIT REACHED)</small>`", unsafe_allow_html=True)

    # Content
    try:
        parts = st.session_state.current_intel.split("---")
        st.markdown(parts[0])
        
        with st.expander("DECRYPT ANSWER" if not st.session_state.stealth_mode else "View Details"):
            st.markdown(parts[1] if len(parts) > 1 else "Data Corrupted.")
    except:
        st.markdown(st.session_state.current_intel)
