# Deploy Version: 2026-02-03-23-58
import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv
from src.utils.file_handler import extract_text_from_file
from src.logic.nlp_processor import extract_entities, split_into_clauses, detect_language
from src.logic.risk_engine import analyze_risk_with_llm, get_overall_assessment
from src.utils.pdf_generator import generate_pdf_report
from src.utils.db_handler import save_contract_analysis, get_recent_contracts
import plotly.graph_objects as go

load_dotenv()

# Advanced UI Components
try:
    from streamlit_option_menu import option_menu
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.metric_cards import style_metric_cards
    ADVANCED_UI = True
except ImportError:
    ADVANCED_UI = False



# --- Config ---
st.set_page_config(
    page_title="GenAI Legal SME Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background-color: #f3f0ff;
        color: #1e1e2e;
    }
    
    /* Fix text visibility in chat */
    [data-testid="stChatMessage"] p {
        color: #1e1e2e !important;
    }
    
    /* Ensure no text spills from the icons */
    .st-emotion-cache-12m6p4t, .st-emotion-cache-1p6f2r1 {
        font-size: 0 !important;
    }
    .main-header {
        font-family: 'Outfit', sans-serif;
        color: #6C5CE7;
        font-weight: 700;
    }
    
    /* Enforce Dark Text Globally */
    p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: #1e1e2e;
    }
    
    /* Text Arrays & Inputs - Fix white text on white bg */
    .stTextArea textarea, .stTextInput input {
        color: #2d3436 !important;
        background-color: #ffffff !important;
    }
    
    /* Expander Headers */
    .streamlit-expanderHeader {
        color: #1e1e2e !important;
        background-color: #ffffff;
    }
    
    /* Buttons - Violet Gradient */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #6C5CE7 0%, #a29bfe 100%);
        color: white !important;
        border: none;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.2);
        transition: all 0.3s ease;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(108, 92, 231, 0.4);
        color: white !important;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #6C5CE7 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #636e72 !important;
    }
    
    /* Risk Highlighters */
    .risk-high { color: #d63031 !important; font-weight: bold; }
    .risk-medium { color: #fdcb6e !important; font-weight: bold; }
    .risk-low { color: #00b894 !important; font-weight: bold; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dfe6e9;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #6C5CE7 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def draw_risk_gauge(score):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        number = {'font': {'color': '#000000', 'size': 48}, 'suffix': "%"},
        title = {'text': "Contract Health Score", 'font': {'color': '#6C5CE7', 'size': 20, 'family': 'Inter'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#6C5CE7"},
            'bar': {'color': "#6C5CE7"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#dfe6e9",
            'steps': [
                {'range': [0, 50], 'color': '#fab1a0'},  # Red-ish
                {'range': [50, 80], 'color': '#ffeaa7'}, # Yellow-ish
                {'range': [80, 100], 'color': '#55efc4'} # Teal-ish
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig

# --- Main App ---
def main():
    # --- PREMIUM UI SYSTEM (Maximum Streamlit Potential) ---
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* === GLOBAL RESET === */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #f8f9fc 100%);
        }
        
        /* === ANIMATIONS === */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        /* === HEADER === */
        .dashboard-header {
            background: white;
            padding: 1.5rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            border-bottom: 1px solid #e8ecef;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            animation: fadeInUp 0.5s ease-out;
        }
        
        .header-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #000000;
            letter-spacing: -0.02em;
        }
        
        .header-subtitle {
            color: #000000;
            font-weight: 500;
            font-size: 0.95rem;
            margin-top: 0.25rem;
        }

        
        /* === CARDS === */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            background: white;
            border-radius: 16px !important;
            padding: 1.75rem !important;
            border: 1px solid #e8ecef !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            animation: fadeInUp 0.6s ease-out;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: #6C5CE7 !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 40px rgba(108, 92, 231, 0.15) !important;
        }
        
        /* === METRICS === */
        div[data-testid="stMetricLabel"] {
            color: #000000 !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        div[data-testid="stMetricValue"] {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
        }
        
        div[data-testid="stMetricDelta"] {
            font-size: 0.85rem !important;
        }
        
        /* === BUTTONS === */
        button[kind="primary"],
        .stDownloadButton > button {
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        button[kind="primary"]:hover,
        .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4) !important;
        }
        
        /* === FILE UPLOADER BUTTON (Browse files) === */
        section[data-testid="stFileUploader"] button,
        section[data-testid="stFileUploader"] button[kind="secondary"],
        div[data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, #a29bfe 0%, #d4c5ff 100%) !important;
            color: #000000 !important;
            border: 2px solid #6C5CE7 !important;
            border-radius: 10px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            box-shadow: 0 3px 12px rgba(108, 92, 231, 0.25) !important;
            transition: all 0.3s ease !important;
        }
        
        section[data-testid="stFileUploader"] button:hover,
        div[data-testid="stFileUploader"] button:hover {
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%) !important;
            color: white !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35) !important;
        }
        
        /* Fix white text in file uploader - HIGH SPECIFICITY */
        section[data-testid="stFileUploader"] label,
        section[data-testid="stFileUploader"] span,
        section[data-testid="stFileUploader"] p,
        section[data-testid="stFileUploader"] div,
        section[data-testid="stFileUploader"] small,
        .stFileUploaderFileName {
            color: #000000 !important;
        }
        
        /* Force black color on the instructions text specifically */
        [data-testid="stFileUploaderDropzoneInstructions"] * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* Standard Captions and Write text */
        div[data-testid="stCaptionContainer"], 
        .stMarkdown div p,
        .stMarkdown div span,
        .stAlert div p {
            color: #000000 !important;
        }
        
        /* Success/Info/Warning box text specifically */
        div[data-testid="stNotification"] p {
            color: #000000 !important;
        }

        
        /* === HIDE TOP TOOLBAR === */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            visibility: hidden !important;
        }
        
        /* Remove top padding caused by hidden header */
        .main .block-container {
            padding-top: 2rem !important;
        }
        
        
        
        /* === FILE UPLOADER === */
        section[data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(135deg, #fcfcff 0%, #f8f9fc 100%) !important;
            border: 2px dashed #a29bfe !important;
            border-radius: 16px !important;
            padding: 3rem 2rem !important;
            transition: all 0.3s ease !important;
        }
        
        /* Filename visibility specifically */
        div[data-testid="stFileUploaderFileName"] {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        .stFileUploaderFileName {
            color: #000000 !important;
        }
        
        section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #6C5CE7 !important;
            background: linear-gradient(135deg, #ffffff 0%, #fcfcff 100%) !important;
            box-shadow: 0 8px 30px rgba(108, 92, 231, 0.1) !important;
        }
        
        /* === SIDEBAR === */
        section[data-testid="stSidebar"] {
            background: white !important;
            border-right: 1px solid #e8ecef !important;
        }
        
        .sidebar-logo-container {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 1.5rem 0;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid #f1f3f5;
        }
        
        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
            border-radius: 12px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 20px;
            box-shadow: 0 4px 12px rgba(108, 92, 231, 0.25);
        }
        
        .logo-text {
            font-size: 1.25rem;
            font-weight: 700;
            color: #000000;
            letter-spacing: -0.01em;
        }
        
        
        /* === NAVIGATION PILLS (Health Engine Style) === */
        div[data-baseweb="radio"] > div {
            gap: 0px !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        div[data-baseweb="radio"] label {
            background-color: transparent !important;
            border: none !important;
            padding: 14px 18px !important;
            border-radius: 12px !important;
            cursor: pointer !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            margin-bottom: 8px !important;
            color: #000000 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            text-align: left !important;
        }
        
        div[data-baseweb="radio"] label[data-checked="true"] {
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 16px rgba(108, 92, 231, 0.3) !important;
            transform: translateX(2px) !important;
        }
        
        div[data-baseweb="radio"] label:hover {
            background-color: #f1f5f9 !important;
            color: #6C5CE7 !important;
            transform: translateX(2px) !important;
        }
        
        div[data-baseweb="radio"] label[data-checked="true"]:hover {
            background: linear-gradient(135deg, #5b4cc4 0%, #9189f5 100%) !important;
            color: white !important;
            box-shadow: 0 6px 20px rgba(108, 92, 231, 0.35) !important;
        }
        
        /* Hide radio circles */
        div[data-baseweb="radio"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        
        /* Style the text container to align with icon */
        div[data-baseweb="radio"] label > div {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }
        
        
        /* === EXPANDERS === */
        .streamlit-expanderHeader {
            background-color: #f8f9fc !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            color: #1a202c !important;
        }
        
        /* === TEXT AREAS === */
        textarea {
            border-radius: 12px !important;
            border-color: #e8ecef !important;
        }
        
        /* === PROGRESS & SPINNERS === */
        .stProgress > div > div {
            background: linear-gradient(90deg, #6C5CE7 0%, #a29bfe 100%) !important;
        }
        
        /* === TOOLTIPS & INFO === */
        .stAlert {
            border-radius: 12px !important;
            border-left: 4px solid #6C5CE7 !important;
        }
        
        /* === HEADINGS === */
        h1, h2, h3, h4, h5, h6 {
            color: #1a202c !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        
        /* === LOADING ANIMATION === */
        .stSpinner > div {
            border-color: #6C5CE7 transparent transparent transparent !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

    # --- Session State Init ---
    if 'page' not in st.session_state:
        st.session_state.page = "Dashboard"
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": "You are a helpful legal assistant."}]

    # --- Top Navigation Bar (Custom HTML) ---
    st.markdown(f"""
    <div class="dashboard-header">
        <div>
            <div class="header-title">Dashboard Overview</div>
            <div class="header-subtitle"><span style='font-size:1.2rem'>🟣</span> Legal Co-Pilot • {st.session_state.get('last_uploaded', 'New Session')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    # --- Sidebar Content ---
    with st.sidebar:
        # Custom Logo Header
        st.markdown("""
        <div class="sidebar-logo-container">
            <div class="logo-icon">LC</div>
            <div class="logo-text">Legal Co-Pilot</div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Status Indicator
        if 'api_key' not in st.session_state:
            st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")
            if st.session_state.api_key:
                import google.generativeai as genai
                genai.configure(api_key=st.session_state.api_key)

        if not st.session_state.api_key:
            st.sidebar.error("🔴 AI Backend: Offline")
        else:
            st.sidebar.success("🟢 AI Backend: Connected")
        
        # Add spacing
        st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)

        
        # Navigation
        # Using better icons with proper spacing
        nav_options = ["Dashboard", "Clause Explorer", "Original Text"]
        nav_icons = ["📊", "🔍", "📜"]
        
        # Create display with proper spacing between icon and text
        nav_display = [f"{icon}   {name}" for icon, name in zip(nav_icons, nav_options)]
        
        selected_nav = st.radio(
            "Navigation", 
            nav_display, 
            label_visibility="collapsed",
            key="sidebar_nav"
        )
        
        # Map back to internal page name
        if "Dashboard" in selected_nav: st.session_state.page = "Dashboard"
        elif "Clause" in selected_nav: st.session_state.page = "Clause Explorer"
        elif "Original" in selected_nav: st.session_state.page = "Original Text"
        
        # Divider with spacing
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        # Recent Scans Section
        st.markdown("**RECENT SCANS**")
        st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
        history = get_recent_contracts(limit=3)
        if history:
            for h in history:
                # Truncate filename
                fname = h.get('filename')
                if len(fname) > 20: fname = fname[:17] + "..."
                st.markdown(f"<div style='color: #000000; font-size: 0.9rem; margin-bottom: 0.5rem;'>📄 {fname}</div>", unsafe_allow_html=True)
        else:
            st.caption("No history yet.")

    # --- Main Content Grid ---
    if st.session_state.page == "Dashboard":
        
        # Page Title Banner (like the screenshot)
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #e0d7ff 0%, #f0ebff 100%);
            padding: 1.25rem 1.75rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 4px solid #6C5CE7;
        '>
            <div style='
                font-size: 1.1rem;
                font-weight: 600;
                color: #000000;
            '>
                👉 <strong>Upload a contract</strong> to unlock AI-powered risk analysis and insights.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
        # Row 1: The "Hero" Cards - Upload & Status
        col_upload, col_stats = st.columns([1.5, 2.5], gap="large")
        
        with col_upload:
            with st.container(border=True):
                st.markdown("##### 📤 Upload Document")
                st.caption("Supported: PDF, DOCX, TXT")
                st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                
                # The Uploader
                uploaded_file = st.file_uploader("Drop contract here", type=["pdf", "docx", "txt"], label_visibility="collapsed")
                
                if uploaded_file:
                    # Logic to process
                    if 'last_uploaded' not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
                        st.session_state.processing = True
                        # ... (Processing Logic below)

        with col_stats:
            # If nothing loaded, show "Placeholder" cards like the screenshot
            if not st.session_state.get('analysis_done'):
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    with st.container(border=True):
                        st.markdown("##### 🔒 Bank-Level Security")
                        st.caption("Your data is encrypted end-to-end.")
                        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                        st.image("https://cdn-icons-png.flaticon.com/512/2345/2345337.png", width=50)
                with c2:
                    with st.container(border=True):
                        st.markdown("##### 🤖 AI-Powered Analysis")
                        st.caption("Instant clause risk detection.")
                        st.markdown("<div style='margin: 0.5rem 0;'></div>", unsafe_allow_html=True)
                        st.image("https://cdn-icons-png.flaticon.com/512/1680/1680012.png", width=50)
                
                st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                with st.container(border=True):
                     st.info("👈 **Upload a contract** to unlock AI-powered risk analysis and insights.")
                     
                     
            else:
                # SHOW REAL STATS when loaded
                s1, s2, s3 = st.columns(3)
                with s1:
                    with st.container(border=True):
                        st.metric("Risk Score", st.session_state['assessment']['overall_score'], delta="AI Calculated")
                with s2:
                     with st.container(border=True):
                         st.metric("Clauses Scanned", len(st.session_state['analyzed_clauses']))
                with s3:
                     with st.container(border=True):
                         risks = sum(1 for c in st.session_state['analyzed_clauses'] if c['analysis']['red_flag'])
                         st.metric("Critical Flags", risks, delta="Action Needed", delta_color="inverse")
                         
        # Row 2: Analysis Detail (Visible if analysis is done)
        if st.session_state.get('analysis_done'):
             
             st.markdown("### 📊 Analysis Report")
             
             with st.container(border=True):
                 c_chart, c_text = st.columns([1, 2])
                 
                 with c_chart:
                     score = st.session_state['assessment']['overall_score']
                     st.plotly_chart(draw_risk_gauge(score), use_container_width=True)
                     
                     # Download Report Button styled as a big action
                     pdf_file = generate_pdf_report(st.session_state.get('last_uploaded', 'Contract'), score, st.session_state['assessment']['summary'], st.session_state['analyzed_clauses'])
                     st.download_button(
                         "📄 Download Summary Report", 
                         data=pdf_file, 
                         file_name="Risk_Report.pdf", 
                         mime="application/pdf", 
                         use_container_width=True, 
                         type="primary"
                    )

                 with c_text:
                     st.subheader("Advisor Summary")
                     st.success(st.session_state['assessment']['summary'])
                     st.divider()
                     st.markdown("**Critical Red Flags:**")
                     
                     risks = [c for c in st.session_state['analyzed_clauses'] if c['analysis']['red_flag']]
                     if risks:
                         for r in risks[:3]: # Show top 3
                             st.error(f"**{r['analysis']['explanation']}**")
                     else:
                         st.success("No major red flags detected.")

        # Processing Logic (High-Speed Parallel execution)
        if uploaded_file and ('last_uploaded' not in st.session_state or st.session_state.last_uploaded != uploaded_file.name):
            from concurrent.futures import ThreadPoolExecutor
            
            with st.status("🔮 Parallel AI Scanning...", expanded=True) as status:
                st.write("📂 Extracting document text...")
                raw_text = extract_text_from_file(uploaded_file)
                st.session_state['raw_text'] = raw_text
                
                st.write("🌐 Detecting language and entities...")
                lang = detect_language(raw_text)
                st.session_state['language'] = lang
                entities = extract_entities(raw_text)
                st.session_state['entities'] = entities
                
                st.write("📊 Analyzing clauses in parallel...")
                clauses = split_into_clauses(raw_text)[:12] # Core clauses
                
                # Execute in parallel to save time
                with ThreadPoolExecutor(max_workers=6) as executor:
                    results = list(executor.map(lambda c: {"text": c, "analysis": analyze_risk_with_llm(c, lang=lang)}, clauses))
                
                st.session_state['analyzed_clauses'] = results
                
                st.write("📝 Finalizing overall assessment...")
                assessment = get_overall_assessment(raw_text, lang=lang)
                st.session_state['assessment'] = assessment
                
                save_contract_analysis(uploaded_file.name, raw_text, entities, results, assessment)
                st.session_state['analysis_done'] = True
                st.session_state['last_uploaded'] = uploaded_file.name
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                st.rerun()


    # 2. Clause Explorer Tab
    elif st.session_state.page == "Clause Explorer":
        # Page Title Banner
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #e0d7ff 0%, #f0ebff 100%);
            padding: 1.25rem 1.75rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 4px solid #6C5CE7;
        '>
            <div style='
                font-size: 1.1rem;
                font-weight: 600;
                color: #000000;
            '>
                🔍 <strong>Clause Explorer</strong> - Deep dive into each clause with AI explanations
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Explore individual clauses with 'Explain Like I'm 5' simplification.")
        
        if st.session_state.get('analysis_done'):
            for idx, item in enumerate(st.session_state['analyzed_clauses']):
                with st.container():
                     # Card-like styling using columns
                     c1, c2 = st.columns(2)
                     with c1:
                         st.markdown("**📜 Legal Text**")
                         st.info(item['text'])
                     with c2:
                         st.markdown("**🤖 AI Explanation**")
                         risk = item['analysis']['risk_score']
                         badges = f":red[**High Risk ({risk}/10)**]" if risk > 7 else f":green[**Safe ({risk}/10)**]"
                         st.markdown(f"{badges} - {item['analysis']['explanation']}")
                         if item['analysis']['suggestion']:
                             st.warning(f"**Tip:** {item['analysis']['suggestion']}")
                st.divider()
        else:
            st.warning("Please upload a contract in the Dashboard first.")

    # 3. Original Text Tab
    elif st.session_state.page == "Original Text":
        # Page Title Banner
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #e0d7ff 0%, #f0ebff 100%);
            padding: 1.25rem 1.75rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            border-left: 4px solid #6C5CE7;
        '>
            <div style='
                font-size: 1.1rem;
                font-weight: 600;
                color: #000000;
            '>
                📜 <strong>Original Document Text</strong> - View the raw contract content
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('raw_text'):
             st.text_area("Raw Content", st.session_state['raw_text'], height=600)
        else:
            st.warning("No file uploaded.")

    # --- Floating AI Assistant (High-Performance Dialog) ---
    @st.dialog("🤖 Legal Assistant")
    def ai_assistant_dialog_window():
        st.markdown("""
            <style>
                /* Standard text colors */
                [data-testid="stDialog"] [data-testid="stMarkdownContainer"] p,
                [data-testid="stDialog"] [data-testid="stMarkdownContainer"] li,
                [data-testid="stChatMessage"] p {
                    color: #1e1e2e !important;
                }
                /* Hide the 'face' and 'smart_toy' labels */
                span[data-testid="stChatMessageAvatarCustomIcon"],
                span[data-testid="stChatMessageAvatarUserIcon"],
                span[data-testid="stChatMessageAvatarAssistantIcon"],
                span[data-testid="stChatMessageAvatarAssistantIcon"] + div,
                span[data-testid="stChatMessageAvatarUserIcon"] + div {
                    display: none !important;
                    font-size: 0 !important;
                }
                /* Hide any markdown paragraph that only contains these strings */
                div[data-testid="stMarkdownContainer"] p {
                    font-size: 1rem;
                }
                
                /* Style the chat input area */
                [data-testid="stChatInput"] textarea {
                    color: #1e1e2e !important;
                }
                .stCaption { color: #636e72 !important; }
                /* Force Alert/Info text to dark */
                .stAlert p { color: #1e1e2e !important; }
            </style>
        """, unsafe_allow_html=True)
        
        st.caption("Ask questions about your scanned contract.")
        
        # Chat History Container (Vertical Rectangle feel)
        chat_box = st.container(height=450)
        with chat_box:
            if not st.session_state.chat_history:
                st.info("👋 Hello! I'm your Legal Co-Pilot. Ask me anything about the document you uploaded.")
            for msg in st.session_state.chat_history:
                if msg["role"] != "system":
                    avatar = "👤" if msg["role"] == "user" else "🤖"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.write(msg["content"])
        
        # Chat Input
        if prompt := st.chat_input("Message the Assistant...", key="dialog_chat_v4"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            try:
                import google.generativeai as genai
                genai.configure(api_key=st.session_state.get('api_key', ''))
                
                # Use cached model if available to save time
                if 'working_model' not in st.session_state:
                    st.session_state.working_model = None
                
                model_found = False
                test_models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-pro']
                
                # Reorder list to try working model first
                if st.session_state.working_model:
                    test_models.insert(0, st.session_state.working_model)

                for mname in test_models:
                    try:
                        name = mname if mname.startswith('models/') else f"models/{mname}"
                        m = genai.GenerativeModel(name)
                        ctx = st.session_state.get('raw_text', '')[:12000]
                        
                        # Enhanced Solution-Oriented Prompt with Language Support
                        detected_lang = st.session_state.get('language', 'en')
                        lang_instr = "IMPORTANT: Provide all answers and solutions in HINDI." if detected_lang == "hi" else "Provide all answers in English."
                        
                        system_instr = f"""
                        You are a Senior Legal Strategist. Your goal is to provide actionable solutions.
                        {lang_instr}
                        1. Answer questions based on the CONTRACT CONTEXT provided.
                        2. If the user asks for suggestions or 'what to do', provide strategic advice and negotiation tips.
                        3. Be proactive: if you see a high risk, suggest a safer alternative.
                        4. Provide clear, professional, and step-by-step solutions.
                        """
                        full_prompt = f"{system_instr}\n\nCONTRACT CONTEXT:\n{ctx}\n\nUSER INPUT: {prompt}"
                        
                        res = m.generate_content(full_prompt)
                        if res and res.text:
                            st.session_state.chat_history.append({"role": "assistant", "content": res.text})
                            st.session_state.working_model = mname # Cache it
                            model_found = True
                            break
                    except:
                        continue
                
                if not model_found:
                    st.session_state.chat_history.append({"role": "assistant", "content": "⚠️ All AI models failed. Please verify your API key access in Google AI Studio."})
                st.rerun()
            except Exception as e:
                st.session_state.chat_history.append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
                st.rerun()

        st.divider()
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with c2:
            if st.button("✕ Close", use_container_width=True):
                st.session_state.show_chat = False
                st.rerun()


    # Main Flow Call
    
    # Sidebar Trigger
    with st.sidebar:
        if st.button("💬 Open AI Assistant", key="sidebar_trigger", use_container_width=True, type="primary"):
            st.session_state.show_chat = True
            st.rerun()
            
    # 3. Call Dialog if active
    if st.session_state.get('show_chat'):
        ai_assistant_dialog_window()

if __name__ == "__main__":
    main()

