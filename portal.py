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
import requests # Added for the GitHub Robot

# --- STEP 1: PAGE CONFIG ---
st.set_page_config(
    page_title="Ruby Springfield College | Official Portal",
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STEP 2: SECRETS (The Safe Box) ---
# We pull these now so they are ready for the Admin Console
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_PATH"]
except Exception as e:
    st.warning("Running in Local Mode: Secrets not detected.")

# --- STEP 3: GOOGLE VERIFICATION ---
verify_code = "lJuiVMz6tsO5tGGxk2wTWmFydMeB7gxsQyuUJger6cg"
# This puts the code in the body where Google can find it
st.markdown(f'<div style="display:none;">google-site-verification: {verify_code}</div>', unsafe_allow_html=True)

# --- STEP 3: VISIBLE SCHOOL BRANDING ---
st.markdown(
    """
    <div style="text-align: center; padding-top: 10px;">
        <h1 style="color: #1E3A8A; font-family: 'Arial'; margin-bottom: 0;">Ruby Springfield College</h1>
        <h3 style="color: #555; margin-top: 0;">Official Academic Management & Result Portal</h3>
        <p style="font-weight: bold; color: #1E3A8A;">Maiduguri, Borno State, Nigeria</p>
        <hr style="border: 1px solid #1E3A8A; width: 60%; margin: auto;">
    </div>
    """, 
    unsafe_allow_html=True
)
def upload_notice_to_github(file_bytes, file_name):
    """The 'Shutdown Robot' that pushes PDFs to GitHub notices folder"""
    url = f"https://api.github.com/repos/{REPO}/contents/notices/{file_name}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Prepare the file for the internet
    encoded_content = base64.b64encode(file_bytes).decode("utf-8")
    
    # GitHub data packet
    data = {
        "message": f"New Notice: {file_name}",
        "content": encoded_content,
        "branch": "main"
    }
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code
    
# --- STEP 4: PERMANENT STORAGE ENGINE ---
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
            df = pd.read_excel(storage_path, engine='openpyxl')
            # This line converts your Excel rows into a usable dictionary
            return dict(zip(df['Key'].astype(str), df['Value'].astype(str)))
        except Exception:
            return defaults
    # This return MUST be perfectly aligned with the "if" above it
    return defaults

# Initialize the storage so other parts of the code can see it
if 'portal_storage' not in st.session_state:
    st.session_state.portal_storage = load_portal_data()
    
# --- STEP 2: EMAIL NOTIFICATION CORE ---
def send_email_notification(receiver_email, student_name, class_name):
    """
    Shutdown, this handles the actual mailing process.
    Ensure you use a Google 'App Password' for security.
    """
    sender_email = "sumilogics247@gmail.com"
    sender_password = "upsw jbon rhoy aiai" 
    
    message = MIMEMultipart()
    message["From"] = f"School Portal Admin <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"🔔 Results Published: {student_name}"

    body = f"""
    Dear Parent/Guardian,

    The academic results for {student_name} ({class_name}) have been processed 
    and are now available for viewing on the school portal.

    Please log in with the student's ID to download the result.

    Best Regards,
    School Management
    """
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def get_local_img(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"
    except FileNotFoundError:
        return "https://via.placeholder.com/600x400?text=Image+Not+Found"
        
        # --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.jpg") 
SIG_PATH = os.path.join(BASE_DIR, "signature.png") 
STAMP_PATH = os.path.join(BASE_DIR, "Stamp.jpg") 

# STAFF ACCESS CONFIGURATION
STAFF_MASTER_KEY = "ADMIN2026" 

def log_activity(user_type, action, details):
    """
    Step 6: Security & Logging System
    Records system usage to a local file for security audits.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {user_type.upper()} | {action} | {details}\n"
        with open("system_audit.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass # Prevents app from crashing if log file is locked

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
            
            r1 = df_sc.iloc[header_idx-1] # Subjects
            r2 = df_sc.iloc[header_idx]   # "Total" labels
            
            subjects = []
            averages = []
            total_cols = [] # Track columns for Step 3
            
            for i in range(len(r2)):
                if str(r2.iloc[i]).strip().lower() == "total":
                    total_cols.append(i)
                    # --- SMART SUBJECT NAME DETECTION ---
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

# --- PROFESSIONAL BLUE & HARSH DARK CSS ---
st.markdown("""
    <style>
    /* Main Background: Harsh Dark Slate */
    .stApp { 
        background: linear-gradient(135deg, #0a0f1e 0%, #111827 100%); 
        color: #f1f5f9; 
    }
    
    /* Sidebar: Deep Black-Blue with Blue Border */
    [data-testid="stSidebar"] {
        background-color: #030712 !important;
        border-right: 3px solid #2563eb;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }

    /* Logo Border: Clean White with Blue Glow */
    .school-logo-border {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 4px double #2563eb;
        padding: 5px;
        background: white;
        object-fit: cover;
        box-shadow: 0px 0px 20px rgba(37, 99, 235, 0.4);
    }
    
    /* Quote Box: Subtle Blue Tint */
    .principal-quote {
        background: rgba(37, 99, 235, 0.1);
        border-left: 5px solid #2563eb;
        padding: 20px;
        margin: 10px 0 25px 0;
        border-radius: 0 15px 15px 0;
        font-family: 'Georgia', serif;
        color: #f1f5f9;
    }

    /* Ticker: Blue & Harsh Dark */
    .ticker-wrap {
        width: 100%; overflow: hidden; height: 40px; 
        background-color: #0f172a; 
        border-bottom: 2px solid #2563eb;
        border-top: 2px solid #2563eb;
        display: flex; align-items: center; margin-bottom: 20px;
    }
    .ticker {
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 60s linear infinite; font-weight: bold; color: #ffffff;
    }
    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    .ticker-item { display: inline-block; padding: 0 50px; }

    /* Content Boxes: Dark with Blue Outlines */
    .statement-box {
        background: rgba(255, 255, 255, 0.03);
        border: 2px solid #2563eb;
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    /* Value Cards: Harsh Hover Effect */
    .core-value-card {
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.4);
        padding: 10px; border-radius: 10px; text-align: center;
        font-weight: bold; color: #ffffff; transition: 0.3s;
    }
    .core-value-card:hover { 
        background: #2563eb; 
        color: #ffffff;
        box-shadow: 0 0 15px #2563eb;
    }
    
    .school-bio {
        text-align: center; max-width: 900px; margin: 0 auto 40px auto;
        font-style: italic; color: #cbd5e1; font-size: 1.2em; line-height: 1.6;
    }

    .history-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 20px; padding: 35px; border: 1px solid rgba(37, 99, 235, 0.2);
        margin-bottom: 25px; line-height: 1.8; color: #ffffff;
    }

    .protocol-box {
        background: #030712; border-left: 5px solid #2563eb;
        padding: 20px; border-radius: 12px; margin-top: 10px; margin-bottom: 10px;
        color: #ffffff;
    }

    /* Footer: Solid Dark Blue */
    .footer-section {
        margin-top: 60px; padding: 40px; background: #020617;
        border-radius: 40px 40px 0 0; text-align: center; border-top: 3px solid #2563eb;
    }
    
    .footer-info {
        color: #cbd5e1; font-size: 0.9em; margin-bottom: 15px; line-height: 1.5;
    }

    .watermark-text {
        color: rgba(37, 99, 235, 0.5); font-size: 0.8em; letter-spacing: 2px; margin-top: 10px; font-weight: bold;
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
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        flex: 1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .metric-label {
        color: #fbbf24;
        font-size: 0.8rem;
        text-transform: uppercase;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .metric-value {
        color: #f8fafc;
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
            pass # Safety skip if rotation is not supported

    def header(self):
        from datetime import datetime
        self.draw_watermark()
        
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 22) 
        
        # School Name & Motto
        self.set_font('Arial', 'B', 16)
        self.set_text_color(40, 70, 120) 
        self.cell(0, 8, 'RUBY SPRINGFIELD COLLEGE', 0, 1, 'C') 
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, 'Motto: A Citadel of Excellence', 0, 1, 'C') 
        
        # Right Side Branding & Date
        self.set_font('Arial', '', 7)
        self.set_text_color(0, 0, 0)
        self.cell(0, 4, 'Opposite Polo Field, Old GRA, Maiduguri, Borno State', 0, 1, 'R') 
        self.cell(0, 4, 'Contact: 08131032577', 0, 1, 'R') 
        
        # Current Date
        curr_date = datetime.now().strftime("%d %B, %Y")
        self.set_font('Arial', 'I', 6)
        self.cell(0, 3, f'Generated on: {curr_date}', 0, 1, 'R')
        
        # Developer Credit
        self.set_font('Arial', 'B', 6)
        self.set_text_color(150, 150, 150)
        self.cell(0, 3, 'Developed by: Adam Usman | Powered by SumiLogics(NJA)', 0, 1, 'R')
        
        self.ln(2)
        self.set_fill_color(200, 210, 230) 
        self.set_font('Arial', 'B', 10)
        self.set_text_color(40, 70, 120)
        self.cell(0, 8, 'OFFICIAL TERMLY PERFORMANCE RECORD', 1, 1, 'C', 1) 
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(128, 128, 128)
        footer_note = "Copyright 2026 Ruby Springfield College - Dev: Adam Usman (SumiLogics NJA)"
        self.cell(0, 10, footer_note, 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')

    def student_info_box(self, student_name, adm, s_class, term, summary):
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 8)
        start_y = self.get_y()
        self.cell(30, 5, 'Name of student:', 0, 0) 
        self.set_font('Arial', '', 9)
        self.cell(80, 5, f" {student_name.upper()}", 'B', 1)
        self.set_font('Arial', 'B', 8)
        self.cell(30, 5, 'Admission No:', 0, 0) 
        self.set_font('Arial', '', 9)
        self.cell(80, 5, f" {adm}", 'B', 1)
        self.set_font('Arial', 'B', 8)
        self.cell(30, 5, 'Class:', 0, 0) 
        self.set_font('Arial', '', 9)
        self.cell(80, 5, f" {s_class}   |   Term: {term}", 'B', 1)

        self.set_xy(135, start_y)
        self.set_fill_color(245, 245, 245)
        self.set_font('Arial', 'B', 7)
        self.cell(35, 5, 'Obtained Score:', 1, 0, 'L', 1)
        self.cell(25, 5, f"{summary['obtained']}", 1, 1, 'C')
        self.set_x(135)
        self.cell(35, 5, 'Average / Pos:', 1, 0, 'L', 1)
        self.cell(25, 5, f"{summary['avg']}% / {summary['pos']}", 1, 1, 'C')
        self.set_x(135)
        self.cell(35, 5, 'Total Possible:', 1, 0, 'L', 1)
        self.cell(25, 5, f"{summary['max']}", 1, 1, 'C')
        self.ln(3)

    def draw_scores_table(self, subject_data, s_class):
        num_sub = len(subject_data)
        row_h = 5.5 if num_sub < 15 else 4.8
        f_size = 8 if num_sub < 15 else 7
        self.set_fill_color(40, 70, 120) 
        self.set_text_color(255, 255, 255) 
        self.set_font('Arial', 'B', f_size)
        
        is_ss = "SS" in str(s_class).upper() and "JSS" not in str(s_class).upper()
        w = [70, 25, 25, 25, 45] if is_ss else [70, 30, 30, 30, 30]
        headers = ['Subject', 'C.A (40%)', 'Exam (60%)', 'Total (100%)', 'Grade & Remark' if is_ss else 'Grade']
        
        for i in range(len(headers)):
            self.cell(w[i], row_h + 1, headers[i], 1, 0, 'C', 1)
        self.ln()
        
        self.set_text_color(0, 0, 0) 
        self.set_font('Arial', '', f_size)
        for sub, scores in subject_data.items():
            valid = scores['Total'] > 0 and not pd.isna(scores['Total'])
            ca_val = str(scores['CA']) if valid else ""
            ex_val = str(scores['Exam']) if valid else ""
            tot_val = str(scores['Total']) if valid else ""
            
            self.cell(w[0], row_h, sub, 1)
            self.cell(w[1], row_h, ca_val, 1, 0, 'C')
            self.cell(w[2], row_h, ex_val, 1, 0, 'C')
            self.cell(w[3], row_h, tot_val, 1, 0, 'C')
            
            g = ""
            if valid:
                t = scores['Total']
                if is_ss:
                    if t >= 75: g = "A1 (EXCELLENT)"
                    elif t >= 70: g = "B2 (V-GOOD)"
                    elif t >= 65: g = "B3 (GOOD)"
                    elif t >= 60: g = "C4 (CREDIT)"
                    elif t >= 55: g = "C5 (CREDIT)"
                    elif t >= 50: g = "C6 (CREDIT)"
                    elif t >= 45: g = "D7 (PASS)"
                    elif t >= 40: g = "E8 (PASS)"
                    else: g = "F9 (FAIL)"
                else:
                    if t >= 75: g = "A (DISTINCTION)"
                    elif t >= 65: g = "B (UPPER CREDIT)"
                    elif t >= 55: g = "C (LOWER CREDIT)"
                    elif t >= 45: g = "D (PASS)"
                    elif t >= 40: g = "E (PASS)"
                    else: g = "F (FAIL)"
            self.cell(w[-1], row_h, g, 1, 1, 'C')
        self.ln(2)

    def draw_transcript_summary(self, summary, term):
        if "3rd" in str(term):
            self.set_fill_color(220, 230, 245)
            self.set_font('Arial', 'B', 7)
            self.cell(0, 5, 'ANNUAL CUMULATIVE TRANSCRIPT', 1, 1, 'C', 1)
            t1, t2, t3 = summary.get('t1_avg', 0), summary.get('t2_avg', 0), summary.get('avg', 0)
            cum = round((t1 + t2 + t3) / 3, 2) if t1 > 0 else t3
            self.cell(47, 4, '1st Term Avg', 1, 0, 'C'); self.cell(47, 4, '2nd Term Avg', 1, 0, 'C')
            self.cell(47, 4, '3rd Term Avg', 1, 0, 'C'); self.cell(49, 4, 'CUMULATIVE AVG (%)', 1, 1, 'C')
            self.set_font('Arial', '', 7)
            self.cell(47, 5, f"{t1}%", 1, 0, 'C'); self.cell(47, 5, f"{t2}%", 1, 0, 'C')
            self.cell(47, 5, f"{t3}%", 1, 0, 'C'); self.cell(49, 5, f"{cum}%", 1, 1, 'C')
            self.ln(1)

    def draw_footer_sections(self, beh, sk, comm, summary, s_class, term):
        is_ss = "SS" in str(s_class).upper() and "JSS" not in str(s_class).upper()
        curr_y = self.get_y()
        if curr_y > 235: self.ln(-8)
        
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 7)
        self.cell(55, 5, 'AFFECTIVE DOMAIN (A)', 1, 1, 'C', 1)
        self.set_font('Arial', '', 6.5)
        for k, v in list(beh.items())[1:9]: 
            self.cell(40, 4.2, k, 1, 0); self.cell(15, 4.2, str(v), 1, 1, 'C')

        self.ln(1)
        self.set_font('Arial', 'B', 7); self.cell(55, 4.5, 'POSITION OF RESPONSIBILITY', 1, 1, 'L', 1)
        self.set_font('Arial', '', 6.5); self.cell(55, 4.5, f" {comm.get('Position', 'None')}", 1, 1, 'L')

        self.set_xy(75, curr_y)
        self.set_font('Arial', 'B', 7); self.cell(55, 5, 'PSYCHOMOTOR SKILLS (B)', 1, 1, 'C', 1)
        self.set_font('Arial', '', 6.5)
        for k, v in list(sk.items())[1:6]:
            self.set_x(75); self.cell(40, 4.2, k, 1, 0); self.cell(15, 4.2, str(v), 1, 1, 'C')

        self.set_xy(140, curr_y)
        self.set_font('Arial', 'B', 7); self.cell(60, 4.5, "HOUSE MASTER'S REPORT", 1, 1, 'L', 1)
        self.set_x(140); self.set_font('Arial', '', 6.5)
        self.cell(60, 5, f" {comm.get('House_Master_Report', 'Satisfactory')}", 1, 1, 'L')

        self.ln(1); self.set_x(140); self.set_font('Arial', 'B', 7)
        self.cell(60, 4.5, "FORM MASTER'S COMMENT", 1, 1, 'L', 1)
        self.set_x(140); self.set_font('Arial', '', 6.5)
        self.cell(60, 5, f" {comm.get('Form_Master_Comment', 'Good performance.')}", 1, 1, 'L')

        self.ln(1); self.set_x(140); self.set_font('Arial', 'B', 7)
        self.cell(60, 4.5, "PRINCIPAL'S COMMENT", 1, 1, 'L', 1)
        self.set_x(140)
        
        avg = summary['avg']
        if is_ss:
            if avg >= 75: p_remark = "Outstanding performance. Maintain focus."
            elif avg >= 50: p_remark = "Average performance. Attention needed."
            else: p_remark = "Poor result. Urgent academic intervention required."
            self.set_font('Arial', 'I', 6)
        else:
            if avg >= 75: p_remark = "An Impressive performance! Keep it up."
            elif avg >= 50: p_remark = "A fair performance. Work harder."
            else: p_remark = "Performance is not up to par. Sit up."
            self.set_font('Arial', 'I', 6.5)
            
        self.multi_cell(60, 4, f" {p_remark}", 1, 'L')

        if "3rd" in str(term):
            self.ln(1.5); self.set_x(10); self.set_font('Arial', 'B', 8)
            status = "PROMOTED TO NEXT CLASS" if avg >= 40 else "HELD BACK"
            self.cell(125, 6, f"PROMOTION STATUS: {status}", 1, 1, 'C')
        
        self.ln(2.5); sig_y = self.get_y()
        if os.path.exists(STAMP_PATH): self.image(STAMP_PATH, 142, sig_y - 4, 20) 
        if os.path.exists(SIG_PATH): self.image(SIG_PATH, 158, sig_y - 2, 15)
        self.set_x(140); self.cell(60, 0, '', 'T', 1, 'C')
        self.set_x(140); self.set_font('Arial', 'B', 6)
        self.cell(60, 3, "Principal's Signature & Stamp", 0, 1, 'C')
#--- SIDEBAR ---#
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
    adm_no = st.sidebar.text_input("Admission Number")
    
    # --- SUMI SECRET ACCESS ---
    if adm_no == "SUMI":
        st.balloons()
        st.title("👸 Queen Maryam's Portal")
        st.success(f"Access Granted for Shutdown & {Babe}") # Babe/Queen from memory
        st.write(f"**Relationship Status:** Planning marriage in 7-8 years.")
        st.info("Keep building the Master Code, Adam.")
        st.stop()

    pwd = st.sidebar.text_input("Access Key", type="password")
    selected_class = st.sidebar.selectbox("Class", get_available_classes())
    login_btn = st.sidebar.button("Generate Report")

    if login_btn:
        file_path = f"Report {selected_class}.xlsx"
        if os.path.exists(file_path):
            # --- MEMORY OPTIMIZATION START ---
            try:
                # Instead of sheet_name=None (which loads everything), we use ExcelFile
                xl = pd.ExcelFile(file_path)
                
                if 'Data' in xl.sheet_names:
                    # Only load the Data sheet for login
                    df_data = xl.parse('Data', header=None)
                    df_data.columns = [str(c).strip() for c in df_data.iloc[0]]
                    df_data = df_data[1:]
                    
                    cols = df_data.columns.tolist()
                    adm_col = next((c for c in cols if "admission" in c.lower()), "Admission_No")
                    pwd_col = next((c for c in cols if "pass" in c.lower() or "key" in c.lower()), "Password")
                    name_col = next((c for c in cols if "name" in c.lower()), "Name")
                    
                    adm_clean = str(adm_no).strip()
                    pwd_clean = str(pwd).strip()

                    user = df_data[(df_data[adm_col].astype(str).str.strip() == adm_clean) & 
                                   (df_data[pwd_col].astype(str).str.strip() == pwd_clean)]

                    if not user.empty:
                        student = user.iloc[0]
                        student_name = str(student.get(name_col, 'Student')).upper()
                        term = student.get('Term', 'N/A')
                        
                        log_activity("Student", "Login", f"Success: {student_name} ({adm_clean})")

                        # Load other sheets only if login is successful
                        sheets_to_load = [s for s in xl.sheet_names if any(k in s.lower() for k in ['bsheet', 'scoresheet', 'behaviour', 'skill', 'comment'])]
                        data_sheets = {s: xl.parse(s, header=None) for s in sheets_to_load}

                        # Helper to find specific sheets
                        def find_s(key):
                            for s in data_sheets.keys():
                                if key.lower() in s.lower(): return s
                            return None

                        bs_n, sc_n = find_s('Bsheet'), find_s('Scoresheet')
                        beh_n, sk_n, com_n = find_s('Behaviour'), find_s('Skill'), find_s('Comment')

                        # BroadSheet Logic (Position)
                        pos_val = "N/A"
                        if bs_n:
                            df_bs = data_sheets[bs_n]
                            df_bs.columns = [str(c).strip() for c in df_bs.iloc[0]]
                            match = df_bs[df_bs.iloc[:,0].astype(str).str.strip() == adm_clean]
                            if not match.empty: pos_val = match.iloc[0].get('Position', 'N/A')

                        processed_results = {}; total_sum = 0
                        if sc_n:
                            df_sc = data_sheets[sc_n]
                            header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                            header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
                            r1, r2 = df_sc.iloc[header_idx-1], df_sc.iloc[header_idx]
                            
                            # Applied your specific iloc request here:
                            header_row = df_sc.iloc[header_idx] 
                            
                            s_row = df_sc[df_sc.iloc[:,0].astype(str).str.strip() == adm_clean]
                            if not s_row.empty:
                                s_vals = s_row.iloc[0]
                                for i, col_val in enumerate(header_row):
                                    if str(col_val).strip().lower() == 'total':
                                        sub = "Unknown"
                                        for j in range(i, -1, -1):
                                            val = str(r1.iloc[j]).strip()
                                            if val.lower() != 'nan' and val != '':
                                                sub = val; break
                                        try:
                                            ca = float(s_vals.iloc[i-2]) if pd.notna(s_vals.iloc[i-2]) else 0
                                            ex = float(s_vals.iloc[i-1]) if pd.notna(s_vals.iloc[i-1]) else 0
                                            tot = float(s_vals.iloc[i]) if pd.notna(s_vals.iloc[i]) else 0
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

                        # --- PDF LOGIC ---
                        try:
                            pdf = ResultPDF()
                            pdf.add_page()
                            pdf.student_info_box(student_name, adm_clean, selected_class, term, summary)
                            pdf.draw_scores_table(processed_results, selected_class)
                            pdf.draw_footer_sections(beh, sk, comm, summary, selected_class, term)
                            pdf_output = pdf.output(dest='S')
                            pdf_bytes = pdf_output.encode('latin-1', errors='replace') if isinstance(pdf_output, str) else pdf_output
                            st.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"{student_name}.pdf")
                        except Exception as e:
                            st.error(f"PDF Error: {e}")

                    else:
                        st.error("❌ Invalid ID or Key.")
                else:
                    st.error("Sheet 'Data' not found.")
            except Exception as e:
                st.error(f"System Error: {e}")
            # --- MEMORY OPTIMIZATION END ---
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
    
    tab_up, tab_db, tab_analytics, tab_bulk, tab_content = st.tabs([
        "📤 Upload/Update", "📂 Database & Logs", "📈 Class Insights", "📦 Bulk & Notifications", "📢 Content Manager"
    ])
    
    # --- 1. UPLOAD TAB ---
    # --- 1. UPLOAD TAB (WITH GITHUB AUTO-OVERWRITE) ---
    with tab_up:
        st.info("Upload class results here. Format: 'Report ClassName.xlsx'")
        target_class = st.text_input("Target Class Name (e.g., JSS 1A)", key="upload_target")
        new_file = st.file_uploader("Select Excel Spreadsheet", type=['xlsx'])
        
        if st.button("Deploy to System") and new_file and target_class:
            save_filename = f"Report {target_class}.xlsx"
            file_bytes = new_file.getvalue() # Get data for GitHub sync
            
            # 1. LOCAL SAVE (For immediate use in the portal)
            with open(save_filename, "wb") as f:
                f.write(file_bytes)
            
            # 2. GITHUB OVERWRITE (Robot Logic)
            with st.spinner(f"🚀 Syncing {save_filename} with GitHub..."):
                # This calls your 'upload_notice_to_github' function
                # It handles checking for the SHA and overwriting automatically
                status = upload_notice_to_github(file_bytes, save_filename)
            
            # 3. LOGGING & SUCCESS FEEDBACK
            if status in [200, 201]:
                log_activity("Admin", "Upload", f"Uploaded and Synced: {save_filename}")
                st.balloons()
                st.success(f"✅ SUCCESS: {save_filename} is now live on Portal & GitHub!")
            else:
                # If GitHub fails, the local file still works, but we warn you
                log_activity("Admin", "Upload Error", f"GitHub Sync failed for {save_filename}")
                st.warning(f"⚠️ Local update successful, but GitHub Sync Error: {status}")

    # --- 2. DATABASE & LOGS TAB ---
    with tab_db:
        col_db, col_log = st.columns(2)
        with col_db:
            st.subheader("📂 Live Databases")
            # Refreshing the file list
            live_files = glob.glob("Report *.xlsx")
            st.write(f"Total: {len(live_files)}")
            for file in live_files:
                st.code(file)
        
     with col_log:
            st.subheader("🕵️ Security Audit")
            if os.path.exists("system_audit.log"):
                with open("system_audit.log", "r") as f:
                    logs = f.readlines()
                # Added 'key' to prevent the Duplicate ID error
                st.text_area("Recent Activity", "".join(logs[-15:]), height=200, key="admin_audit_logs")
            else:
                st.info("No logs generated yet.")
                
    # --- 3. ANALYTICS TAB (FULL CLASS INSIGHTS) ---
    with tab_analytics:
        available_classes = get_available_classes()
        if not available_classes:
            st.warning("No databases found to analyze.")
        else:
            selected_analysis = st.selectbox("Analyze Class Performance", available_classes, key="analysis_select")
            if st.button("Run Analysis"):
                f_path = f"Report {selected_analysis}.xlsx"
                if os.path.exists(f_path):
                    d_sheets = pd.read_excel(f_path, sheet_name=None, header=None)
                    sc_key = next((k for k in d_sheets.keys() if k.lower() == 'scoresheet'), None)
                    
                    if sc_key:
                        df_sc = d_sheets[sc_key]
                        header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
                        header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
                        header_row = df_sc.iloc[header_idx] 
                        subject_row = df_sc.iloc[header_idx - 1]
                        
                        subject_stats = []
                        total_cols = []
                        
                        for i, col_val in enumerate(header_row): 
                            if str(col_val).strip().lower() == 'total':
                                total_cols.append(i) 
                                sub_name = str(subject_row.iloc[i]).strip()
                                # Refined merge-cell detection
                                if sub_name.lower() == 'nan' or sub_name == '':
                                    for look_back in range(i-1, max(-1, i-10), -1):
                                        val = str(subject_row.iloc[look_back]).strip()
                                        if val.lower() != 'nan' and val != '':
                                            sub_name = val
                                            break
                                if sub_name.lower() == 'nan': sub_name = f"Subject {i}"
                                scores = pd.to_numeric(df_sc.iloc[header_idx+1:, i], errors='coerce').dropna()
                                if not scores.empty:
                                    subject_stats.append({"Subject": sub_name, "Average Score": round(scores.mean(), 2)})
                        
                        if subject_stats:
                            df_stats = pd.DataFrame(subject_stats)
                            
                            # --- STEP 3: MANAGEMENT SUMMARY ---
                            st.subheader("📋 Management Summary")
                            data_rows = df_sc.iloc[header_idx+1:, :]
                            at_risk_list = []
                            for _, row in data_rows.iterrows():
                                s_name = row.iloc[1]
                                # Detect if student is failing 3+ subjects
                                fails = sum(1 for c in total_cols if pd.to_numeric(row.iloc[c], errors='coerce') < 40)
                                if fails >= 3:
                                    at_risk_list.append({"Student": s_name, "Failing": fails})

                            m1, m2, m3 = st.columns(3)
                            m1.metric("Class Average", f"{round(df_stats['Average Score'].mean(), 1)}%")
                            m2.metric("Total Students", len(data_rows))
                            m3.metric("At-Risk", len(at_risk_list))

                            if at_risk_list:
                                with st.expander("⚠️ View At-Risk Students"):
                                    st.table(pd.DataFrame(at_risk_list))

                            # Charts
                            fig_bar = px.bar(df_stats, x='Subject', y='Average Score', 
                                           title=f"Class Subject Performance: {selected_analysis}",
                                           color='Average Score', color_continuous_scale='Viridis', text_auto=True)
                            st.plotly_chart(fig_bar, use_container_width=True)

                            st.markdown("---")
                            col_lead, col_pie = st.columns([1, 1])
                            with col_lead:
                                st.subheader("🏆 Class Leaderboard")
                                grand_idx = total_cols[-1]
                                df_lead = df_sc.iloc[header_idx+1:, [0, 1, grand_idx]].copy()
                                df_lead.columns = ['ID', 'Name', 'TotalScore']
                                df_lead['TotalScore'] = pd.to_numeric(df_lead['TotalScore'], errors='coerce')
                                top_3 = df_lead.nlargest(3, 'TotalScore')
                                for rank, (idx, row) in enumerate(top_3.iterrows(), 1):
                                    st.success(f"{rank}. **{row['Name']}** - {row['TotalScore']} pts")
                            
                            with col_pie:
                                st.subheader("📈 Grade Spread")
                                all_totals = pd.to_numeric(df_sc.iloc[header_idx+1:, total_cols].values.flatten(), errors='coerce')
                                all_totals = all_totals[~np.isnan(all_totals)]
                                grades = {"A (75+)": sum(all_totals >= 75), "B (65-74)": sum((all_totals >= 65) & (all_totals < 75)), 
                                          "C (50-64)": sum((all_totals >= 50) & (all_totals < 65)), "Fail (<50)": sum(all_totals < 50)}
                                fig_pie = px.pie(names=list(grades.keys()), values=list(grades.values()), color_discrete_sequence=px.colors.qualitative.Pastel)
                                st.plotly_chart(fig_pie, use_container_width=True)
                            
                            log_activity("Admin", "Analysis", f"Ran full stats for {selected_analysis}")
                        else:
                            st.warning("No performance data found.")

   # --- 4. BULK GENERATOR & NOTIFICATIONS ---
    with tab_bulk:
        st.subheader("📦 Bulk Result Generator & Parent Alerts")
        
        # This dropdown controls which class file we pull emails from
        bulk_class = st.selectbox("Select Class for Mass Action", get_available_classes(), key="bulk_target")
        
        # Everything inside this block is now correctly indented under tab_bulk
        col_pdf, col_notif = st.columns(2)
        
        with col_pdf:
            st.markdown("#### 📄 Document Export")
            if st.button("🚀 GENERATE ALL PDFs"):
                st.info(f"Generating reports for {bulk_class}...")
                # Your PDF generation logic sits here

        with col_notif:
            st.markdown("#### 🔔 Parent Notifications")
            test_email = st.text_input("Test Email Address", placeholder="yourname@gmail.com")
            
            if st.button("🧪 Send Test Email"):
                success = send_email_notification(test_email, "Test Student", bulk_class)
                if success: 
                    st.success("Test Email Sent!")
                else: 
                    st.error("Email Failed. Check SMTP settings.")

            st.markdown("---")
            
            if st.button("📢 BLAST NOTIFY ALL PARENTS"):
                f_path = f"Report {bulk_class}.xlsx"
                
                if os.path.exists(f_path):
                    with st.spinner(f"Extracting all contacts for {bulk_class}..."):
                        try:
                            # Direct check of the 'Data' sheet for all 43+ students
                            xls = pd.ExcelFile(f_path)
                            target_sheet = next((s for s in xls.sheet_names if 'data' in s.lower()), None)
                            
                            if target_sheet:
                                df_data = pd.read_excel(f_path, sheet_name=target_sheet)
                                df_data.columns = [str(c).strip().lower() for c in df_data.columns]
                                
                                name_col = next((c for c in df_data.columns if 'name' in c), None)
                                email_col = next((c for c in df_data.columns if 'email' in c), None)
                                
                                if name_col and email_col:
                                    # Force conversion to string to catch every row
                                    df_data[name_col] = df_data[name_col].astype(str).str.strip()
                                    df_data[email_col] = df_data[email_col].astype(str).str.strip()
                                    
                                    # Filter for valid emails
                                    valid_contacts = df_data[df_data[email_col].str.contains("@", na=False)]
                                    
                                    if not valid_contacts.empty:
                                        st.info(f"🚀 Found {len(valid_contacts)} parents. Starting blast...")
                                        p_bar = st.progress(0)
                                        
                                        for i, row in enumerate(valid_contacts.itertuples()):
                                            p_name = getattr(row, name_col)
                                            p_email = getattr(row, email_col)
                                            
                                            # Send using your SMTP logic
                                            send_email_notification(p_email, p_name, bulk_class)
                                            p_bar.progress((i + 1) / len(valid_contacts))
                                        
                                        st.success(f"✅ Successfully notified all {len(valid_contacts)} parents!")
                                    else:
                                        st.error("No valid email addresses found in the sheet.")
                                else:
                                    st.error(f"Missing Name/Email columns. Found: {list(df_data.columns)}")
                            else:
                                st.error(f"Sheet 'Data' not found in {f_path}")
                        except Exception as e:
                            st.error(f"Critical Error: {e}")
                else:
                    st.error(f"File {f_path} not found.")

    # --- 5. CONTENT MANAGER (Inside Staff Management Tab) ---
    with tab_content:
        st.markdown("### 📰 News & Protocol Control")
        
        # Live Preview for the Admin
        with st.expander("👁️ View Live Dashboard Preview", expanded=False):
            st.markdown(f"#### {st.session_state.news_content['title']}")
            if os.path.exists("news_event.jpg"):
                st.image("news_event.jpg", width=400)
            st.write(st.session_state.news_content['desc'])

        # News Update Form
        with st.form("news_update_form"):
            st.subheader("✍️ Update Dashboard News")
            new_title = st.text_input("Headline", value=st.session_state.news_content['title'])
            new_desc = st.text_area("Content", value=st.session_state.news_content['desc'])
            uploaded_news_img = st.file_uploader("Change Image", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("🚀 Publish & Save"):
                st.session_state.news_content.update({'title': new_title.upper(), 'desc': new_desc})
                st.session_state.portal_storage.update({'news_title': new_title.upper(), 'news_desc': new_desc})
                
                # Save to Master Excel
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                
                if uploaded_news_img:
                    with open("news_event.jpg", "wb") as f: f.write(uploaded_news_img.getbuffer())
                st.success("✅ News updated globally!")
                st.rerun()

        # Protocol Update Form
        with st.form("protocol_form"):
            st.subheader("📜 Edit School Protocols")
            n_cal = st.text_area("Calendar", st.session_state.protocols['calendar'])
            n_exam = st.text_area("Exams", st.session_state.protocols['exams'])
            
            if st.form_submit_button("💾 Save Protocols"):
                st.session_state.protocols.update({"calendar": n_cal, "exams": n_exam})
                st.session_state.portal_storage.update({"calendar": n_cal, "exams": n_exam})
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                st.success("✅ Protocols synced with Dashboard!")
                st.rerun()

       # --- SHUTDOWN: PERSISTENT DIGITAL NOTICE BOARD (MANAGEMENT ONLY) ---
        st.markdown("---")
        st.markdown("### 📂 Digital Notice Board Management")
        st.info("Files uploaded here are synced to the public Dashboard and GitHub.")
        
        with st.form("notice_board_form"):
            notice_name = st.text_input("Notice Title (e.g., '2026 Exam Timetable')")
            uploaded_pdf = st.file_uploader("Upload PDF Document", type=['pdf'])
            
            if st.form_submit_button("📌 Pin to Notice Board & Sync to GitHub"):
                if uploaded_pdf and notice_name:
                    clean_filename = f"notice_{notice_name.replace(' ', '_').lower()}.pdf"
                    file_bytes = uploaded_pdf.getvalue()
                    
                    # 1. LOCAL SAVE
                    if not os.path.exists("notices"): os.makedirs("notices")
                    local_path = os.path.join("notices", clean_filename)
                    with open(local_path, "wb") as f:
                        f.write(file_bytes)
                    
                    # 2. GITHUB SYNC (Robot Function)
                    with st.spinner("Pushing to GitHub..."):
                        status = upload_notice_to_github(file_bytes, clean_filename)
                    
                    # 3. UPDATE DATA
                    if 'notices' not in st.session_state: st.session_state.notices = []
                    st.session_state.notices.append({"title": notice_name, "path": local_path})
                    st.session_state.portal_storage['notices_data'] = str(st.session_state.notices)
                    pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                    
                    if status in [200, 201]:
                        st.success(f"✅ '{notice_name}' synced successfully!")
                    else:
                        st.warning(f"⚠️ Saved locally, but GitHub Sync Error: {status}")
                    st.rerun()

        # 2. DELETE FEATURE (Management UI)
        if 'notices' in st.session_state and st.session_state.notices:
            st.write("---")
            st.write("🗑️ **Manage Active Notices**")
            for i, notice in enumerate(st.session_state.notices):
                col_n, col_d = st.columns([3, 1])
                col_n.write(f"📄 {notice['title']}")
                if col_d.button("Delete", key=f"admin_del_{i}"):
                    if os.path.exists(notice['path']):
                        os.remove(notice['path'])
                    st.session_state.notices.pop(i)
                    st.session_state.portal_storage['notices_data'] = str(st.session_state.notices)
                    pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                    st.warning(f"Deleted: {notice['title']}")
                    st.rerun()
# --- DASHBOARD LOGIC (STUDENT) ---
elif page == "📊 Dashboard":
    import os
    import random
    import io  

    # 1. Assets
    founder_path, lab_path, news_path = "founder.jpg", "lab.jpg", "news_event.jpg"
    lab_img_base64 = get_local_img(lab_path) 

    quotes = [
        "\"The function of education is to teach one to think intensively and to think critically. Intelligence plus character - that is the goal of true education.\"",
        "\"Education is the passport to the future, for tomorrow belongs to those who prepare for it today.\"",
        "\"Your attitude, not your aptitude, will determine your altitude.\"",
        "\"Great leaders don't set out to be leaders... they set out to make a difference. It's never about the role-always about the goal.\"",
        "\"Knowledge is power, but character is respect.\""
    ]
    
    # 2. TOP SECTION
    st.markdown(f"""
        <div class="principal-quote">
            <small style="color:#fbbf24; text-transform:uppercase; letter-spacing:1px;"><b>Principal's Quote of the Day</b></small><br>
            <span style="font-size:1.3em; color:#f8fafc;">{random.choice(quotes)}</span>
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

    st.markdown("""<h1 style='text-align:center; color:#fbbf24; font-size:3em;'>RUBY SPRINGFIELD COLLEGE</h1>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='text-align:center; color:#f8fafc; font-style:italic; margin-top:-15px;'>Motto: A Citadel of Excellence</h3>""", unsafe_allow_html=True)
    st.markdown('<div class="school-bio">"Knowledge meets character in the heart of Maiduguri. We are building global leaders with integrity and academic brilliance."</div>', unsafe_allow_html=True)

    # 4. VISION & MISSION
    v_col, m_col = st.columns(2)
    with v_col:
        st.markdown(f"""<div class="statement-box"><h3 style="color:#fbbf24; text-align:center;">🔭 VISION STATEMENT</h3><p style="text-align:justify; line-height:1.6;">TO PROVIDE QUALITATIVE EDUCATION IN A SERENE AND SAFE LEARNING ENVIRONMENT, ENABLING US TO PRODUCE HIGHLY QUALIFIED AND POTENTIAL LEADERS OF TOMORROW.</p></div>""", unsafe_allow_html=True)
    with m_col:
        st.markdown(f"""<div class="statement-box"><h3 style="color:#fbbf24; text-align:center;">🎯 MISSION STATEMENT</h3><p style="text-align:justify; line-height:1.6;">TO BRIDGE THE GAP BETWEEN THE RICH AND THE POOR. TO DEMONSTRATE ACHIEVEMENTS ACROSS THE RANGE OF STUDENTS, SO THAT OUR GRADUATES ARE WELL NURTURED IN LOVE TO EXCEL AND FIT IN ANY WHERE.</p></div>""", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#fbbf24;'>💎 OUR CORE VALUES</h2>", unsafe_allow_html=True)
    cv_cols = st.columns(4)
    values = ["Hard work", "Integrity", "High moral standard", "Discipline", "Honesty", "Excellence", "Team spirit"]
    for idx, val in enumerate(values):
        cv_cols[idx % 4].markdown(f'<div class="core-value-card">{val.upper()}</div>', unsafe_allow_html=True)
    
    st.divider()

   # 5. METRICS SECTION (REDESIGNED)
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

    # 6. HERITAGE & FOUNDER
    col_hist, col_img = st.columns([2, 1])
    with col_hist:
        st.markdown('<div class="history-card"><h2 style="color:#fbbf24;">A Heritage of Leadership</h2><p>Founded in Maiduguri, RSC provides a university-preparatory environment.</p></div>', unsafe_allow_html=True)
    with col_img:
        if os.path.exists(founder_path):
            st.image(founder_path, use_column_width=True) 
        else:
            st.warning("founder.jpg missing.")

    # 7. PRACTICAL GALLERY
    st.markdown(f"""
        <div class="practical-gallery" style="background-image: url('data:image/jpeg;base64,{lab_img_base64}');">
            <div class="overlay-content">
                <h4>🧪 Advanced Chemical Research Lab</h4>
                <p>Precision and discovery in every experiment.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 8. NEWS FEED & PROTOCOLS
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("### 🔔 RSC News Feed")
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#fbbf24;'>{st.session_state.news_content['title']}</h4>", unsafe_allow_html=True)
            if os.path.exists(news_path):
                with open(news_path, "rb") as f:
                    st.image(io.BytesIO(f.read()), use_column_width=True)
            st.markdown(f"<div style='margin-top:10px;'>{st.session_state.news_content['desc']}</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("### 🛠️ Official Protocol")
        st.markdown("""<style>.protocol-box {background-color: #1E3A8A; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #fbbf24;}</style>""", unsafe_allow_html=True)

        if st.button("📅 School Calendar", use_container_width=True): 
            st.session_state.show_cal = not st.session_state.get('show_cal', False)
        if st.session_state.get('show_cal', False):
            cal_data = st.session_state.get('portal_storage', {}).get('calendar', 'Calendar update pending.')
            st.markdown(f'<div class="protocol-box"><b>🗓️ ACADEMIC CALENDAR:</b><br>{cal_data}</div>', unsafe_allow_html=True)

        if st.button("📜 Exam Guidelines", use_container_width=True): 
            st.session_state.show_exam = not st.session_state.get('show_exam', False)
        if st.session_state.get('show_exam', False):
            exam_data = st.session_state.get('portal_storage', {}).get('exams', 'Proper uniform and ID card required for entry.')
            st.markdown(f'<div class="protocol-box"><b style="color:#fbbf24;">EXAM PROTOCOL:</b><br>{exam_data}</div>', unsafe_allow_html=True)

        if st.button("📞 Contact Info", use_container_width=True): 
            st.session_state.show_contact = not st.session_state.get('show_contact', False)
        if st.session_state.get('show_contact', False):
            contact_data = st.session_state.get('portal_storage', {}).get('contact', 'School Office: Maiduguri, Borno State.')
            st.markdown(f'<div class="protocol-box"><b>📞 OFFICIAL CONTACT:</b><br>{contact_data}</div>', unsafe_allow_html=True)

# --- SHUTDOWN: PERSISTENT DIGITAL NOTICE BOARD (WITH GITHUB SYNC) ---
    st.markdown("---")
    st.markdown("<h3 style='color:#fbbf24;'>📂 School Notice Board</h3>", unsafe_allow_html=True)
    
    if os.path.exists("notices"):
        notice_files = [f for f in os.listdir("notices") if f.endswith('.pdf')]
        if notice_files:
            n_cols = st.columns(3)
            for idx, filename in enumerate(notice_files):
                with n_cols[idx % 3]:
                    with st.container(border=True):
                        clean_title = filename.replace("notice_", "").replace(".pdf", "").replace("_", " ").upper()
                        st.markdown(f"**📄 {clean_title}**")
                        file_path = os.path.join("notices", filename)
                        with open(file_path, "rb") as f:
                            st.download_button(label="📥 View PDF", data=f, file_name=filename, mime="application/pdf", key=f"pub_dl_{idx}", use_container_width=True)
        else:
            st.info("The notice board is currently empty.")
    
# 10. FOOTER
    st.markdown('<div class="footer-section"><p>© 2026 Ruby Springfield College • Developed by Adam Usman</p><div class="watermark-text">Powered by SumiLogics(NJA)</div></div>', unsafe_allow_html=True)







