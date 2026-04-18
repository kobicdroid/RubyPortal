import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import os
import glob  
import random
from datetime import datetime
import qrcode 
import plotly.express as px 
import zipfile
from io import BytesIO
import base64
import gc
import plotly.graph_objects as go
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ast 
import time
import requests 
import streamlit.components.v1 as components 


# =================================================================
# --- GHOST PROTOCOL: TOTAL STEALTH MODE ---
# =================================================================
import streamlit as st
from datetime import datetime

# --- LIVE TICKING ENGINE ---
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, key="maintenance_tick")
except ImportError:
    pass

MAINTENANCE_MODE = True  
ADMIN_SECRET_KEY = "SUMI" 
TARGET_DATE = datetime(2026, 4, 20, 8, 0) 

# --- SESSION STATE ---
if 'maintenance_bypass' not in st.session_state:
    st.session_state.maintenance_bypass = False
if 'ghost_unlocked' not in st.session_state:
    st.session_state.ghost_unlocked = False

# --- AUTO-UNLOCK LOGIC ---
now = datetime.now()
diff = TARGET_DATE - now
if diff.total_seconds() <= 0:
    st.session_state.maintenance_bypass = True

if MAINTENANCE_MODE and not st.session_state.maintenance_bypass:
    st.set_page_config(page_title="RSC | System Maintenance", page_icon="🚧", layout="centered")
    
    # Calculate Timer Display
    days = max(0, diff.days)
    hours, remainder = divmod(max(0, diff.seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    timer_display = f"{days:02d}d : {hours:02d}h : {minutes:02d}m : {seconds:02d}s"

    # 1. --- THE STYLE BLOCK (HIDING THE VISIBLE BUTTON) ---
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap');
        .stApp { background: radial-gradient(circle at top right, #1e3a8a, #0f172a, #020617) !important; }
        
        .main-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 40px; border-radius: 25px; text-align: center; margin-top: 30px;
        }
        
        .timer-container {
            font-family: 'JetBrains Mono', monospace; color: #3b82f6; font-size: 3em; font-weight: 700;
            padding: 20px; background: rgba(59, 130, 246, 0.1); border-radius: 15px;
            border: 1px solid rgba(59, 130, 246, 0.3); margin: 25px auto; display: inline-block;
        }

        /* HIDE THE TRIGGER BUTTON FROM HUMAN EYES */
        div[data-testid="stButton"] button:has(div:contains("Unlock System")) {
            display: none !important;
        }
        
        /* THE GHOST SENSOR */
        .ghost-sensor {
            position: fixed;
            top: 0;
            left: 0;
            width: 100px;
            height: 100px;
            background: transparent;
            z-index: 99999;
            cursor: default;
        }
        </style>
        
        <div class="ghost-sensor" id="sensor"></div>

        <script>
            const sensor = window.parent.document.getElementById('sensor');
            sensor.addEventListener('dblclick', function() {
                // Find and click the hidden button
                const buttons = window.parent.document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.innerText.includes("Unlock System")) {
                        btn.click();
                        break;
                    }
                }
            });
        </script>
    """, unsafe_allow_html=True)

    # 2. --- THE HEADER & MESSAGE ---
    st.markdown(f"""
        <div class="main-card">
            <div style="color: #ef4444; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; font-size: 0.9em; margin-bottom: 10px;">
                ⚠️ OFFICIAL SYSTEM MAINTENANCE
            </div>
            <h1 style="color: white; font-size: 2.8em; margin: 0;">PORTAL <span style="color: #3b82f6;">OFFLINE</span></h1>
            <p style="color: #94a3b8; margin-top: 10px; font-size: 1.1em;">
                Ruby Springfield College Portal is undergoing essential internal maintenance. 
                Access will be automatically restored once the countdown completes.
            </p>
            <div class="timer-container">{timer_display}</div>
        </div>
    """, unsafe_allow_html=True)

    # 3. --- THE STEALTH BYPASS (NOW HIDDEN VIA CSS) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    # This button is now 100% invisible because of the CSS rule above
    if st.button("Unlock System", key="hidden_trigger"):
        st.session_state.ghost_unlocked = not st.session_state.ghost_unlocked

    # The password field ONLY appears after you double-click the top-left corner
    if st.session_state.ghost_unlocked:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            secret = st.text_input("System Decryption Key", type="password")
            if st.button("Authorize Access"):
                if secret == ADMIN_SECRET_KEY:
                    st.session_state.maintenance_bypass = True
                    st.rerun()
                else:
                    st.error("Access Denied")

    st.stop()
# =================================================================

# --- NEW: HELPER FUNCTION TO FIX NAMEERROR ---
def get_local_img(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None
    except Exception:
        return None

# --- STEP 1: PAGE CONFIG ---
st.set_page_config(
    page_title="Ruby Springfield College | Official Portal",
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STEP 2: LOGO WATERMARK (MODERATE & PROFESSIONAL) ---
def add_logo_watermark(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background: 
                    linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
                    url("data:image/jpeg;base64,{encoded_string}") !important;
                background-attachment: fixed !important;
                background-size: 350px !important; 
                background-position: center !important;
                background-repeat: no-repeat !important;
            }}
            
            @media (max-width: 768px) {{
                [data-testid="stAppViewContainer"] {{
                    background-size: 250px !important; 
                }}
            }}

            .stApp {{
                background-color: transparent !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"❌ DATABASE ERROR: File '{image_file}' not found.")

# --- CALL THE LOGO ---
add_logo_watermark("logo.jpg")

# --- NEW: DESIGN & FONT FEATURES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #F3F4F6 !important;
    }

    .stApp {
        background: #F3F4F6;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #D1D5DB !important;
        padding: 10px !important;
    }

    div.stButton > button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 10px 25px !important;
        font-weight: 600 !important;
        width: 100% !important;
        border: none !important;
        transition: 0.3s ease;
    }

    div.stButton > button:hover {
        background-color: #2563EB !important;
        transform: translateY(-2px);
    }

    .portal-header {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 30px;
        border-top: 5px solid #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# --- STEP 3: LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- SECRETS ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_PATH"]
except Exception as e:
    st.warning("Running in Local Mode: Secrets not detected.")

# --- GOOGLE VERIFICATION ---
verify_code = "lJuiVMz6tsO5tGGxk2wTWmFydMeB7gxsQyuUJger6cg"
st.markdown(f'<div style="display:none;">google-site-verification: {verify_code}</div>', unsafe_allow_html=True)

# --- VISIBLE SCHOOL BRANDING ---
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <h1 style="color: #1E3A8A; margin-bottom: 5px; font-weight: 700; font-size: 3em;">RUBY SPRINGFIELD COLLEGE</h1>
        <h3 style="color: #4B5563; margin-top: 0; font-weight: 400;">Official Academic Management & Result Portal</h3>
        <p style="font-weight: 600; color: #1E3A8A; letter-spacing: 1px;">MAIDUGURI, BORNO STATE, NIGERIA</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Motto and Bio (Correctly placed outside the previous string)
st.markdown("""<h3 style='text-align:center; color:#2563eb; font-style:italic; margin-top:-15px;'>Motto: A Citadel of Supreme Excellence</h3>""", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color: #374151; font-weight: 500; margin-bottom: 20px;">"We are building global leaders with integrity and academic brilliance."</div>', unsafe_allow_html=True)

def upload_notice_to_github(file_bytes, file_name):
    url = f"https://api.github.com/repos/{REPO}/contents/notices/{file_name}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    encoded_content = base64.b64encode(file_bytes).decode("utf-8")
    data = {
        "message": f"New Notice: {file_name}",
        "content": encoded_content,
        "branch": "main"
    }
    response = requests.put(url, headers=headers, json=data)
    return response.status_code
    
# --- STEP 4: PERMANENT STORAGE ENGINE & GLOBAL DATA LOADING ---
def load_portal_data():
    storage_path = "portal_data.xlsx"
    defaults = {
        'news_title': "Ruby Springfield College Portal", 
        'news_desc': "Welcome to the official academic management system.",
        'calendar': "Welcome to the 2026 Academic Session",
        'exams': "Valid ID and Uniform required.",
        'contact': "Principal: +234 813 103 2577",
        'notices_data': "[]"
    }
    
    if os.path.exists(storage_path):
        try:
            df_storage = pd.read_excel(storage_path, engine='openpyxl')
            return dict(zip(df_storage['Key'].astype(str), df_storage['Value'].astype(str)))
        except Exception:
            return defaults
    return defaults 

# --- UPDATED: SMART GLOBAL DATABASE LOADING ---
def load_main_database():
    """ Automatically finds and loads the Report file, fixing column naming issues """
    report_files = glob.glob("Report *.xlsx")
    if report_files:
        try:
            temp_df = pd.read_excel(report_files[0])
            
            # --- SMART COLUMN CLEANER ---
            # 1. Strip extra spaces from headers
            temp_df.columns = [str(c).strip() for c in temp_df.columns]
            
            # 2. Check for 'Class' (case-insensitive) and force it to be 'Class'
            col_map = {col.lower(): col for col in temp_df.columns}
            if 'class' in col_map:
                temp_df = temp_df.rename(columns={col_map['class']: 'Class'})
                return temp_df
            else:
                st.error(f"❌ DATA ERROR: The column 'Class' was not found in {report_files[0]}. Please check your Excel headers!")
                return temp_df
        except Exception as e:
            st.error(f"❌ LOAD ERROR: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Initialize Global Data
df = load_main_database()

if 'portal_storage' not in st.session_state:
    st.session_state.portal_storage = load_portal_data()
    
# --- STEP 5: THE UPDATED EMAIL FUNCTION (PROFESSIONAL VERSION) ---
def send_email_notification(receiver_email, student_name, class_name, reg_number, access_key):
    sender_email = "sumilogics247@gmail.com"
    sender_password = "upsw jbon rhoy aiai" 
    portal_link = "https://rubyspringfield-college.streamlit.app/" 

    message = MIMEMultipart()
    message["From"] = f"Ruby Springfield College Admin <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"OFFICIAL: Academic Result Notification - {student_name}"

    # Professional HTML Body
    body = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2e7d32;">Ruby Springfield College, Maiduguri</h2>
            <p>Dear Parent/Guardian,</p>
            <p>This is an official notification regarding the release of the academic performance report for <strong>{student_name}</strong> in <strong>{class_name}</strong>.</p>
            
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; border-left: 5px solid #2e7d32;">
                <h3 style="margin-top: 0;">Portal Access Credentials</h3>
                <p style="margin-bottom: 5px;"><strong>Portal Link:</strong> <a href="{portal_link}">{portal_link}</a></p>
                <p style="margin-bottom: 5px;"><strong>Admission Number:</strong> {reg_number}</p>
                <p style="margin-top: 0;"><strong>Access Key/Password:</strong> {access_key}</p>
            </div>

            <p>Please log in to the portal to view the full terminal report and performance analysis.</p>
            <br>
            <p>Best Regards,</p>
            <hr style="border: 0; border-top: 1px solid #ccc; width: 200px; margin-left: 0;">
            <p><strong>School Management</strong><br>
            Ruby Springfield College</p>
        </div>
    </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Mail Error: {e}")
        return False      

# --- STEP 6: CONFIGURATION & DIRECTORIES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.jpg") 
SIG_PATH = os.path.join(BASE_DIR, "signature.png") 
STAMP_PATH = os.path.join(BASE_DIR, "Stamp.jpg") 

# STAFF ACCESS CONFIGURATION
STAFF_MASTER_KEY = "MGTRSC2026" 

def log_activity(user_type, action, details):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {user_type.upper()} | {action} | {details}\n"
        with open("system_audit.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass 

def get_available_classes():
    files = glob.glob("Report *.xlsx")
    return [f.replace("Report ", "").replace(".xlsx", "") for f in files]

def show_analytics(selected_class):
    file_path = f"Report {selected_class}.xlsx"
    if os.path.exists(file_path):
        data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        
        sc_n = next((s for s in data_sheets.keys() if 'scoresheet' in s.lower()), None)
        if sc_n:
            df_sc = data_sheets[sc_n]
            header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
            header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
            
            r1 = df_sc.iloc[header_idx-1] 
            r2 = df_sc.iloc[header_idx]   
            
            subjects = []
            averages = []
            
            for i in range(len(r2)):
                if str(r2.iloc[i]).strip().lower() == "total":
                    sub_name = str(r1.iloc[i]).strip()
                    if sub_name.lower() == 'nan' or sub_name == '':
                        for look_back in range(i-1, max(-1, i-10), -1):
                            val = str(r1.iloc[look_back]).strip()
                            if val.lower() != 'nan' and val != '':
                                sub_name = val
                                break
                    
                    if sub_name.lower() == 'nan': sub_name = f"Sub_{i}"
                    
                    score_col = pd.to_numeric(df_sc.iloc[header_idx+1:, i], errors='coerce').dropna()
                    if not score_col.empty:
                        subjects.append(sub_name)
                        averages.append(round(score_col.mean(), 1))
            st.markdown(f"### 📊 Performance Overview: {selected_class}")
            
            # --- STEP 3: MANAGEMENT SUMMARY LOGIC ---
            data_rows = df_sc.iloc[header_idx+1:, :]
            at_risk_list = []
            
            for _, row in data_rows.iterrows():
                student_name = row.iloc[1]
                fail_count = sum(1 for c in total_cols if pd.to_numeric(row.iloc[c], errors='coerce') < 50)
                if fail_count >= 3:
                    at_risk_list.append({"Student": student_name, "Failing Subjects": fail_count})

            class_avg = sum(averages) / len(averages) if averages else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Class Average", f"{round(class_avg, 1)}%")
            m2.metric("Total Students", len(data_rows))
            m3.metric("At-Risk Students", len(at_risk_list), delta_color="inverse")

            # --- VISUALS ---
            col1, col2 = st.columns([2, 1])
            with col1:
                fig_bar = px.bar(
                    x=subjects, y=averages, 
                    labels={'x': 'Subjects', 'y': 'Avg Score'},
                    title="Average Subject Performance",
                    color=averages, color_continuous_scale='Viridis',
                    text_auto=True
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("🏆 **Top 3 Students**")
                grand_total_idx = total_cols[-1] if total_cols else 1
                df_leader = df_sc.iloc[header_idx+1:, [0, 1, grand_total_idx]].copy()
                df_leader.columns = ['ID', 'Name', 'Total']
                df_leader['Total'] = pd.to_numeric(df_leader['Total'], errors='coerce')
                top_3 = df_leader.nlargest(3, 'Total')
                for i, row in top_3.iterrows():
                    st.success(f"{row['Name']} - {row['Total']}")

            if at_risk_list:
                with st.expander("⚠️ View At-Risk Students (Failing 3+ Subjects)"):
                    st.table(pd.DataFrame(at_risk_list))

            log_activity("Admin", "Analytics", f"Generated dashboard for {selected_class}")

        else:
            st.warning("Could not find 'Scoresheet' tab for analysis.")
    else:
        st.error(f"Excel file for {selected_class} not found.")

def get_master_remarks(avg):
    if avg >= 75: return "A1", "EXCELLENT", "An Outstanding performance, keep up the standard."
    elif avg >= 70: return "B2", "V-GOOD", "An impressive result, there is room for more improvement."
    elif avg >= 65: return "B3", "GOOD", "A very good result, but you can do better."
    elif avg >= 60: return "C4", "CREDIT", "Demonstrated partial knowledge by struggling with complex tasks."
    elif avg >= 55: return "C5", "CREDIT", "Fell short of expectations due to incomplete understanding or inconsistent effort."
    elif avg >= 50: return "C6", "CREDIT", "Urgent attention needed to address critical skill deficits."
    elif avg >= 45: return "D7", "PASS", "This performance indicates significant gaps in understanding."
    elif avg >= 40: return "E8", "PASS", "Performance is below average, you need to work harder."
    else: return "F9", "FAIL", "There is an urgent need for academic intervention and serious study."

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- INITIALIZE DYNAMIC CONTENT (UPDATED FOR PERSISTENCE) ---
# Shutdown, this now pulls from st.session_state.portal_storage 
# which we linked to the portal_data.xlsx file earlier.

if 'news_content' not in st.session_state:
    # We check if portal_storage exists (from our load_portal_data function)
    # If it does, we use that. If not, we use the fallback "Grand Cultural Festival"
    storage = st.session_state.get('portal_storage', {})
    
    st.session_state.news_content = {
        "title": storage.get("news_title", "🌍 THE GRAND CULTURAL FESTIVAL"),
        "desc": storage.get("news_desc", "Darlings, let your heritage shine! Wear your patterns with pride."),
        "img": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?q=80&w=800&auto=format&fit=crop"
    }

if 'protocols' not in st.session_state:
    storage = st.session_state.get('portal_storage', {})
    
    st.session_state.protocols = {
        "calendar": storage.get("calendar", "• **Feb 14-17:** Mid-term Break\n• **March 25:** Exam Commencement"),
        "exams": storage.get("exams", "1. Hall closes 15m before start.\n2. Zero tolerance for devices."),
        "contact": storage.get("contact", "• **Phone:** 08131032577\n• **Location:** Old GRA, Maiduguri")
    }

# This ensures that even if you refresh, the session_state 
# is immediately repopulated from your Excel "Brain".

def get_available_classes():
    files = glob.glob("Report *.xlsx")
    classes = []
    for f in files:
        filename = os.path.basename(f)
        class_name = filename.replace("Report ", "").replace(".xlsx", "").strip()
        if class_name:
            classes.append(class_name)
    return sorted(list(set(classes))) if classes else ["JSS 1A"]


# Initialize session state for all toggles
for key in ['show_students', 'show_subjects', 'show_cal', 'show_exam', 'show_contact']:
    if key not in st.session_state:
        st.session_state[key] = False

# --- PROFESSIONAL ROYAL BLUE & CLEAN LIGHT THEME (MOBILE OPTIMIZED) ---
st.markdown("""
    <style>
    /* Force the main app background to white regardless of system theme */
    .stApp { 
        background-color: #ffffff !important; 
        color: #1e293b !important; 
    }
    
    /* SIDEBAR: Explicitly force light background and dark text */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 3px solid #2563eb !important;
    }

    /* Target ALL text in sidebar to ensure readability on mobile dark mode */
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }

    /* Specifically target the navigation links/labels */
    [data-testid="stSidebarNav"] span {
        color: #1e293b !important;
        font-weight: 600 !important;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }

    /* Logo Border: White with Blue Glow */
    .school-logo-border {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 4px double #2563eb;
        padding: 5px;
        background: white;
        object-fit: cover;
        box-shadow: 0px 4px 15px rgba(37, 99, 235, 0.2);
    }
    
    /* Quote Box: Soft Blue Background for contrast */
    .principal-quote {
        background: #eff6ff !important;
        border-left: 5px solid #2563eb !important;
        padding: 20px;
        margin: 10px 0 25px 0;
        border-radius: 0 15px 15px 0;
        font-family: 'Georgia', serif;
        color: #1e3a8a !important;
    }

    /* Ticker: Blue with White Text */
    .ticker-wrap {
        width: 100%; overflow: hidden; height: 40px; 
        background-color: #2563eb !important; 
        border-bottom: 2px solid #1e40af;
        border-top: 2px solid #1e40af;
        display: flex; align-items: center; margin-bottom: 20px;
    }
    .ticker {
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 60s linear infinite; font-weight: bold; color: #ffffff !important;
    }
    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    .ticker-item { display: inline-block; padding: 0 50px; }

    /* Content Boxes: White with Blue Outlines */
    .statement-box {
        background: #ffffff !important;
        border: 2px solid #2563eb !important;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        color: #1e293b !important;
    }

    /* Value Cards: Hover Effect preserved but colors lightened */
    .core-value-card {
        background: #f1f5f9 !important;
        border: 1px solid #2563eb !important;
        padding: 10px; border-radius: 10px; text-align: center;
        font-weight: bold; color: #1e3a8a !important; transition: 0.3s;
    }
    .core-value-card:hover { 
        background: #2563eb !important; 
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.4);
    }
    
    .school-bio {
        text-align: center; max-width: 900px; margin: 0 auto 40px auto;
        font-style: italic; color: #475569 !important; font-size: 1.2em; line-height: 1.6;
    }

    .history-card {
        background: #f8fafc !important;
        border-radius: 20px; padding: 35px; border: 1px solid rgba(37, 99, 235, 0.2);
        margin-bottom: 25px; line-height: 1.8; color: #1e293b !important;
    }

    .protocol-box {
        background: #eff6ff !important; border-left: 5px solid #2563eb !important;
        padding: 20px; border-radius: 12px; margin-top: 10px; margin-bottom: 10px;
        color: #1e3a8a !important;
        border: 1px solid #e2e8f0;
    }

    /* Footer: Kept Formal Professional Dark Blue */
    .footer-section {
        margin-top: 60px; padding: 40px; background: #020617 !important;
        border-radius: 40px 40px 0 0; text-align: center; border-top: 3px solid #2563eb;
    }
    
    .footer-section p {
        color: #cbd5e1 !important; font-size: 0.9em; margin-bottom: 15px; line-height: 1.5;
    }

    .watermark-text {
        color: rgba(37, 99, 235, 0.6) !important; font-size: 0.8em; letter-spacing: 2px; margin-top: 10px; font-weight: bold;
    }

    /* Buttons: Strong Blue */
    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #ffffff !important;
    }

    /* METRIC CARDS CSS */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 3px solid #2563eb !important;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        flex: 1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-label {
        color: #2563eb !important; /* Changed from gold to blue for readability on white */
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .metric-value {
        color: #1e293b !important;
        font-size: 1.2rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

class ResultPDF(FPDF):
    def draw_watermark(self):
        """Adds professional diagonal watermark using manual rotation"""
        try:
            self.set_font('Arial', 'B', 45)
            self.set_text_color(240, 240, 240)  # Very light grey
            self.rotate(45, 105, 148)
            self.text(35, 190, 'RUBY SPRINGFIELD COLLEGE')
            self.rotate(0) # Reset to 0
        except:
            pass 

    def header(self):
        # --- PROFESSIONAL BACKGROUND COLOR ---
        self.set_fill_color(252, 252, 254) 
        self.rect(0, 0, 210, 297, 'F')
        
        self.draw_watermark()
        
        # Logo handling
        if 'LOGO_PATH' in globals() and os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 22) 
        
        # School Name (Size 18)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(40, 70, 120) 
        self.cell(0, 8, 'RUBY SPRINGFIELD COLLEGE', 0, 1, 'C') 
        
        # Motto (Size 12)
        self.set_font('Arial', 'I', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, 'Motto: A Citadel of Supreme Excellence', 0, 1, 'C') 
        
        # Right Side Branding & Address (Size 12)
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, 'Opposite Polo Field, Old GRA, Maiduguri, Borno State', 0, 1, 'R') 
        self.cell(0, 5, 'Contact: 08131032577', 0, 1, 'R') 
        
        # Current Date (Size 10)
        curr_date = datetime.now().strftime("%d %B, %Y")
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, f'Generated on: {curr_date}', 0, 1, 'R')
        
        # Developer Credit (Small)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 4, 'Developed by: Adam Usman | Powered by SumiLogics(NJA)', 0, 1, 'R')
        
        self.ln(2)
        # --- STYLED HEADER BOX (Size 12) ---
        self.set_fill_color(40, 70, 120) 
        self.set_font('Arial', 'B', 12)
        self.set_text_color(255, 255, 255) 
        
        title = "OFFICIAL CONTINUOUS ASSESSMENT RECORD" if hasattr(self, 'is_test') and self.is_test else "OFFICIAL TERMLY PERFORMANCE RECORD"
        self.cell(0, 9, title, 0, 1, 'C', 1) 
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)
        footer_note = "Copyright @2026 Ruby Springfield College - Dev: Adam Usman (SumiLogics NJA)"
        self.cell(0, 10, footer_note, 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def student_info_box(self, student_name, adm, s_class, term, summary):
        self.set_text_color(40, 70, 120)
        self.set_font('Arial', 'B', 12)
        start_y = self.get_y()
        
        # Left side info (All Size 12)
        self.cell(40, 6, 'Name of student:', 0, 0) 
        self.set_text_color(0, 0, 0)
        self.cell(75, 6, f" {str(student_name).upper()}", 'B', 1)
        
        self.set_text_color(40, 70, 120)
        self.cell(40, 6, 'Admission No:', 0, 0) 
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(75, 6, f" {adm}", 'B', 1)
        
        self.set_text_color(40, 70, 120)
        self.set_font('Arial', 'B', 12)
        self.cell(40, 6, 'Class:', 0, 0) 
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 0, 0)
        self.cell(75, 6, f" {s_class}   |   Term: {term}", 'B', 1)

        # Right side summary box (Size 12)
        if summary.get('avg') not in ["N/A", 0, "0", None]:
            self.set_xy(130, start_y)
            self.set_fill_color(240, 242, 248) 
            self.set_font('Arial', 'B', 12)
            self.set_text_color(40, 70, 120)
            self.cell(40, 6, 'Obtained Score:', 1, 0, 'L', 1)
            self.set_text_color(0, 0, 0)
            self.cell(30, 6, f"{summary.get('obtained', 0)}", 1, 1, 'C')
            self.set_x(130)
            self.set_text_color(40, 70, 120)
            self.cell(40, 6, 'Average / Pos:', 1, 0, 'L', 1)
            self.set_text_color(0, 0, 0)
            self.cell(30, 6, f"{summary.get('avg', 0)}% / {summary.get('pos', '-')}", 1, 1, 'C')
            self.set_x(130)
            self.set_text_color(40, 70, 120)
            self.cell(40, 6, 'Total Possible:', 1, 0, 'L', 1)
            self.set_text_color(0, 0, 0)
            self.cell(30, 6, f"{summary.get('max', 0)}", 1, 1, 'C')
        self.ln(6)

    def draw_scores_table(self, subject_data, s_class):
        # Increased f_size to 12 as requested
        f_size = 12
        row_h = 7 
        
        self.set_fill_color(40, 70, 120) 
        self.set_text_color(255, 255, 255) 
        self.set_font('Arial', 'B', f_size)
        
        is_ss = "SS" in str(s_class).upper() and "JSS" not in str(s_class).upper()
        
        # --- FIXED WIDTHS TO PREVENT OVERLAP ---
        if is_ss:
            w = [60, 22, 22, 22, 64] # Total 190mm
        else:
            w = [65, 22, 22, 21, 60] # Total 190mm
            
        headers = ['Subject', 'C.A (40)', 'Exam (60)', 'Total (100)', 'Grade & Remark' if is_ss else 'Grade']
        
        for i in range(len(headers)):
            self.cell(w[i], row_h + 1, headers[i], 1, 0, 'C', 1)
        self.ln()
        
        self.set_text_color(0, 0, 0) 
        self.set_font('Arial', '', f_size)
        
        fill = False
        for sub, scores in subject_data.items():
            total = scores.get('Total', 0)
            if total > 0:
                self.set_fill_color(242, 244, 248) if fill else self.set_fill_color(255, 255, 255)
                
                # Subject Name
                self.cell(w[0], row_h, f" {sub}", 1, 0, 'L', 1)
                # CA & Exam
                self.cell(w[1], row_h, str(scores.get('CA', '')), 1, 0, 'C', 1)
                self.cell(w[2], row_h, str(scores.get('Exam', '')), 1, 0, 'C', 1)
                
                # Bold Total
                self.set_font('Arial', 'B', f_size)
                self.cell(w[3], row_h, str(total), 1, 0, 'C', 1)
                self.set_font('Arial', '', f_size)
                
                # --- GRADING LOGIC ---
                g = ""
                t = total
                if is_ss:
                    if t >= 75: g = "EXCELLENT"
                    elif t >= 70: g = "V-GOOD"
                    elif t >= 65: g = "GOOD"
                    elif t >= 60: g = "CREDIT"
                    elif t >= 55: g = "CREDIT"
                    elif t >= 50: g = "CREDIT"
                    elif t >= 45: g = "PASS"
                    elif t >= 40: g = "PASS"
                    else: g = "FAIL"
                else:
                    if t >= 75: g = "DISTINCTION"
                    elif t >= 65: g = "UPPER CREDIT"
                    elif t >= 55: g = "LOWER CREDIT"
                    elif t >= 45: g = "PASS"
                    elif t >= 40: g = "PASS"
                    else: g = "FAIL"
                
                # Render Grade without overlap
                self.cell(w[4], row_h, g, 1, 1, 'C', 1)
                fill = not fill
        self.ln(2)

    def draw_transcript_summary(self, summary, term):
        if "3rd" in str(term):
            self.set_fill_color(40, 70, 120)
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 6, 'ANNUAL CUMULATIVE TRANSCRIPT', 1, 1, 'C', 1)
            
            self.set_fill_color(230, 235, 245)
            self.set_text_color(0, 0, 0)
            t1, t2, t3 = summary.get('t1_avg', 0), summary.get('t2_avg', 0), summary.get('avg', 0)
            cum = round((t1 + t2 + t3) / 3, 2) if t1 > 0 else t3
            
            self.cell(47, 5, '1st Term Avg', 1, 0, 'C', 1)
            self.cell(47, 5, '2nd Term Avg', 1, 0, 'C', 1)
            self.cell(47, 5, '3rd Term Avg', 1, 0, 'C', 1)
            self.cell(49, 5, 'CUMULATIVE AVG (%)', 1, 1, 'C', 1)
            
            self.set_font('Arial', '', 12)
            self.cell(47, 6, f"{t1}%", 1, 0, 'C')
            self.cell(47, 6, f"{t2}%", 1, 0, 'C')
            self.cell(47, 6, f"{t3}%", 1, 0, 'C')
            self.set_font('Arial', 'B', 12)
            self.cell(49, 6, f"{cum}%", 1, 1, 'C')
            self.ln(1)

    def draw_footer_sections(self, beh, sk, comm, summary, s_class, term):
        is_ss = "SS" in str(s_class).upper() and "JSS" not in str(s_class).upper()
        curr_y = self.get_y()
        
        # All sections headers and text updated to Size 11
        self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 11)
        self.cell(55, 6, 'AFFECTIVE DOMAIN (A)', 1, 1, 'C', 1)
        
        self.set_text_color(0, 0, 0); self.set_font('Arial', '', 12)
        fill = False
        for k, v in list(beh.items())[1:9]: 
            self.set_fill_color(245, 245, 245) if fill else self.set_fill_color(255, 255, 255)
            self.cell(40, 5, k, 1, 0, 'L', 1); self.cell(15, 5, str(v), 1, 1, 'C', 1)
            fill = not fill
            
        self.ln(1)
        self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 10)
        self.cell(55, 5, 'POSITION OF RESPONSIBILITY', 1, 1, 'L', 1)
        self.set_text_color(0,0,0); self.set_font('Arial', '', 10); self.cell(55, 6, f" {comm.get('Position', 'None')}", 1, 1, 'L')
        
        # Psychomotor Skills (Size 10)
        self.set_xy(75, curr_y)
        self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 10)
        self.cell(55, 6, 'PSYCHOMOTOR SKILLS (B)', 1, 1, 'C', 1)
        self.set_text_color(0,0,0); self.set_font('Arial', '', 10)
        fill = False
        for k, v in list(sk.items())[1:6]:
            self.set_fill_color(245, 245, 245) if fill else self.set_fill_color(255, 255, 255)
            self.set_x(75); self.cell(40, 5, k, 1, 0, 'L', 1); self.cell(15, 5, str(v), 1, 1, 'C', 1)
            fill = not fill
            
        # Comments Section (Size 11)
        self.set_xy(140, curr_y)
        self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 11)
        self.cell(60, 6, "HOUSE MASTER'S REPORT", 1, 1, 'L', 1)
        self.set_text_color(0,0,0); self.set_x(140); self.set_font('Arial', '', 11); self.cell(60, 6, f" {comm.get('House_Master_Report', 'Satisfactory')}", 1, 1, 'L')
        
        self.ln(1); self.set_x(140); self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 11)
        self.cell(60, 6, "FORM MASTER'S COMMENT", 1, 1, 'L', 1)
        self.set_text_color(0,0,0); self.set_x(140); self.set_font('Arial', '', 11); self.cell(60, 6, f" {comm.get('Form_Master_Comment', 'Good performance.')}", 1, 1, 'L')
        
        self.ln(1); self.set_x(140); self.set_fill_color(40, 70, 120); self.set_text_color(255,255,255); self.set_font('Arial', 'B', 11)
        self.cell(60, 6, "PRINCIPAL'S COMMENT", 1, 1, 'L', 1)
        self.set_text_color(0,0,0); self.set_x(140)
        avg = summary['avg']
        if is_ss:
            p_remark = "Outstanding performance." if avg >= 75 else "Average performance." if avg >= 50 else "Poor result."
        else:
            p_remark = "An Impressive performance!" if avg >= 75 else "A fair performance." if avg >= 50 else "Sit up."
        self.set_font('Arial', 'I', 12); self.multi_cell(60, 6, f" {p_remark}", 1, 'L')
        
        if "3rd" in str(term):
            self.ln(1.5); self.set_x(10); self.set_font('Arial', 'B', 12)
            status = "PROMOTED TO NEXT CLASS" if avg >= 40 else "HELD BACK"
            self.set_fill_color(230, 245, 230) if avg >= 40 else self.set_fill_color(255, 230, 230)
            self.cell(125, 7, f"PROMOTION STATUS: {status}", 1, 1, 'C', 1)
            
        self.ln(2.5); sig_y = self.get_y()
        if os.path.exists(STAMP_PATH): self.image(STAMP_PATH, 145, sig_y - 4, 45) 
        if os.path.exists(SIG_PATH): self.image(SIG_PATH, 155, sig_y - 2, 22)
        self.set_x(140); self.cell(60, 0, '', 'T', 1, 'C')
        self.set_x(140); self.set_font('Arial', 'B', 12); self.set_text_color(40,70,120); self.cell(60, 5, "Principal's Signature & Stamp", 0, 1, 'C')

    # --- MISSING PART ADDED BELOW ---
    def draw_test_table(self, test_results):
        """Specifically for the C.A / Test Results portal"""
        f_size = 11
        row_h = 8
        self.set_fill_color(40, 70, 120)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', f_size)
        
        # Column widths (Total 190mm)
        w = [60, 26, 26, 26, 26, 26]
        headers = ['Subject', 'CA 1', 'CA 2', 'CA 3', 'CA 4', 'Total CA']
        
        for i in range(len(headers)):
            self.cell(w[i], row_h + 1, headers[i], 1, 0, 'C', 1)
        self.ln()
        
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', f_size)
        fill = False
        
        for sub, scores in test_results.items():
            self.set_fill_color(242, 244, 248) if fill else self.set_fill_color(255, 255, 255)
            self.cell(w[0], row_h, f" {sub}", 1, 0, 'L', 1)
            self.cell(w[1], row_h, str(scores.get('CA1', 0)), 1, 0, 'C', 1)
            self.cell(w[2], row_h, str(scores.get('CA2', 0)), 1, 0, 'C', 1)
            self.cell(w[3], row_h, str(scores.get('CA3', 0)), 1, 0, 'C', 1)
            self.cell(w[4], row_h, str(scores.get('CA4', 0)), 1, 0, 'C', 1)
            self.set_font('Arial', 'B', f_size)
            self.cell(w[5], row_h, str(scores.get('Total_CA', 0)), 1, 1, 'C', 1)
            self.set_font('Arial', '', f_size)
            fill = not fill#--- SIDEBAR ---#
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        logo_base64 = get_base64_of_bin_file(LOGO_PATH)
        st.markdown(f'<div class="logo-container"><img src="data:image/jpeg;base64,{logo_base64}" class="school-logo-border"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#fbbf24;'>🔐 ACCESS PORTAL</h3>", unsafe_allow_html=True)
    user_role = st.selectbox("Select Access Type", ["Student Portal", "Staff Portal (Shutdown)"])
    page = st.radio("Navigation", ["📊 Dashboard", "🎓 Result Portal"] if user_role == "Student Portal" else ["🛠️ Staff Management"])

# --- STUDENT LOGIN & PORTAL ---
if page == "🎓 Result Portal":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎓 Student Login")

    portal_type = st.sidebar.radio(
        "Select Portal Type",
        ["📊 Full Term Results", "📝 Test Results (C.A)"],
        index=0
    )

    adm_no = st.sidebar.text_input("Admission Number").strip()
    
    # --- SECRET CODE: SUMI ---
    if adm_no == "SUMI":
        st.balloons()
        st.title("MUM's Portal")
        st.success("Access Granted for Shutdown & Babe") 
        st.write("**Dedication:** I dedicate the project to my beloved Chikito👸 once.")
        st.info("Who Am I!?, Adam.")
        st.stop()

    pwd = st.sidebar.text_input("Access Key", type="password").strip()
    selected_class = st.sidebar.selectbox("Class", get_available_classes())
    
    btn_label = "Generate Full Report" if portal_type == "📊 Full Term Results" else "View Test Scores"
    login_btn = st.sidebar.button(btn_label)

    # --- POPUP DIALOG FOR DOWNLOAD ---
    @st.dialog("📥 Report Ready")
    def show_download_popup(pdf_bytes, filename):
        st.success("Your PDF has been generated successfully!")
        st.download_button("Click here to Download PDF", data=pdf_bytes, file_name=filename, use_container_width=True)
        if st.button("Close"):
            st.rerun()

    if login_btn:
        file_path = f"Report {selected_class}.xlsx"
        if os.path.exists(file_path):
            try:
                xl = pd.ExcelFile(file_path)
                if 'Data' in xl.sheet_names:
                    df_data = xl.parse('Data', header=None)
                    df_data.columns = [str(c).strip() for c in df_data.iloc[0]]
                    df_data = df_data[1:]
                    
                    adm_clean, pwd_clean = str(adm_no), str(pwd)
                    cols = df_data.columns.tolist()
                    adm_col = next((c for c in cols if "admission" in c.lower()), "Admission_No")
                    pwd_col = next((c for c in cols if "pass" in c.lower() or "key" in c.lower()), "Password")
                    name_col = next((c for c in cols if "name" in c.lower()), "Name")

                    user = df_data[(df_data[adm_col].astype(str).str.strip() == adm_clean) & 
                                   (df_data[pwd_col].astype(str).str.strip() == pwd_clean)]

                    if not user.empty:
                        student = user.iloc[0]
                        student_name = str(student.get(name_col, 'Student')).upper()
                        term = student.get('Term', 'N/A')
                        
                        log_activity("Student", "Login", f"Success: {student_name} ({adm_clean})")
                        sheets_to_load = [s for s in xl.sheet_names if any(k in s.lower() for k in ['bsheet', 'scoresheet', 'behaviour', 'skill', 'comment'])]
                        data_sheets = {s: xl.parse(s, header=None) for s in sheets_to_load}

                        def find_s(key):
                            for s in data_sheets.keys():
                                if key.lower() in s.lower(): return s
                            return None

                        def clean_score(val):
                            try:
                                if pd.isna(val) or str(val).strip() in ["-", "None", ""]: return 0.0
                                return float(val)
                            except: return 0.0

                        sc_n = find_s('Scoresheet')
                        
                        # --- BRANCH 1: TEST RESULTS (C.A) ---
                        if portal_type == "📝 Test Results (C.A)":
                            st.title(f"📝 Test Records: {student_name}")
                            test_results = {}
                            if sc_n:
                                df_sc = data_sheets[sc_n]
                                header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                                header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
                                r1, header_row = df_sc.iloc[header_idx-1], df_sc.iloc[header_idx]
                                s_row = df_sc[df_sc.iloc[:,0].astype(str).str.strip() == adm_clean]
                                
                                if not s_row.empty:
                                    s_vals = s_row.iloc[0]
                                    for i, col_val in enumerate(header_row):
                                        if str(col_val).strip().lower() == 'total':
                                            sub = "Unknown"
                                            for j in range(i, -1, -1):
                                                val = str(r1.iloc[j]).strip()
                                                if val.lower() != 'nan' and val != '': sub = val; break
                                            try:
                                                test_results[sub] = {
                                                    "CA1": clean_score(s_vals.iloc[i-6]),
                                                    "CA2": clean_score(s_vals.iloc[i-5]),
                                                    "CA3": clean_score(s_vals.iloc[i-4]),
                                                    "CA4": clean_score(s_vals.iloc[i-3]),
                                                    "Total_CA": clean_score(s_vals.iloc[i-2])
                                                }
                                            except: continue
                            
                            st.table(pd.DataFrame(test_results).T)
                            
                            try:
                                pdf = ResultPDF()
                                pdf.is_test = True 
                                pdf.set_margins(left=10, top=10, right=10)
                                pdf.add_page()
                                _ = pdf.student_info_box(student_name, adm_clean, selected_class, term, {'avg': 0})
                                _ = pdf.draw_test_table(test_results) # Works now!
                                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
                                show_download_popup(pdf_bytes, f"Test_{student_name}.pdf")
                            except Exception as e:
                                st.error(f"PDF Error: {e}")

                        # --- BRANCH 2: FULL TERM RESULTS ---
                        else:
                            # ... (Full Term Logic remains the same) ...
                            bs_n, beh_n, sk_n, com_n = find_s('Bsheet'), find_s('Behaviour'), find_s('Skill'), find_s('Comment')
                            pos_val = "N/A"
                            if bs_n:
                                df_bs = data_sheets[bs_n]
                                df_bs.columns = [str(c).strip() for c in df_bs.iloc[0]]
                                match = df_bs[df_bs.iloc[:,0].astype(str).str.strip() == adm_clean]
                                if not match.empty: pos_val = match.iloc[0].get('Position', 'N/A')

                            processed_results, total_sum = {}, 0
                            if sc_n:
                                is_3rd = "3rd" in sc_n.lower()
                                disp_term = "3RD TERM" if is_3rd else "2ND TERM"
                                df_sc = data_sheets[sc_n]
                                header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                                header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
                                r1, header_row = df_sc.iloc[header_idx-1], df_sc.iloc[header_idx]
                                s_row = df_sc[df_sc.iloc[:,0].astype(str).str.strip() == adm_clean]
                                if not s_row.empty:
                                    s_vals = s_row.iloc[0]
                                    for i, col_val in enumerate(header_row):
                                        if str(col_val).strip().lower() == 'total':
                                            sub = "Unknown"
                                            for j in range(i, -1, -1):
                                                val = str(r1.iloc[j]).strip()
                                                if val.lower() != 'nan' and val != '': sub = val; break
                                            try:
                                                ca, ex, tot = clean_score(s_vals.iloc[i-2]), clean_score(s_vals.iloc[i-1]), clean_score(s_vals.iloc[i])
                                                processed_results[sub] = {"CA": ca, "Exam": ex, "Total": tot}
                                                total_sum += tot
                                            except: continue

                            def get_row(sn):
                                if not sn: return {}
                                df = data_sheets[sn]
                                df.columns = [str(c).strip() for c in df.iloc[0]]
                                m = df[df.iloc[:,0].astype(str).str.strip() == adm_clean]
                                return m.iloc[0].to_dict() if not m.empty else {}

                            beh, sk, comm = get_row(beh_n), get_row(sk_n), get_row(com_n)
                            active_subs = [v for k, v in processed_results.items() if v['Total'] > 0]
                            summary = {'obtained': total_sum, 'avg': round(total_sum/max(1, len(active_subs)), 2), 'pos': pos_val, 'max': len(processed_results)*100}
                            
                            st.title(f"👋 Welcome, {student_name}")
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Average", f"{summary['avg']}%")
                            m2.metric("Position", summary['pos'])
                            m3.metric("Total", f"{int(summary['obtained'])}/{summary['max']}")
                            st.table(pd.DataFrame(processed_results).T)

                            try:
                                pdf = ResultPDF()
                                pdf.set_margins(left=10, top=10, right=10)
                                pdf.set_auto_page_break(auto=True, margin=10)
                                pdf.add_page()
                                _ = pdf.student_info_box(student_name, adm_clean, selected_class, disp_term, summary)
                                _ = pdf.draw_scores_table(processed_results, selected_class)
                                if is_3rd: _ = pdf.draw_transcript_summary(summary, disp_term)
                                _ = pdf.draw_footer_sections(beh, sk, comm, summary, selected_class, disp_term)
                                
                                pdf.ln(8)
                                pdf.set_font('Arial', 'B', 10)
                                pdf.cell(0, 10, "NEXT TERM BEGINS: 20th APRIL, 2026", ln=1, align='C')
                                
                                pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
                                show_download_popup(pdf_bytes, f"{student_name}.pdf")
                            except Exception as e:
                                st.error(f"PDF Error: {e}")
                    else:
                        st.sidebar.error("❌ Invalid Login Credentials")
                else:
                    st.error("❌ 'Data' sheet not found in the file.")
            except Exception as e:
                st.error(f"System Error: {e}")
        else:
            st.error(f"❌ Record for {selected_class} not found.")
# --- STAFF MANAGEMENT LOGIC ---
elif page == "🛠️ Staff Management":
    import io  
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    st.title("🛠️ Staff Administrative Console")
    
# 1. SIDEBAR AUTHENTICATION BARRIER
    st.sidebar.markdown("### 🔐 Admin Access")
    master_auth = st.sidebar.text_input("Enter Master Authentication Key", type="password")
    
    if not master_auth:
        st.info("👋 Welcome. Please enter the Master Key in the sidebar to access the console.")
        st.stop() 

    if master_auth != STAFF_MASTER_KEY:
        log_activity("Unauthorized", "Login Attempt", "Failed Master Key entry")
        st.error("❌ Invalid Authentication Key. Access Denied.")
        st.stop() 

    # Success Log
    if 'logged_in' not in st.session_state:
        log_activity("Admin", "Login", "Shutdown accessed the Staff Console")
        st.session_state['logged_in'] = True

    st.success("✅ Authentication Successful. Welcome, Management.")
     
    # Define Tabs
    tab_up, tab_db, tab_analytics, tab_bulk, tab_content = st.tabs([
        "📤 Upload/Update", "📂 Database & Logs", "📈 Class Insights", 
        "📦 Bulk & Notifications", "📢 Content Manager"
    ])

    # --- 1. UPLOAD TAB ---
    with tab_up:
        st.subheader("📤 Results Management")
        st.info("Upload class results here. Format: 'Report ClassName.xlsx'")
        target_class = st.text_input("Target Class Name (e.g., JSS 1A)", key="upload_target")
        new_file = st.file_uploader("Select Excel Spreadsheet", type=['xlsx'])
        
        if st.button("Deploy to System") and new_file and target_class:
            save_filename = f"Report {target_class}.xlsx"
            file_bytes = new_file.getvalue() 
            with open(save_filename, "wb") as f:
                f.write(file_bytes)
            
            with st.spinner(f"🚀 Syncing {save_filename} with GitHub..."):
                status = upload_notice_to_github(file_bytes, save_filename)
            
            if status in [200, 201]:
                st.balloons()
                st.success(f"✅ {save_filename} is now live!")
            else:
                st.warning(f"⚠️ Sync Error: {status}")

   # --- 2. DATABASE TAB ---
    with tab_db:
        col_db, col_log = st.columns(2)
        
        with col_db:
            st.subheader("📂 Live Databases")
            live_files = glob.glob("Report *.xlsx")
            
            if not live_files:
                st.info("No active databases found.")
            
            for file in live_files:
                # Use columns to put the file name and delete button side-by-side
                db_col1, db_col2 = st.columns([3, 1])
                with db_col1:
                    st.code(file)
                with db_col2:
                    # Unique key for each button based on filename
                    if st.button(f"🗑️ Delete", key=f"del_{file}", use_container_width=True):
                        try:
                            os.remove(file)
                            st.toast(f"🔥 {file} removed successfully!")
                            st.rerun() # Refresh to update the list
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col_log:
            st.subheader("🕵️ Security Audit")
            log_file = "system_audit.log"
            
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = f.readlines()
                
                st.text_area("Recent Activity", "".join(logs[-15:]), height=200)
                
                # Button to clear the log file
                if st.button("🧨 Clear Audit Log", use_container_width=True):
                    with open(log_file, "w") as f:
                        f.write(f"[{datetime.now()}] LOG CLEARED BY ADMIN\n")
                    st.success("Audit log wiped clean.")
                    st.rerun()
            else:
                st.info("No audit log found.")
                

    # # --- 3. ANALYTICS TAB ---
    with tab_analytics:
        st.subheader("📈 Professional Performance Analytics")
        
        # Select Database to Analyze
        analysis_target = st.selectbox("Select Database for Analysis", glob.glob("Report *.xlsx"), key="analysis_selector")
        
        if analysis_target and os.path.exists(analysis_target):
            xl = pd.ExcelFile(analysis_target)
            sc_sheet = next((s for s in xl.sheet_names if 'scoresheet' in s.lower()), None)
            
            if sc_sheet:
                # Load data (Header is usually row 1 or 2 based on your Excel structure)
                df_analysis = xl.parse(sc_sheet, header=None)
                
                # Find the 'Total' columns to identify subjects
                header_mask = df_analysis.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                header_idx = df_analysis[header_mask].index[0] if any(header_mask) else 1
                
                # Extract Student Names and Totals
                subject_labels = df_analysis.iloc[header_idx - 1]
                data_rows = df_analysis.iloc[header_idx + 1:]
                
                # 1. TOP METRICS ROW
                col1, col2, col3 = st.columns(3)
                total_students = len(data_rows.iloc[:, 0].dropna())
                
                # Calculate Grand Average
                all_totals = []
                for i, label in enumerate(df_analysis.iloc[header_idx]):
                    if str(label).strip().lower() == 'total':
                        all_totals.extend(pd.to_numeric(data_rows.iloc[:, i], errors='coerce').dropna().tolist())
                
                class_avg = round(sum(all_totals)/len(all_totals), 2) if all_totals else 0
                
                with col1:
                    st.metric("Total Enrollment", f"{total_students} Students", border=True)
                with col2:
                    st.metric("Class Mean Score", f"{class_avg}%", delta=f"{round(class_avg - 50, 1)}% vs Pass", border=True)
                with col3:
                    st.metric("Current Term", "2ND TERM", border=True)

                st.divider()

                # 2. VISUAL ANALYSIS SECTION
                chart_col, list_col = st.columns([2, 1])
                
                with chart_col:
                    st.markdown("#### 📊 Grade Distribution")
                    # Grading Logic for Chart
                    grades = {"A (75+)": 0, "B (65-74)": 0, "C (50-64)": 0, "P (40-49)": 0, "F (<40)": 0}
                    for score in all_totals:
                        if score >= 75: grades["A (75+)"] += 1
                        elif score >= 65: grades["B (65-74)"] += 1
                        elif score >= 50: grades["C (50-64)"] += 1
                        elif score >= 40: grades["P (40-49)"] += 1
                        else: grades["F (<40)"] += 1
                    
                    # Display as a Professional Bar Chart
                    st.bar_chart(pd.Series(grades), color="#1E3A8A")

                with list_col:
                    st.markdown("#### 🏆 Subject Ranking")
                    # Calculate Average per Subject
                    subject_performance = {}
                    for i, label in enumerate(df_analysis.iloc[header_idx]):
                        if str(label).strip().lower() == 'total':
                            sub_name = str(subject_labels.iloc[i-1]).strip()
                            if sub_name == 'nan' or sub_name == '': 
                                sub_name = str(subject_labels.iloc[i]).strip()
                            
                            sub_scores = pd.to_numeric(data_rows.iloc[:, i], errors='coerce').dropna()
                            if not sub_scores.empty:
                                subject_performance[sub_name] = round(sub_scores.mean(), 1)
                    
                    # Show as a clean table
                    perf_df = pd.DataFrame(list(subject_performance.items()), columns=['Subject', 'Avg %'])
                    st.dataframe(perf_df.sort_values(by='Avg %', ascending=False), hide_index=True, use_container_width=True)

                st.divider()
                
                # 3. INDIVIDUAL SEARCH FEATURE
                st.markdown("#### 🔍 Quick Student Insight")
                search_name = st.text_input("Enter Student Name to see Trend")
                if search_name:
                    student_match = data_rows[data_rows.iloc[:, 1].astype(str).str.contains(search_name, case=False)]
                    if not student_match.empty:
                        st.success(f"Student Found: {student_match.iloc[0, 1]}")
                        # You could add a radar chart or line chart here for individual progress
                    else:
                        st.warning("No student matches that name.")
            else:
                st.error("No Scoresheet detected in this file.")
        else:
            st.info("Please select a database file from the dropdown above to begin analysis.")

# --- 4. BULK GENERATOR & NOTIFICATIONS ---
    with tab_bulk:
        st.subheader("📦 Bulk Action Suite")
        bulk_class = st.selectbox("Select Class for Mass Action", get_available_classes(), key="bulk_action_selector")
        col_pdf, col_notif = st.columns(2)

        with col_pdf:
            st.markdown("#### 📄 Document Export")
            
            if st.button("🚀 GENERATE & PACKAGE ALL PDFs", use_container_width=True):
                target_file = f"Report {bulk_class}.xlsx"
                
                if os.path.exists(target_file):
                    xl = pd.ExcelFile(target_file)
                    sheets_to_load = [s for s in xl.sheet_names if any(k in s.lower() for k in ['bsheet', 'scoresheet', 'behaviour', 'skill', 'comment'])]
                    data_sheets = {s: xl.parse(s, header=None) for s in sheets_to_load}
                    
                    def find_s(key):
                        return next((s for s in data_sheets.keys() if key.lower() in s.lower()), None)

                    sc_n = find_s('Scoresheet')
                    if not sc_n:
                        st.error("❌ 'Scoresheet' not found.")
                    else:
                        # --- SMART TERM DETECTION ---
                        # Checks if '3rd' is in the sheet name or the filename
                        is_third_term = "3rd" in sc_n or "3rd" in target_file
                        current_term = "3rd Term" if is_third_term else " 2ND TERM"

                        df_sc_raw = data_sheets[sc_n]
                        adm_list = df_sc_raw.iloc[2:, 0].dropna().unique()

                        status_window = st.empty() 
                        progress_bar = st.progress(0)
                        button_placeholder = st.empty() 
                        
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w") as zf:
                            header_mask = df_sc_raw.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                            header_idx = df_sc_raw[header_mask].index[0] if any(header_mask) else 1
                            
                            subject_row = df_sc_raw.iloc[header_idx - 1]
                            label_row = df_sc_raw.iloc[header_idx] 

                            for index, adm_val in enumerate(adm_list):
                                adm_clean = str(adm_val).strip()
                                try:
                                    s_row_data = df_sc_raw[df_sc_raw.iloc[:, 0].astype(str).str.strip() == adm_clean]
                                    if s_row_data.empty: continue
                                    
                                    student_vals = s_row_data.iloc[0]
                                    student_name = str(student_vals.iloc[1]).upper()

                                    status_window.markdown(f"""
                                        <div style="padding:15px; border-radius:10px; background-color:#f8f9fa; border-left: 5px solid #1E3A8A;">
                                            <span style="color:#1E3A8A; font-weight:bold; font-size:12px;">GENERATING PHYSICAL REPORT...</span><br>
                                            <span style="font-size:18px; color:#333;">📄 <b>{student_name}</b></span>
                                        </div>
                                    """, unsafe_allow_html=True)

                                    # --- FULL PAGE PDF CONFIGURATION ---
                                    pdf = ResultPDF()
                                    # Set margins to 10mm to maximize A4 width (210mm)
                                    pdf.set_margins(left=10, top=10, right=10)
                                    pdf.set_auto_page_break(auto=True, margin=10)
                                    pdf.add_page()

                                    processed_results = {}
                                    total_marks = 0
                                    for i, label in enumerate(label_row):
                                        if str(label).strip().lower() == 'total':
                                            subject_name = "Unknown"
                                            for j in range(i, -1, -1):
                                                val = str(subject_row.iloc[j]).strip()
                                                if val.lower() != 'nan' and val != '':
                                                    subject_name = val
                                                    break
                                            try:
                                                ca = float(student_vals.iloc[i-2]) if pd.notna(student_vals.iloc[i-2]) else 0
                                                ex = float(student_vals.iloc[i-1]) if pd.notna(student_vals.iloc[i-1]) else 0
                                                tot = float(student_vals.iloc[i]) if pd.notna(student_vals.iloc[i]) else 0
                                                if subject_name != "Unknown":
                                                    processed_results[subject_name] = {"CA": ca, "Exam": ex, "Total": tot}
                                                    total_marks += tot
                                            except: continue

                                    def get_meta(key):
                                        sh = find_s(key)
                                        if not sh: return {}
                                        df = data_sheets[sh].copy()
                                        df.columns = [str(c).strip() for c in df.iloc[0]]
                                        m = df[df.iloc[:,0].astype(str).str.strip() == adm_clean]
                                        return m.iloc[0].to_dict() if not m.empty else {}

                                    summary = {
                                        'obtained': total_marks, 
                                        'avg': round(total_marks/max(1, len(processed_results)), 2), 
                                        'pos': get_meta('Bsheet').get('Position', 'N/A'), 
                                        'max': len(processed_results) * 100
                                    }
                                    
                                    # --- DRAWING LOGIC WITH CONDITIONAL TRANSCRIPT ---
                                    pdf.student_info_box(student_name, adm_clean, bulk_class, current_term, summary)
                                    
                                    # Table now fills 190mm (Standard A4 width minus margins)
                                    pdf.draw_scores_table(processed_results, bulk_class)
                                    
                                    # ONLY draw cumulative summary if it is 3rd Term
                                    if is_third_term:
                                        pdf.draw_transcript_summary(summary, current_term)
                                    
                                    # Adjusted footer to stay at the bottom of a single page
                                    pdf.draw_footer_sections(get_meta('Behaviour'), get_meta('Skill'), get_meta('Comment'), summary, bulk_class, current_term)
                                    
                                    # --- ADD RESUMPTION DATE TO PDF ---
                                    pdf.ln(10)
                                    pdf.set_font('Arial', 'B', 11)
                                    pdf.cell(0, 10, "NEXT TERM BEGINS: 20th APRIL, 2026", ln=1, align='C')                        
                                    
                                    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
                                    zf.writestr(f"{student_name.replace(' ', '_')}.pdf", pdf_bytes)

                                except Exception as e:
                                    st.error(f"Error for {adm_clean}: {e}")

                                progress_bar.progress((index + 1) / len(adm_list))

                        status_window.success(f"✅ READY! All {len(adm_list)} reports formatted for A4 printing.")
                        st.balloons()
                        
                        button_placeholder.download_button(
                            label="📥 DOWNLOAD ZIP PACKAGE NOW",
                            data=zip_buffer.getvalue(),
                            file_name=f"Reports_{bulk_class}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                else:
                    st.error(f"❌ File {target_file} not found.")
        with col_notif:
            st.markdown("#### 🔔 Parent Notifications")
            test_email = st.text_input("Test Email Address", placeholder="yourname@gmail.com")
            
            if st.button("🧪 Send Test Email"):
                success = send_email_notification(test_email, "Test Student", bulk_class, "RSC-TEST-001", "1234")
                if success: st.success("✅ Test Email Sent!")
                else: st.error("❌ Email Failed.")

            st.markdown("---")
            if st.button("📢 BLAST NOTIFY ALL PARENTS"):
                f_path = f"Report {bulk_class}.xlsx"
                if os.path.exists(f_path):
                    with st.spinner(f"Reading {bulk_class} Data..."):
                        try:
                            xls = pd.ExcelFile(f_path)
                            target_sheet = next((s for s in xls.sheet_names if 'data' in s.lower()), None)
                            if target_sheet:
                                df_bulk = pd.read_excel(f_path, sheet_name=target_sheet)
                                st.info(f"🚀 Found {len(df_bulk)} parents. Starting blast...")
                                p_bar = st.progress(0)
                                success_count = 0
                                for i, row in df_bulk.iterrows():
                                    try:
                                        p_email = str(row['Email']).strip()
                                        p_name = str(row['Names ']).strip()
                                        p_class = str(row['Class ']).strip()
                                        p_reg = str(row['Admission_No']).strip()
                                        p_pass = str(row['Password']).strip()
                                        if "@" in p_email:
                                            if send_email_notification(p_email, p_name, p_class, p_reg, p_pass):
                                                success_count += 1
                                    except: pass
                                    p_bar.progress((i + 1) / len(df_bulk))
                                st.success(f"🏁 Blast complete! {success_count} emails sent.")
                            else: st.error("❌ Sheet 'Data' not found.")
                        except Exception as e: st.error(f"❌ Error during blast: {e}")
                else: st.error("❌ File not found.")

# --- 5. CONTENT MANAGER (NOW CORRECTLY OUTSIDE TAB_BULK) ---
    with tab_content:
        st.markdown("### 📰 News & Protocol Control")
        if os.path.exists("news_event.jpg"):
            st.image("news_event.jpg", width=400)
        
        with st.form("news_update_form"):
            st.subheader("✍️ Update Dashboard News")
            new_title = st.text_input("Headline", value=st.session_state.news_content['title'])
            new_desc = st.text_area("Content", value=st.session_state.news_content['desc'])
            uploaded_news_img = st.file_uploader("Change Image", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("🚀 Publish & Save"):
                st.session_state.news_content.update({'title': new_title.upper(), 'desc': new_desc})
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                if uploaded_news_img:
                    with open("news_event.jpg", "wb") as f: f.write(uploaded_news_img.getbuffer())
                st.success("✅ News updated!")
                st.rerun()

# --- PROTOCOL & CONTACT UPDATES ---
        with st.form("protocol_updates_form"):
            st.subheader("📅 School Protocol & Contact Info")
            current_storage = st.session_state.get('portal_storage', {})
            
            col1, col2 = st.columns(2)
            with col1:
                new_calendar = st.text_area("School Calendar", value=current_storage.get('calendar', ''))
                new_contact = st.text_area("Contact Information", value=current_storage.get('contact', ''))
            with col2:
                new_guidelines = st.text_area("Exam Guidelines", value=current_storage.get('exams', ''))

            # Buttons for Saving and Clearing
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.form_submit_button("💾 Save Protocols"):
                st.session_state.portal_storage.update({'calendar': new_calendar, 'exams': new_guidelines, 'contact': new_contact})
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                st.success("✅ Dashboard updated!")
                st.rerun()
            
            if btn_col2.form_submit_button("🗑️ Clear All Protocol"):
                st.session_state.portal_storage.update({'calendar': '', 'exams': '', 'contact': ''})
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                st.warning("🚨 Protocol text cleared!")
                st.rerun()

        # --- NOTICE BOARD WITH UPLOAD & DELETE ---
        st.markdown("---")
        with st.form("notice_board_form"):
            st.subheader("📌 Pin to Notice Board")
            notice_name = st.text_input("Notice Title")
            uploaded_pdf = st.file_uploader("Upload PDF", type=['pdf'])
            
            if st.form_submit_button("📢 Upload & Pin"):
                if uploaded_pdf and notice_name:
                    target_dir = os.path.abspath("notices")
                    os.makedirs(target_dir, exist_ok=True)
                    clean_filename = f"notice_{notice_name.replace(' ', '_').lower()}.pdf"
                    final_path = os.path.join(target_dir, clean_filename)
                    file_bytes = uploaded_pdf.getvalue()
                    
                    try:
                        with open(final_path, "wb") as f: f.write(file_bytes)
                        if 'upload_notice_to_github' in globals():
                            upload_notice_to_github(file_bytes, clean_filename)
                        st.success(f"✅ '{notice_name}' pinned!")
                        st.rerun()
                    except Exception as e: st.error(f"Upload failed: {e}")

        # --- DELETE NOTICE SECTION ---
        st.subheader("🗑️ Delete Pinned Notices")
        notice_dir = os.path.abspath("notices")
        if os.path.exists(notice_dir):
            files = [f for f in os.listdir(notice_dir) if f.endswith(".pdf")]
            if files:
                to_delete = st.selectbox("Select notice to remove:", files)
                if st.button("🔥 Delete Selected Notice"):
                    os.remove(os.path.join(notice_dir, to_delete))
                    st.success(f"Successfully deleted {to_delete}")
                    st.rerun()
            else:
                st.info("No notices found to delete.")

# ==========================================
# --- 📊 DASHBOARD PAGE ---
# ==========================================
elif page == "📊 Dashboard":
        
    # 1. Assets & Initialization
    founder_path, lab_path, news_path = "founder.jpg", "lab.jpg", "news_event.jpg"
    lab_img_base64 = get_local_img(lab_path)

    # --- 2. QUOTES SECTION (FIXED INDENTATION) ---
    quotes = [
        "Education is the most powerful weapon which you can use to change the world.",
        "The beautiful thing about learning is that no one can take it away from you.",
        "Success is not final; failure is not fatal: it is the courage to continue that counts.",
        "The mind is not a vessel to be filled, but a fire to be kindled."
    ]
    
    selected_quote = random.choice(quotes)
    st.markdown(f"> *{selected_quote}*")
     
    # 2. TOP SECTION (Updated for Light Theme)
    st.markdown(f"""
        <div class="principal-quote">
            <small style="color:#2563eb; text-transform:uppercase; letter-spacing:1px;"><b>Principal's Quote of the Day</b></small><br>
            <span style="font-size:1.3em; color:#1e293b;">{random.choice(quotes)}</span>
        </div>
    """, unsafe_allow_html=True)

    # 3. TICKER
    announcement = st.session_state.news_content['title']
    st.markdown(f"""
        <div class="ticker-wrap">
            <div class="ticker">
                <span class="ticker-item">🌟 VISION: To produce highly qualified and potential leaders of tomorrow.</span>
                <span class="ticker-item">🎯 MISSION: To bridge the gap between the rich and the poor.</span>
                <span class="ticker-item">💎 VALUES: Hard work • Integrity • Moral Standard • Discipline • Honesty • Excellence • Team Spirit</span>
                <span class="ticker-item" style="color:#fbbf24;">📢 LATEST: {announcement}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

      # 4. VISION & MISSION
    v_col, m_col = st.columns(2)
    with v_col:
        st.markdown(f"""<div class="statement-box"><h3 style="color:#2563eb; text-align:center;">🔭 VISION STATEMENT</h3><p style="text-align:justify; line-height:1.6; color:#334155;">TO PROVIDE QUALITATIVE EDUCATION IN A SERENE AND SAFE LEARNING ENVIRONMENT, ENABLING US TO PRODUCE HIGHLY QUALIFIED AND POTENTIAL LEADERS OF TOMORROW.</p></div>""", unsafe_allow_html=True)
    with m_col:
        st.markdown(f"""<div class="statement-box"><h3 style="color:#2563eb; text-align:center;">🎯 MISSION STATEMENT</h3><p style="text-align:justify; line-height:1.6; color:#334155;">TO BRIDGE THE GAP BETWEEN THE RICH AND THE POOR. TO DEMONSTRATE ACHIEVEMENTS ACROSS THE RANGE OF STUDENTS, SO THAT OUR GRADUATES ARE WELL NURTURED IN LOVE TO EXCEL AND FIT IN ANY WHERE.</p></div>""", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#1e3a8a;'>💎 OUR CORE VALUES</h2>", unsafe_allow_html=True)
    cv_cols = st.columns(4)
    values = ["Hard work", "Integrity", "High moral standard", "Discipline", "Honesty", "Excellence", "Team spirit"]
    for idx, val in enumerate(values):
        cv_cols[idx % 4].markdown(f'<div class="core-value-card">{val.upper()}</div>', unsafe_allow_html=True)
    
    st.divider()

   # 5. METRICS SECTION (Redesigned with light theme classes)
    st.markdown("""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-label">Students</div>
                <div class="metric-value">2.4k</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">System</div>
                <div class="metric-value">100%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Subjects</div>
                <div class="metric-value">18</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Performance</div>
                <div class="metric-value">92%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

   # 6. HERITAGE & FOUNDER (Color Updates)
    col_hist, col_img = st.columns([2, 1])
    with col_hist:
        st.markdown('<div class="history-card"><h2 style="color:#1e3a8a;">A Heritage of Leadership</h2><p style="color:#334155;"> I give God all the Glory for Ruby Springfield College. Ruby Springfield started modestly as a standard bearer, introducing Secondary Education in a package completely different from what obtains in this part of the world. The school took off in 1998. Like a child it grew and waxed strong progressively to the fancy and admiration of all and sundry. Our watch words in this highly esteemed college is SUPREME EXCELLENCE.</p></div>', unsafe_allow_html=True)
    with col_img:
        if os.path.exists(founder_path):
            st.image(founder_path, use_container_width=True) 
        else:
            st.error("Founder Image Missing")

    # 7. PRACTICAL GALLERY
    st.markdown(f"""
        <div class="practical-gallery" style="background-image: url('data:image/jpeg;base64,{lab_img_base64}'); height: 250px; background-size: cover; border-radius: 15px; position: relative;">
            <div class="overlay-content" style="background: rgba(30, 58, 138, 0.7); position: absolute; bottom: 0; width: 100%; padding: 20px; border-radius: 0 0 15px 15px; color: white;">
                <h4 style="margin:0;">🧪 Advanced Chemical Research Lab</h4>
                <p style="margin:0;">Precision and discovery in every experiment.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

  # # 8. NEWS FEED & PROTOCOL (DASHBOARD SIDE)
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("<h3 style='color:#1e3a8a;'>🔔 RSC News Feed</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#2563eb;'>{st.session_state.news_content['title']}</h4>", unsafe_allow_html=True)
            if os.path.exists(news_path):
                with open(news_path, "rb") as f:
                    st.image(BytesIO(f.read()), use_container_width=True)
            st.markdown(f"<div style='margin-top:10px; color:#334155;'>{st.session_state.news_content['desc']}</div>", unsafe_allow_html=True)
    
    with col_r:
        st.markdown("<h3 style='color:#1e3a8a;'>🛠️ Official Protocol</h3>", unsafe_allow_html=True)
        st.markdown("""<style>.protocol-box {background-color: #eff6ff; color: #1e3a8a; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2563eb; border: 1px solid #e2e8f0; white-space: pre-wrap;}</style>""", unsafe_allow_html=True)

        # Accessing the live storage
        storage = st.session_state.get('portal_storage', {})

        if st.button("📅 School Calendar", use_container_width=True): 
            st.session_state.show_cal = not st.session_state.get('show_cal', False)
        if st.session_state.get('show_cal', False):
            cal_data = storage.get('calendar', 'Calendar update pending.')
            st.markdown(f'<div class="protocol-box"><b>🗓️ ACADEMIC CALENDAR:</b><br>{cal_data}</div>', unsafe_allow_html=True)

        if st.button("📜 Exam Guidelines", use_container_width=True): 
            st.session_state.show_exam = not st.session_state.get('show_exam', False)
        if st.session_state.get('show_exam', False):
            exam_data = storage.get('exams', 'Proper uniform and ID card required for entry.')
            st.markdown(f'<div class="protocol-box"><b style="color:#2563eb;">EXAM PROTOCOL:</b><br>{exam_data}</div>', unsafe_allow_html=True)

        if st.button("📞 Contact Info", use_container_width=True): 
            st.session_state.show_contact = not st.session_state.get('show_contact', False)
        if st.session_state.get('show_contact', False):
            contact_data = storage.get('contact', 'School Office: Maiduguri, Borno State.')
            st.markdown(f'<div class="protocol-box"><b>📞 OFFICIAL CONTACT:</b><br>{contact_data}</div>', unsafe_allow_html=True)

    # 9. NOTICE BOARD
    st.markdown("---")
    st.markdown("<h3 style='color:#1e3a8a;'>📂 School Notice Board</h3>", unsafe_allow_html=True)
    
    if os.path.exists("notices"):
        notice_files = [f for f in os.listdir("notices") if f.endswith('.pdf')]
        if notice_files:
            n_cols = st.columns(3)
            for idx, filename in enumerate(notice_files):
                with n_cols[idx % 3]:
                    with st.container(border=True):
                        clean_title = filename.replace("notice_", "").replace(".pdf", "").replace("_", " ").upper()
                        st.markdown(f"<b style='color:#1e293b;'>📄 {clean_title}</b>", unsafe_allow_html=True)
                        file_path = os.path.join("notices", filename)
                        with open(file_path, "rb") as f:
                            st.download_button(label="📥 View PDF", data=f, file_name=filename, mime="application/pdf", key=f"pub_dl_{idx}", use_container_width=True)
        else:
            st.info("The notice board is currently empty.")
    
    # 10. FOOTER (Kept professional/solid as requested)
    st.markdown('<div class="footer-section"><p>© 2026 Ruby Springfield College • Developed by Adam Usman</p><div class="watermark-text">Powered by SumiLogics(NJA)</div></div>', unsafe_allow_html=True)

























