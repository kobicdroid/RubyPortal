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

# --- NEW: HELPER FUNCTION TO FIX NAMEERROR ---
def get_local_img(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return None
    except Exception:
        return None

# --- STEP 1: PAGE CONFIG (MOBILE OPTIMIZED) ---
st.set_page_config(
    page_title="Ruby Springfield College | Official Portal",
    page_icon="🎓", 
    layout="centered", # Optimized for mobile apps
    initial_sidebar_state="collapsed" # Hide sidebar for WebToApp
)

# --- STEP 2: APP-STYLE CSS (HIDING STREAMLIT & ADDING NATIVE LOOK) ---
st.markdown("""
    <style>
    /* HIDE STREAMLIT BRANDING */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* MOBILE THEME COLORS */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #F8FAFC !important;
    }

    .stApp { background: #F8FAFC; }

    /* EXECUTIVE MOBILE HEADER */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 45px 20px;
        border-radius: 0px 0px 35px 35px;
        text-align: center;
        color: white;
        margin: -85px -20px 30px -20px;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.2);
    }

    .school-title { font-size: 2.2em; font-weight: 800; text-transform: uppercase; margin: 0; letter-spacing: 1px; }
    .school-motto { font-size: 0.9em; font-style: italic; opacity: 0.9; margin-top: 5px; }
    .loc-badge { margin-top:12px; font-size: 0.7em; background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; display: inline-block; }

    /* INPUT STYLES */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* CUSTOM MOBILE BUTTONS */
    div.stButton > button {
        background: #1E3A8A !important;
        color: white !important;
        border-radius: 15px !important;
        height: 55px !important;
        font-weight: 700 !important;
        width: 100% !important;
        border: none !important;
    }
    </style>

    <div class="app-header">
        <div class="school-title">RUBY SPRINGFIELD</div>
        <div class="school-motto">A Citadel of Excellence</div>
        <div class="loc-badge">📍 MAIDUGURI, BORNO STATE</div>
    </div>
""", unsafe_allow_html=True)

# --- STEP 3: LOGO WATERMARK ---
def add_logo_watermark(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background: linear-gradient(rgba(248, 250, 252, 0.95), rgba(248, 250, 252, 0.95)), 
                            url("data:image/jpeg;base64,{encoded_string}") !important;
                background-attachment: fixed !important;
                background-size: 300px !important; 
                background-position: center !important;
                background-repeat: no-repeat !important;
            }}
            </style>
            """, unsafe_allow_html=True)
    else:
        st.error(f"❌ DATABASE ERROR: File '{image_file}' not found.")

add_logo_watermark("logo.jpg")

# --- LOGIN & PERMANENCE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- SECRETS & GOOGLE ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO = st.secrets["REPO_PATH"]
except Exception:
    pass

verify_code = "lJuiVMz6tsO5tGGxk2wTWmFydMeB7gxsQyuUJger6cg"
st.markdown(f'<div style="display:none;">google-site-verification: {verify_code}</div>', unsafe_allow_html=True)

# --- STORAGE & NOTIFICATIONS ---
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
            return dict(zip(df['Key'].astype(str), df['Value'].astype(str)))
        except Exception:
            return defaults
    return defaults

if 'portal_storage' not in st.session_state:
    st.session_state.portal_storage = load_portal_data()

# --- PROFESSIONAL EMAIL FUNCTION ---
def send_email_notification(receiver_email, student_name, class_name, reg_number, access_key):
    sender_email = "sumilogics247@gmail.com"
    sender_password = "upsw jbon rhoy aiai" 
    portal_link = "https://rubyspringfield-college.streamlit.app/" 
    message = MIMEMultipart()
    message["From"] = f"Ruby Springfield College Admin <{sender_email}>"
    message["To"] = receiver_email
    message["Subject"] = f"OFFICIAL: Result Release - {student_name}"
    body = f"""
    <html><body>
        <div style="font-family: Arial, sans-serif; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
            <h2 style="color: #1E3A8A;">Ruby Springfield College</h2>
            <p>The academic report for <b>{student_name}</b> in <b>{class_name}</b> is ready.</p>
            <div style="background: #f4f4f4; padding: 15px; border-left: 5px solid #1E3A8A;">
                <p><b>Link:</b> {portal_link}<br><b>Adm No:</b> {reg_number}<br><b>Key:</b> {access_key}</p>
            </div>
            <p>Best Regards,<br>Management</p>
        </div>
    </body></html>"""
    message.attach(MIMEText(body, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(); server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit(); return True
    except Exception as e:
        st.error(f"❌ Mail Error: {e}"); return False

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
        pass 

def get_available_classes():
    files = glob.glob("Report *.xlsx")
    return sorted([f.replace("Report ", "").replace(".xlsx", "") for f in files]) if files else ["JSS 1A"]

def show_analytics(selected_class):
    file_path = f"Report {selected_class}.xlsx"
    if os.path.exists(file_path):
        data_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        
        sc_n = next((s for s in data_sheets.keys() if 'scoresheet' in s.lower()), None)
        if sc_n:
            df_sc = data_sheets[sc_n]
            # SHUTDOWN: Your master code two logic integrated here
            header_mask = df_sc.apply(lambda row: row.astype(str).str.contains('Total', case=False).any(), axis=1)
            header_idx = df_sc[header_mask].index[0] if any(header_mask) else 1
            
            r1 = df_sc.iloc[header_idx-1] # Subjects
            r2 = df_sc.iloc[header_idx]   # Headers
            
            subjects = []
            averages = []
            total_cols = [] 
            
            for i in range(len(r2)):
                if str(r2.iloc[i]).strip().lower() == "total":
                    total_cols.append(i)
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

            st.markdown(f"### 📊 Analytics: {selected_class}")
            
            data_rows = df_sc.iloc[header_idx+1:, :]
            at_risk_list = []
            
            for _, row in data_rows.iterrows():
                student_name = row.iloc[1]
                # Fail detection logic
                fail_count = sum(1 for c in total_cols if pd.to_numeric(row.iloc[c], errors='coerce') < 50)
                if fail_count >= 3:
                    at_risk_list.append({"Student": student_name, "Failing Subjects": fail_count})

            class_avg = sum(averages) / len(averages) if averages else 0
            
            # APP-STYLE METRICS
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Class Avg", f"{round(class_avg, 1)}%")
            m2.metric("Enrolled", len(data_rows))
            m3.metric("At-Risk", len(at_risk_list), delta_color="inverse")
            st.markdown('</div>', unsafe_allow_html=True)

            # PERFORMANCE CHART (MODERNIZED COLORS)
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            fig_bar = px.bar(
                x=subjects, y=averages, 
                labels={'x': 'Subjects', 'y': 'Avg Score'},
                title="Subject Performance Distribution",
                color=averages, 
                color_continuous_scale=['#DBEAFE', '#1E3A8A'], # Light Blue to Ruby Blue
                text_auto=True
            )
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # TOP STUDENTS SECTION
            st.markdown('<div class="app-card">', unsafe_allow_html=True)
            st.markdown("🏆 **Honor Roll (Top 3)**")
            grand_total_idx = total_cols[-1] if total_cols else 1
            df_leader = df_sc.iloc[header_idx+1:, [0, 1, grand_total_idx]].copy()
            df_leader.columns = ['ID', 'Name', 'Total']
            df_leader['Total'] = pd.to_numeric(df_leader['Total'], errors='coerce')
            top_3 = df_leader.nlargest(3, 'Total')
            for i, row in top_3.iterrows():
                st.success(f"**{row['Name']}** — Score: {row['Total']}")
            st.markdown('</div>', unsafe_allow_html=True)

            if at_risk_list:
                with st.expander("⚠️ View Academic Interventions Needed"):
                    st.table(pd.DataFrame(at_risk_list))

            log_activity("Admin", "Analytics", f"Analyzed {selected_class}")
        else:
            st.warning("Data format mismatch: 'Scoresheet' tab missing.")
    else:
        st.error(f"Missing Data: {selected_class} file not found.")

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
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# --- STEP 1: INITIALIZE DYNAMIC CONTENT (EXCEL PERSISTENCE) ---
# Shutdown, this pulls from the 'portal_storage' we loaded in Part 1.

if 'news_content' not in st.session_state:
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

# --- STEP 2: NAVIGATION & TOGGLE INITIALIZATION ---
for key in ['show_students', 'show_subjects', 'show_cal', 'show_exam', 'show_contact']:
    if key not in st.session_state:
        st.session_state[key] = False

# --- STEP 3: NATIVE-APP CSS (WHITE THEME / BLUE ACCENTS) ---
st.markdown("""
    <style>
    /* GLOBAL MOBILE OVERRIDES */
    .stApp { background-color: #ffffff !important; color: #1E293B !important; }
    
    /* CUSTOM CARD CONTAINERS */
    .app-card-white {
        background: #ffffff !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }

    /* THE PRINCIPAL'S QUOTE BOX */
    .quote-box {
        background: #EFF6FF !important;
        border-left: 6px solid #1E3A8A !important;
        padding: 20px;
        margin: 15px 0;
        border-radius: 0 15px 15px 0;
        font-family: 'Georgia', serif;
        color: #1E3A8A !important;
        font-style: italic;
    }

    /* NEWS TICKER (BLUE BAR) */
    .ticker-wrap {
        width: 100%; overflow: hidden; height: 45px; 
        background-color: #1E3A8A !important; 
        display: flex; align-items: center; margin: 10px 0 25px 0;
        border-radius: 10px;
    }
    .ticker {
        display: inline-block; white-space: nowrap; padding-right: 100%;
        animation: ticker 40s linear infinite; font-weight: bold; color: #ffffff !important;
    }
    @keyframes ticker {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    /* MOBILE VALUE BUTTONS */
    .value-pill {
        background: #F1F5F9;
        border: 1px solid #1E3A8A;
        padding: 12px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    .value-pill:hover { background: #1E3A8A; color: #ffffff; }

    /* FOOTER DESIGN */
    .app-footer {
        background: #0F172A;
        padding: 40px 20px;
        border-radius: 35px 35px 0 0;
        text-align: center;
        color: #94A3B8;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# --- STEP 4: SCHOOL LOGO SECTION ---
logo_b64 = get_local_img("logo.jpg")
if logo_b64:
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="data:image/jpeg;base64,{logo_b64}" 
                 style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #1E3A8A; padding: 3px; background: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
        </div>
    """, unsafe_allow_html=True)

# --- STEP 5: THE TICKER BAR ---
ticker_text = f"📢 LATEST NEWS: {st.session_state.news_content['title']} — PORTAL OPEN FOR 2026 TERM RESULTS — CONTACT ADMISSIONS FOR ENQUIRIES"
st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker">{ticker_text}</div>
    </div>
""", unsafe_allow_html=True)

# --- ADMIN TABS SETUP ---
tabs = st.tabs([
    "📈 Result Analysis", 
    "📉 Class Insights", 
    "📦 Bulk & Notifications", 
    "📢 Content Manager"
])

# --- 3. ANALYTICS TAB ---
with tabs[0]: 
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
                    
                    # MASTER CODE TWO LOGIC
                    header_row = df_sc.iloc[header_idx] 
                    subject_row = df_sc.iloc[header_idx - 1]
                    
                    subject_stats = []
                    total_cols = []
                    
                    for i, col_val in enumerate(header_row): 
                        if str(col_val).strip().lower() == 'total':
                            total_cols.append(i) 
                            sub_name = str(subject_row.iloc[i]).strip()
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
                        st.subheader("📋 Management Summary")
                        data_rows = df_sc.iloc[header_idx+1:, :]
                        at_risk_list = []
                        for _, row in data_rows.iterrows():
                            s_name = row.iloc[1]
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

                        fig_bar = px.bar(df_stats, x='Subject', y='Average Score', 
                                       title=f"Class Subject Performance: {selected_analysis}",
                                       color='Average Score', color_continuous_scale='Viridis', text_auto=True)
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.warning("No performance data found.")
            else:
                st.error("Class file not found.")

# --- 4. BULK GENERATOR & NOTIFICATIONS ---
with tabs[2]:
    st.subheader("📦 Bulk Result Generator & Parent Alerts")
    
    bulk_class = st.selectbox("Select Class for Mass Action", get_available_classes(), key="bulk_target")
    col_pdf, col_notif = st.columns(2)
    
    with col_pdf:
        st.markdown("#### 📄 Document Export")
        if st.button("🚀 GENERATE ALL PDFs"):
            st.info(f"Generating reports for {bulk_class}...")

    with col_notif:
        st.markdown("#### 🔔 Parent Notifications")
        test_email = st.text_input("Test Email Address", placeholder="yourname@gmail.com")
        
        if st.button("🧪 Send Test Email"):
            success = send_email_notification(test_email, "Test Student", bulk_class, "RSC-TEST-001", "1234")
            if success: 
                st.success("✅ Test Email Sent!")
            else: 
                st.error("❌ Email Failed.")

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
                                            time.sleep(0.5) 
                                except Exception:
                                    pass
                                p_bar.progress((i + 1) / len(df_bulk))
                            st.success(f"🏁 Blast complete! {success_count} emails sent.")
                        else:
                            st.error("❌ Sheet 'Data' not found.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.error(f"❌ File '{f_path}' not found.")

# --- 5. CONTENT MANAGER ---
with tabs[3]:
    st.markdown("### 📰 News & Protocol Control")
    
    with st.expander("👁️ View Live Dashboard Preview", expanded=False):
        st.markdown(f"#### {st.session_state.news_content['title']}")
        if os.path.exists("news_event.jpg"):
            st.image("news_event.jpg", width=400)
        st.write(st.session_state.news_content['desc'])

    with st.form("news_update_form"):
        st.subheader("✍️ Update Dashboard News")
        new_title = st.text_input("Headline", value=st.session_state.news_content['title'])
        new_desc = st.text_area("Content", value=st.session_state.news_content['desc'])
        uploaded_news_img = st.file_uploader("Change Image", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("🚀 Publish & Save"):
            st.session_state.news_content.update({'title': new_title.upper(), 'desc': new_desc})
            st.session_state.portal_storage.update({'news_title': new_title.upper(), 'news_desc': new_desc})
            pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
            if uploaded_news_img:
                with open("news_event.jpg", "wb") as f:
                    f.write(uploaded_news_img.getbuffer())
            st.success("✅ News updated!")
            st.rerun()

    with st.form("protocol_form"):
        st.subheader("📜 Edit School Protocols")
        n_cal = st.text_area("Calendar", st.session_state.protocols['calendar'])
        n_exam = st.text_area("Exams", st.session_state.protocols['exams'])
        if st.form_submit_button("💾 Save Protocols"):
            st.session_state.protocols.update({"calendar": n_cal, "exams": n_exam})
            st.session_state.portal_storage.update({"calendar": n_cal, "exams": n_exam})
            pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
            st.success("✅ Protocols synced!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📂 Digital Notice Board Management")
    with st.form("notice_board_form"):
        notice_name = st.text_input("Notice Title")
        uploaded_pdf = st.file_uploader("Upload PDF Document", type=['pdf'])
        if st.form_submit_button("📌 Pin to Notice Board"):
            if uploaded_pdf and notice_name:
                clean_filename = f"notice_{notice_name.replace(' ', '_').lower()}.pdf"
                file_bytes = uploaded_pdf.getvalue()
                if not os.path.exists("notices"): os.makedirs("notices")
                local_path = os.path.join("notices", clean_filename)
                with open(local_path, "wb") as f: f.write(file_bytes)
                # upload_notice_to_github(file_bytes, clean_filename) # Ensure this is defined elsewhere
                if 'notices' not in st.session_state: st.session_state.notices = []
                st.session_state.notices.append({"title": notice_name, "path": local_path})
                st.session_state.portal_storage['notices_data'] = str(st.session_state.notices)
                pd.DataFrame(list(st.session_state.portal_storage.items()), columns=['Key', 'Value']).to_excel("portal_data.xlsx", index=False)
                st.success(f"📌 '{notice_name}' pinned successfully!")
                st.rerun()
# A. DASHBOARD
if page == "📊 Dashboard":
    # 1. Assets
    founder_path, lab_path, news_path = "founder.jpg", "lab.jpg", "news_event.jpg"
    lab_img_base64 = get_local_img(lab_path) 

    quotes = [
        "\"The function of education is to teach one to think intensively and to think critically.\"",
        "\"Education is the passport to the future, for tomorrow belongs to those who prepare for it today.\"",
        "\"Your attitude, not your aptitude, will determine your altitude.\"",
        "\"Knowledge is power, but character is respect.\""
    ]
    
    # 2. TOP SECTION
    st.markdown(f'<div class="principal-quote"><small style="color:#2563eb;"><b>PRINCIPAL\'S QUOTE</b></small><br><span style="font-size:1.2em;">{random.choice(quotes)}</span></div>', unsafe_allow_html=True)

    # 3. TICKER
    announcement = st.session_state.news_content.get('title', 'WELCOME TO RUBY SPRINGFIELD')
    st.markdown(f'<div class="ticker-wrap">📢 <b>LATEST NEWS:</b> {announcement}</div>', unsafe_allow_html=True)

    # 4. VISION & MISSION
    v_col, m_col = st.columns(2)
    with v_col:
        st.markdown('<div class="statement-box"><h3 style="color:#2563eb; text-align:center;">🔭 VISION</h3><p style="text-align:justify;">TO PRODUCE HIGHLY QUALIFIED AND POTENTIAL LEADERS OF TOMORROW.</p></div>', unsafe_allow_html=True)
    with m_col:
        st.markdown('<div class="statement-box"><h3 style="color:#2563eb; text-align:center;">🎯 MISSION</h3><p style="text-align:justify;">TO BRIDGE THE GAP BETWEEN THE RICH AND THE POOR.</p></div>', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; color:#1e3a8a; margin-top:30px;'>💎 OUR CORE VALUES</h2>", unsafe_allow_html=True)
    cv_cols = st.columns(4)
    values = ["Hard work", "Integrity", "Discipline", "Excellence", "Honesty", "Team spirit", "Moral Standard", "Focus"]
    for idx, val in enumerate(values):
        cv_cols[idx % 4].markdown(f'<div class="core-value-card">{val.upper()}</div>', unsafe_allow_html=True)
    
    st.divider()

    # 5. METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown('<div class="metric-card"><div class="metric-label">Students</div><div class="metric-value">2.4k+</div></div>', unsafe_allow_html=True)
    with m2: st.markdown('<div class="metric-card"><div class="metric-label">Uptime</div><div class="metric-value">100%</div></div>', unsafe_allow_html=True)
    with m3: st.markdown('<div class="metric-card"><div class="metric-label">Subjects</div><div class="metric-value">18</div></div>', unsafe_allow_html=True)
    with m4: st.markdown('<div class="metric-card"><div class="metric-label">Performance</div><div class="metric-value">92%</div></div>', unsafe_allow_html=True)

    # 6. HERITAGE
    col_hist, col_img = st.columns([2, 1])
    with col_hist:
        st.markdown('<div class="statement-box"><h2>A Heritage of Leadership</h2><p>Ruby Springfield started in 1998... Our watchword is SUPREME EXCELLENCE.</p></div>', unsafe_allow_html=True)
    with col_img:
        if os.path.exists(founder_path): st.image(founder_path, use_container_width=True, caption="The Founder, RSC")
        else: st.warning("Founder Image Missing")

    # 7. NEWS FEED & PROTOCOL
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("### 🔔 RSC News Feed")
        with st.container(border=True):
            st.markdown(f"#### {st.session_state.news_content['title']}")
            if os.path.exists(news_path): st.image(news_path, use_container_width=True)
            st.write(st.session_state.news_content['desc'])
    
    with col_r:
        st.markdown("### 🛠️ Official Protocol")
        if st.button("📅 School Calendar", use_container_width=True): st.info("Calendar: Term starts Sept 15th.")
        if st.button("📜 Exam Guidelines", use_container_width=True): st.warning("ID cards are compulsory.")
        if st.button("📞 Contact Info", use_container_width=True): st.success("Office: Maiduguri, Borno State.")

    # 8. FOOTER
    st.markdown(f'''<div class="footer-section"><p>© {datetime.now().year} Ruby Springfield College • Developed by Adam Usman</p><div class="watermark-text">Powered by SumiLogics(NJA)</div></div>''', unsafe_allow_html=True)