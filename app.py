import html
from urllib.parse import quote_plus, urlparse
import pandas as pd
import streamlit as st
from scraper import JobDiscoveryEngine


st.set_page_config(
    page_title="وصلة | Wasla - Jobs in Germany",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "wasla_light_mode" not in st.session_state:
    st.session_state["wasla_light_mode"] = True
light_mode = st.session_state["wasla_light_mode"]
ui_language = st.session_state.get("wasla_ui_language", "العربية")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

    /* ─── Reset & Base ─────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; }

    html, body, .stApp {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        background-color: #0d1117 !important;
        color: #e2e8f0 !important;
    }

    /* Hide sidebar */
    [data-testid="collapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Hide Streamlit default header */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    /* Center and constrain main content container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 860px !important;
        margin: 0 auto !important;
    }

    /* ─── Typography ────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6,
    p, label,
    .stMarkdown, .stText {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }

    /* ─── Page header ───────────────────────────────────────── */
    .wasla-header {
        text-align: center !important;
        margin-bottom: 2.5rem;
        padding-top: 0.5rem;
    }
    .wasla-logo {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 0.8rem;
        font-weight: 700;
        color: #8b949e;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .wasla-logo-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #1a7fc1;
        display: inline-block;
    }
    .wasla-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #e2e8f0;
        line-height: 1.2;
        margin: 0 0 0.5rem 0;
    }
    .wasla-title span { color: #1a7fc1; }
    .wasla-sub {
        font-size: 0.97rem;
        color: #8b949e;
        line-height: 1.75;
        max-width: 540px;
        margin: 0 auto;
    }

    /* ─── Search cards ──────────────────────────────────────── */
    .search-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.6rem 1.8rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .search-card-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #8b949e;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 1.1rem;
        display: flex;
        align-items: center;
        gap: 8px;
        direction: rtl;
    }
    .search-card-title::before {
        content: '';
        display: inline-block;
        width: 3px;
        height: 13px;
        background: #1a7fc1;
        border-radius: 2px;
        flex-shrink: 0;
    }

    /* ─── Text inputs ───────────────────────────────────────── */
    .stTextInput > div > div > input {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 1.0rem !important;
        padding: 0.65rem 1rem !important;
        direction: rtl !important;
        text-align: right !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1a7fc1 !important;
        box-shadow: 0 0 0 3px rgba(26,127,193,0.18) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: #4a5568 !important; }
    .stTextInput label {
        color: #c9d1d9 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* ─── Selectboxes ───────────────────────────────────────── */
    .stSelectbox > div > div {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-family: 'Cairo', sans-serif !important;
        transition: border-color 0.15s ease !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #1a7fc1 !important;
        box-shadow: 0 0 0 3px rgba(26,127,193,0.18) !important;
    }
    .stSelectbox label {
        color: #c9d1d9 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    ul[data-baseweb="menu"] {
        background: #1c2333 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    li[role="option"] {
        direction: rtl !important;
        text-align: right !important;
        color: #e2e8f0 !important;
        font-family: 'Cairo', sans-serif !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background: rgba(26,127,193,0.15) !important;
    }

    /* ─── Active Filter Pills ──────────────────────────────── */
    .active-filters-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.9rem;
        padding-top: 0.75rem;
        border-top: 1px dashed #21262d;
        direction: rtl !important;
    }
    .active-filters-title {
        color: #8b949e;
        font-size: 0.8rem;
        font-weight: 700;
        margin-left: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .filter-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(56, 139, 253, 0.12);
        border: 1px solid rgba(56, 139, 253, 0.35);
        color: #79c0ff;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Cairo', sans-serif !important;
    }
    .filter-pill-contract {
        background: rgba(240, 136, 62, 0.12);
        border-color: rgba(240, 136, 62, 0.35);
        color: #ffa657;
    }
    .filter-pill-remote {
        background: rgba(46, 160, 67, 0.12);
        border-color: rgba(46, 160, 67, 0.35);
        color: #7ee787;
    }
    .filter-pill-seniority {
        background: rgba(163, 113, 247, 0.12);
        border-color: rgba(163, 113, 247, 0.35);
        color: #d2a8ff;
    }

    /* ─── Divider ───────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid #21262d !important;
        margin: 1.5rem 0 !important;
    }

    /* ─── Primary CTA ───────────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: #1a7fc1 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.75rem 2rem !important;
        width: 100% !important;
        transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
        cursor: pointer !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #388bfd !important;
        box-shadow: 0 0 0 4px rgba(56,139,253,0.2), 0 3px 8px rgba(0,0,0,0.5) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
        background: #1a7fc1 !important;
    }

    /* Secondary / download */
    .stDownloadButton > button {
        background: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    .stDownloadButton > button:hover {
        border-color: #388bfd !important;
        color: #e2e8f0 !important;
        background: #2d333b !important;
    }

    /* ─── Metric cards ──────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        padding: 1rem 1.2rem !important;
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        justify-content: flex-start !important;
    }
    [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }

    /* ─── Alerts ────────────────────────────────────────────── */
    .stAlert {
        border-radius: 8px !important;
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    .stAlert > div { direction: rtl !important; text-align: right !important; }

    /* ─── Progress bar ──────────────────────────────────────── */
    .stProgress > div > div { background: #1a7fc1 !important; border-radius: 4px !important; }
    .stProgress > div { background: #21262d !important; border-radius: 4px !important; }

    /* ─── Dataframe ─────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ─── Welcome & tip boxes ───────────────────────────────── */
    .wasla-welcome {
        background: #161b22;
        border: 1px solid #30363d;
        border-right: 3px solid #1a7fc1;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        color: #8b949e;
        font-size: 0.95rem;
        line-height: 1.8;
        direction: rtl;
        text-align: right;
    }
    .wasla-tip {
        background: #0d2818;
        border: 1px solid #21382a;
        border-right: 3px solid #2ea043;
        border-radius: 10px;
        padding: 1rem 1.4rem;
        margin-top: 1rem;
        color: #7ee787;
        font-size: 0.9rem;
        line-height: 1.7;
        direction: rtl;
        text-align: right;
    }

    /* ─── Job Cards ─────────────────────────────────────────── */
    .jobs-container {
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        margin-top: 1rem;
        direction: rtl !important;
        text-align: right !important;
    }
    .job-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.25rem;
        direction: rtl !important;
        text-align: right !important;
        transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .job-card:hover {
        border-color: #1a7fc1;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
        transform: translateY(-2px);
    }
    .job-card-main {
        flex: 1;
        min-width: 0;
        direction: rtl !important;
        text-align: right !important;
    }
    .job-card-header {
        margin-bottom: 0.65rem;
    }
    .job-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #58a6ff;
        margin: 0 0 0.35rem 0;
        line-height: 1.35;
        word-break: break-word;
        font-family: 'Cairo', sans-serif !important;
    }
    .job-company {
        font-size: 0.95rem;
        font-weight: 600;
        color: #c9d1d9;
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Cairo', sans-serif !important;
    }
    .job-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
        direction: rtl !important;
    }
    .job-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.25rem 0.65rem;
        font-size: 0.8rem;
        color: #8b949e;
        white-space: nowrap;
        font-family: 'Cairo', sans-serif !important;
    }
    .job-badge-intern {
        background: rgba(56, 139, 253, 0.12);
        border-color: rgba(56, 139, 253, 0.35);
        color: #79c0ff;
        font-weight: 600;
    }
    .job-badge-remote {
        background: rgba(46, 160, 67, 0.12);
        border-color: rgba(46, 160, 67, 0.35);
        color: #7ee787;
        font-weight: 600;
    }
    .job-badge-hybrid {
        background: rgba(210, 153, 34, 0.12);
        border-color: rgba(210, 153, 34, 0.35);
        color: #e3b341;
    }
    .job-badge-seniority {
        background: rgba(163, 113, 247, 0.12);
        border-color: rgba(163, 113, 247, 0.35);
        color: #d2a8ff;
        font-weight: 600;
    }
    .job-badge-contract {
        background: rgba(240, 136, 62, 0.12);
        border-color: rgba(240, 136, 62, 0.35);
        color: #ffa657;
        font-weight: 600;
    }
    .job-badge-source-linkedin {
        background: rgba(10, 102, 194, 0.15);
        border-color: rgba(10, 102, 194, 0.4);
        color: #70b5f9;
        font-weight: 700;
    }
    .job-badge-source-tanqeeb {
        background: rgba(46, 160, 67, 0.15);
        border-color: rgba(46, 160, 67, 0.45);
        color: #56d364;
        font-weight: 700;
    }
    .job-badge-source-multi {
        background: linear-gradient(135deg, rgba(10, 102, 194, 0.25), rgba(235, 87, 87, 0.25));
        border-color: rgba(163, 113, 247, 0.6);
        color: #d2a8ff;
        font-weight: 700;
        box-shadow: 0 0 8px rgba(163, 113, 247, 0.25);
    }
    .job-badge-source-indeed {
        background: rgba(33, 142, 241, 0.14);
        border-color: rgba(33, 142, 241, 0.36);
        color: #79c0ff;
        font-weight: 700;
    }
    .job-badge-source-post {
        background: rgba(240, 136, 62, 0.14);
        border-color: rgba(240, 136, 62, 0.36);
        color: #ffa657;
        font-weight: 700;
    }
    .job-badge-eligibility {
        background: rgba(248, 81, 73, 0.14);
        border-color: rgba(248, 81, 73, 0.36);
        color: #ff7b72;
        font-weight: 700;
    }
    .job-card-action {
        flex-shrink: 0;
    }
    .job-apply-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #1a7fc1;
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 0.65rem 1.3rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        font-family: 'Cairo', sans-serif !important;
        transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        white-space: nowrap;
    }
    .job-apply-btn:hover {
        background: #388bfd;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(56, 139, 253, 0.35);
    }
    .job-apply-btn:active {
        transform: translateY(0);
    }

    /* ─── Tabs ──────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent !important;
        border-bottom: 1px solid #30363d !important;
        padding-bottom: 0.2rem !important;
        direction: rtl !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px 8px 0 0 !important;
        color: #8b949e !important;
        font-family: 'Cairo', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.2rem !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0 !important;
        border-color: #484f58 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        border-color: #1a7fc1 !important;
        border-bottom-color: #21262d !important;
        color: #58a6ff !important;
    }

    /* ─── Responsive (Mobile & Tablets) ─────────────────────── */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
        .wasla-header {
            margin-bottom: 1.5rem !important;
        }
        .wasla-title {
            font-size: 1.6rem !important;
            line-height: 1.35 !important;
        }
        .wasla-sub {
            font-size: 0.88rem !important;
            line-height: 1.6 !important;
            padding: 0 0.5rem !important;
        }
        .search-card {
            padding: 1.1rem 0.9rem !important;
            margin-bottom: 1rem !important;
            border-radius: 10px !important;
        }
        .stRadio > div {
            flex-direction: column !important;
        }

        /* Metrics grid: 2x2 on mobile */
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0.5rem !important;
        }
        [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"] {
            width: 100% !important;
            min-width: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stMetric"] {
            padding: 0.65rem 0.75rem !important;
            min-height: 75px !important;
            border-radius: 8px !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.72rem !important;
            line-height: 1.3 !important;
            white-space: normal !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
            line-height: 1.2 !important;
        }

        /* Top Bar results header & download button */
        .stDownloadButton > button {
            width: 100% !important;
            margin-top: 0.4rem !important;
            font-size: 0.85rem !important;
            padding: 0.6rem 0.8rem !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
        }

        /* Job Cards on Mobile: Vertical Stack (Zero Overlap) */
        .jobs-container {
            gap: 0.75rem !important;
        }
        .job-card {
            flex-direction: column !important;
            align-items: stretch !important;
            justify-content: flex-start !important;
            padding: 1rem 0.95rem !important;
            gap: 0.85rem !important;
            border-radius: 10px !important;
        }
        .job-card-main {
            width: 100% !important;
            min-width: 0 !important;
        }
        .job-card-header {
            margin-bottom: 0.45rem !important;
        }
        .job-title {
            font-size: 1.05rem !important;
            line-height: 1.35 !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
        }
        .job-company {
            font-size: 0.88rem !important;
            flex-wrap: wrap !important;
            gap: 4px !important;
        }
        .job-badges {
            gap: 0.35rem !important;
            margin-top: 0.45rem !important;
        }
        .job-badge {
            font-size: 0.73rem !important;
            padding: 0.2rem 0.5rem !important;
            white-space: normal !important;
            word-break: break-word !important;
            line-height: 1.3 !important;
        }
        .job-card-action {
            width: 100% !important;
            margin-top: 0.25rem !important;
            display: block !important;
        }
        .job-apply-btn {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
            padding: 0.75rem 1rem !important;
            font-size: 0.92rem !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
        }

        /* Active Filter Pills Bar on Mobile */
        .active-filters-row {
            gap: 5px !important;
            padding-top: 0.6rem !important;
            margin-top: 0.65rem !important;
        }
        .filter-pill {
            font-size: 0.72rem !important;
            padding: 0.2rem 0.55rem !important;
        }
        .active-filters-title {
            font-size: 0.72rem !important;
        }
        .wasla-footer {
            flex-direction: column !important;
            gap: 0.35rem !important;
            padding: 1.25rem 0.75rem !important;
            text-align: center !important;
        }
        .wasla-footer span,
        .wasla-footer a {
            text-align: center !important;
        }
        .stCheckbox {
            min-height: 2.8rem !important;
            display: flex !important;
            align-items: center !important;
        }
    }

    /* Extra small mobile adjustments */
    @media (max-width: 420px) {
        .wasla-title {
            font-size: 1.35rem !important;
        }
        .job-title {
            font-size: 0.98rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.68rem !important;
        }
    }

    .wasla-footer {
        margin: 3.5rem auto 0;
        padding: 1.25rem 1rem;
        max-width: 860px;
        border-top: 1px solid #30363d;
        color: #8b949e;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.55rem;
        font-size: 0.82rem;
        direction: rtl;
        text-align: center;
    }
    .wasla-footer a {
        color: #58a6ff !important;
        text-decoration: none !important;
        font-weight: 700;
    }
    .wasla-footer a:hover { text-decoration: underline !important; }

    #MainMenu, footer { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

theme_css = """
<style>
html, body, .stApp { background: #f6f8fb !important; color: #14213d !important; }
[data-testid="stHeader"] { background: rgba(246,248,251,0.9) !important; }
.search-card, [data-testid="stMetric"], .job-card { background: #ffffff !important; border-color: #d8e0ea !important; }
.stTextInput > div > div > input, .stSelectbox > div > div { background: #ffffff !important; border-color: #c9d5e3 !important; color: #14213d !important; }
.stSelectbox [data-baseweb="select"] *, .stSelectbox [role="combobox"] *, .stSelectbox input { color: #14213d !important; -webkit-text-fill-color: #14213d !important; }
.stTextInput label, .stSelectbox label, [data-testid="stMetricValue"], .wasla-title { color: #14213d !important; }
.wasla-logo, .wasla-sub, [data-testid="stMetricLabel"], .job-badge { color: #526174 !important; }
.job-company { color: #34445c !important; }
.job-card:hover { box-shadow: 0 8px 24px rgba(28, 63, 105, 0.12) !important; }
.stDownloadButton > button { background: #ffffff !important; color: #253858 !important; border-color: #c9d5e3 !important; }
ul[data-baseweb="menu"] { background: #ffffff !important; border-color: #d8e0ea !important; }
/* Streamlit renders the open select menu in a BaseWeb popover.  Styling only
   the closed selectbox left the menu dark after switching to light mode. */
div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"],
ul[data-baseweb="menu"] { background: #ffffff !important; border-color: #d8e0ea !important; }
li[role="option"], div[role="option"] { color: #14213d !important; background: #ffffff !important; }
li[role="option"]:hover, li[role="option"][aria-selected="true"],
div[role="option"]:hover, div[role="option"][aria-selected="true"] {
    background: #e8f1fb !important;
    color: #14213d !important;
}
.wasla-footer { border-color: #d8e0ea !important; color: #526174 !important; }
</style>
""" if light_mode else ""
st.markdown(theme_css, unsafe_allow_html=True)


COUNTRIES = {
    "مصر": {
        "مصر كلها": "Egypt",
        "القاهرة (Cairo)": "Cairo, Egypt",
        "الجيزة (Giza)": "Giza, Egypt",
        "الإسكندرية (Alexandria)": "Alexandria, Egypt",
        "المنصورة / الدقهلية (Mansoura)": "Mansoura, Egypt",
        "طنطا / الغربية (Tanta)": "Tanta, Egypt",
        "الزقازيق / الشرقية (Zagazig)": "Zagazig, Egypt",
        "الإسماعيلية (Ismailia)": "Ismailia, Egypt",
        "بورسعيد (Port Said)": "Port Said, Egypt",
        "السويس (Suez)": "Suez, Egypt",
        "القليوبية / بنها (Qalyubia)": "Qalyubia, Egypt",
        "المنوفية / شبين الكوم (Menofia)": "Menofia, Egypt",
        "دمياط (Damietta)": "Damietta, Egypt",
        "كفر الشيخ (Kafr El Sheikh)": "Kafr El Sheikh, Egypt",
        "البحيرة / دمنهور (Beheira)": "Beheira, Egypt",
        "الفيوم (Faiyum)": "Faiyum, Egypt",
        "بني سويف (Beni Suef)": "Beni Suef, Egypt",
        "المنيا (Minya)": "Minya, Egypt",
        "أسيوط (Asyut)": "Asyut, Egypt",
        "سوهاج (Sohag)": "Sohag, Egypt",
        "قنا والأقصر وأسوان (Upper Egypt)": "Aswan, Egypt",
        "الغردقة / البحر الأحمر (Hurghada)": "Hurghada, Egypt",
        "شرم الشيخ / سيناء (South Sinai)": "Sharm El Sheikh, Egypt",
        "محافظة تانية (كتابة يدوية)": "__custom__",
    },
    "السعودية": {
        "السعودية كلها": "Saudi Arabia",
        "الرياض (Riyadh)": "Riyadh, Saudi Arabia",
        "جدة (Jeddah)": "Jeddah, Saudi Arabia",
        "الدمام والخبر (Eastern Province)": "Dammam, Saudi Arabia",
        "مكة المكرمة (Mecca)": "Mecca, Saudi Arabia",
        "المدينة المنورة (Medina)": "Medina, Saudi Arabia",
        "مدينة تانية (كتابة يدوية)": "__custom__",
    },
    "الإمارات": {
        "الإمارات كلها": "United Arab Emirates",
        "دبي (Dubai)": "Dubai, United Arab Emirates",
        "أبوظبي (Abu Dhabi)": "Abu Dhabi, United Arab Emirates",
        "الشارقة (Sharjah)": "Sharjah, United Arab Emirates",
        "إمارة تانية (كتابة يدوية)": "__custom__",
    },
    "قطر": {
        "قطر كلها": "Qatar",
        "الدوحة (Doha)": "Doha, Qatar",
        "الريان (Al Rayyan)": "Al Rayyan, Qatar",
        "مدينة تانية (كتابة يدوية)": "__custom__",
    },
    "ألمانيا": {
        "ألمانيا كلها": "Germany",
        "برلين (Berlin)": "Berlin, Germany",
        "دوسلدورف (Düsseldorf)": "Düsseldorf, Germany",
        "كولن (Köln / Cologne)": "Cologne, Germany",
        "ميونخ (München / Munich)": "Munich, Germany",
        "هامبورغ (Hamburg)": "Hamburg, Germany",
        "فرانكفورت (Frankfurt)": "Frankfurt, Germany",
        "مدينة تانية (كتابة يدوية)": "__custom__",
    },
    "هولندا": {
        "هولندا كلها": "Netherlands",
        "أمستردام (Amsterdam)": "Amsterdam, Netherlands",
        "روتردام (Rotterdam)": "Rotterdam, Netherlands",
        "لاهاي (The Hague)": "The Hague, Netherlands",
        "أوترخت (Utrecht)": "Utrecht, Netherlands",
        "مدينة تانية (كتابة يدوية)": "__custom__",
    },
    "بلد تانية (كتابة يدوية)": {
        "كتابة يدوية (Custom)": "__custom__",
    },
}

JOB_TYPES = {
    "الكل (مش فارقة معايا)": "all",
    "دوام كامل (Full-time)": "full_time",
    "دوام جزئي (Part-time)": "part_time",
    "عقد عمل / عمل حر (Contract)": "contract",
}

SENIORITY_LEVELS = {
    "الكل (أي مستوى)": "all",
    "تدريب طلبة وخريجين (Internship)": "internship",
    "مبتدئ / حديث تخرج (Junior / Entry)": "entry",
    "متوسط الخبرة (Mid-Level)": "mid",
    "سينيور / خبير (Senior / Lead)": "senior",
    "إدارة وقيادة (Manager / Director)": "director",
}

WORKPLACE_TYPES = {
    "الكل (المهم نشتغل)": "all",
    "Remote - من البيت": "remote",
    "Hybrid - يومين كده ويومين كده": "hybrid",
    "On-site - من الشركة": "onsite",
}

DATE_POSTED_OPTIONS = {
    "آخر أسبوع (أحسن فرصة للتقديم)": "past_week",
    "آخر 24 ساعة (طازة طازة)": "past_24h",
    "أي وقت (المتاح كله)": "all",
}


LANGUAGE_CODES = {"العربية": "ar", "English": "en", "Deutsch": "de"}

I18N = {
    "ar": {
        "language": "اللغة",
        "tagline": "فرصتك القادمة في ألمانيا تبدأ من هنا",
        "result_language": "لغة إعلانات الوظائف",
        "result_language_help": "نبحث بالألمانية والإنجليزية معًا لزيادة فرص العثور على وظائف مناسبة في ألمانيا.",
        "theme": "☀️ فاتح",
        "job_title": "المسمى الوظيفي",
        "job_title_placeholder": "مثلاً: Data Analyst, Cyber Security, Pflegefachkraft",
        "job_title_help": "يمكنك كتابة أكثر من مسمى والفصل بينهم بفاصلة (,). نضيف المرادفات الألمانية تلقائيًا عند توفرها.",
        "skills": "المهارات والشهادات (اختياري)",
        "skills_placeholder": "مثلاً: Python, AWS, German B2, Visa Sponsorship",
        "skills_help": "أضف المهارات أو الشهادات أو مستوى اللغة أو كلمات مثل Visa Sponsorship وRelocation.",
        "job_type": "نوع التوظيف",
        "seniority": "مستوى الخبرة",
        "workplace": "نظام العمل",
        "eligibility": "⚙️ فلاتر الأهلية والتوطين",
        "eligibility_caption": "نخفي فقط الإعلانات التي تشترط صراحة جنسية محلية في الخليج.",
        "exclude_uae": "استبعاد وظائف الإماراتيين فقط",
        "exclude_saudi": "استبعاد وظائف السعوديين فقط",
        "exclude_gcc": "استبعاد وظائف مواطني الخليج فقط",
        "intern_no_exp": "تدريب بدون خبرة سابقة",
        "include_indeed": "البحث في Indeed",
        "include_posts": "البحث في منشورات التوظيف على LinkedIn",
        "germany_sources": "🇩🇪 مصادر التوظيف في ألمانيا",
        "germany_sources_caption": "مفعّلة افتراضيًا وتظهر نتائجها عند اختيار ألمانيا أو مدينة ألمانية.",
        "bundesagentur": "Jobsuche الحكومية",
        "fast_search": "بحث سريع (صفحة واحدة لكل مصدر)",
        "fast_search_help": "ألغِ الاختيار لبحث أوسع قد يستغرق وقتًا أطول.",
        "country": "الدولة",
        "city": "المدينة",
        "date": "تاريخ النشر",
        "date_help": "التقديم خلال أول 24 ساعة أو أسبوع يزيد فرصة مشاهدة طلبك.",
        "custom_location": "اكتب المدينة أو الدولة بالإنجليزية أو الألمانية",
        "custom_location_help": "مثال: Leipzig, Germany أو Köln, Deutschland",
        "search": "ابحث عن وظائف في ألمانيا",
        "linkedin_posts": "افتح بحث منشورات LinkedIn ↗",
        "google_xray": "بحث Google في منشورات LinkedIn ↗",
        "linkedin_help": "يفتح بحثًا مباشرًا في LinkedIn وقد يتطلب تسجيل الدخول.",
        "google_help": "بحث X-Ray إضافي عن منشورات التوظيف العامة.",
        "missing_title": "اكتب مسمى وظيفيًا واحدًا على الأقل لبدء البحث.",
        "missing_location": "اختر الدولة أو المدينة التي تريد البحث فيها.",
        "searching": "نبحث الآن في أفضل مصادر التوظيف الألمانية والدولية...",
        "search_error": "حدثت مشكلة أثناء البحث: {error}. حاول مرة أخرى.",
        "total": "إجمالي الفرص",
        "companies": "الشركات",
        "contracts": "عقود وعمل حر",
        "internships": "تدريب",
        "remote": "عن بُعد",
        "found": "وجدنا {count} فرصة مناسبة من مصادر متعددة بعد إزالة التكرار.",
        "outside": "استُبعدت {count} نتيجة خارج الموقع المختار",
        "uae_excluded": "أُخفي {count} إعلانًا للإماراتيين فقط",
        "saudi_excluded": "أُخفي {count} إعلانًا للسعوديين فقط",
        "gcc_excluded": "أُخفي {count} إعلانًا لمواطني الخليج فقط",
        "download": "تنزيل النتائج CSV",
        "untitled": "وظيفة بدون عنوان",
        "unknown": "غير محدد",
        "apply": "عرض الوظيفة والتقديم ↗",
        "open_post": "افتح منشور التوظيف ↗",
        "remote_badge": "عن بُعد (Remote)",
        "hybrid_badge": "هجين (Hybrid)",
        "onsite_badge": "من مقر الشركة (On-site)",
        "no_results": "لم نجد نتائج مطابقة هذه المرة. جرّب مسمى أوسع، أو اختر ألمانيا كلها، أو ألغِ بعض الفلاتر.",
        "contact": "تواصل مع Moustafa على X",
        "forked": "مبني بالاعتماد على",
        "uae_help": "يخفي الإعلانات التي تذكر صراحة UAE National أو Emirati أو Emiratisation.",
        "saudi_help": "يخفي الإعلانات التي تذكر صراحة Saudi National أو Saudization.",
        "gcc_help": "يخفي الإعلانات التي تذكر صراحة GCC National أو Gulf National.",
        "intern_help": "يستبعد التدريبات التي تطلب خبرة سابقة.",
        "posts_help": "يعرض منشورات التوظيف العامة كفرص تواصل وقد تحتاج لمراسلة الناشر.",
        "germany_focus": "نبحث في ألمانيا أولًا عبر StepStone وJobsuche وXING وIndeed Deutschland وMake it in Germany، بالإضافة إلى LinkedIn.",
    },
    "en": {
        "language": "Language", "tagline": "Your next opportunity in Germany starts here",
        "result_language": "Job listing language", "result_language_help": "Search in German and English to improve coverage across Germany.",
        "theme": "☀️ Light", "job_title": "Job title", "job_title_placeholder": "e.g. Data Analyst, Cyber Security, Pflegefachkraft",
        "job_title_help": "Enter multiple roles separated by commas. German equivalents are added automatically when available.",
        "skills": "Skills and certifications (optional)", "skills_placeholder": "e.g. Python, AWS, German B2, Visa Sponsorship",
        "skills_help": "Add skills, certifications, language level, Visa Sponsorship or Relocation.",
        "job_type": "Employment type", "seniority": "Experience level", "workplace": "Workplace",
        "eligibility": "⚙️ Eligibility and localization filters", "eligibility_caption": "Only listings that explicitly require a local Gulf nationality are hidden.",
        "exclude_uae": "Exclude UAE nationals-only jobs", "exclude_saudi": "Exclude Saudi nationals-only jobs", "exclude_gcc": "Exclude GCC nationals-only jobs",
        "intern_no_exp": "Internships with no prior experience", "include_indeed": "Search Indeed", "include_posts": "Search LinkedIn recruiter posts",
        "germany_sources": "🇩🇪 German job sources", "germany_sources_caption": "Enabled by default and used for Germany or a German city.",
        "bundesagentur": "Federal Jobsuche", "fast_search": "Fast search (one page per source)", "fast_search_help": "Turn off for a broader search that may take longer.",
        "country": "Country", "city": "City", "date": "Date posted", "date_help": "Applying within the first 24 hours or week improves visibility.",
        "custom_location": "Enter a city or country in English or German", "custom_location_help": "Example: Leipzig, Germany or Köln, Deutschland",
        "search": "Find jobs in Germany", "linkedin_posts": "Open LinkedIn Posts search ↗", "google_xray": "Google X-Ray LinkedIn posts ↗",
        "linkedin_help": "Opens LinkedIn content search and may require sign-in.", "google_help": "An additional X-Ray search for public recruiter posts.",
        "missing_title": "Enter at least one job title to start searching.", "missing_location": "Choose the country or city you want to search.",
        "searching": "Searching leading German and international job sources...", "search_error": "Something went wrong while searching: {error}. Please try again.",
        "total": "Total opportunities", "companies": "Companies", "contracts": "Contracts / freelance", "internships": "Internships", "remote": "Remote",
        "found": "Found {count} matching opportunities across multiple sources after deduplication.", "outside": "Excluded {count} result(s) outside the selected location",
        "uae_excluded": "Hidden {count} UAE nationals-only listing(s)", "saudi_excluded": "Hidden {count} Saudi nationals-only listing(s)", "gcc_excluded": "Hidden {count} GCC nationals-only listing(s)",
        "download": "Download results as CSV", "untitled": "Untitled job", "unknown": "Not specified", "apply": "View job and apply ↗", "open_post": "Open recruiter post ↗",
        "remote_badge": "Remote", "hybrid_badge": "Hybrid", "onsite_badge": "On-site",
        "no_results": "No exact matches this time. Try a broader title, select all of Germany, or relax some filters.",
        "contact": "Contact Moustafa on X", "forked": "Built on", "uae_help": "Hides listings explicitly restricted to UAE nationals.", "saudi_help": "Hides listings explicitly restricted to Saudi nationals.", "gcc_help": "Hides listings explicitly restricted to GCC nationals.", "intern_help": "Excludes internships that require prior experience.", "posts_help": "Shows public recruiter posts as networking opportunities; you may need to message the author.", "germany_focus": "Germany-first search across StepStone, Federal Jobsuche, XING, Indeed Deutschland, Make it in Germany and LinkedIn.",
    },
    "de": {
        "language": "Sprache", "tagline": "Ihre nächste Chance in Deutschland beginnt hier",
        "result_language": "Sprache der Stellenanzeigen", "result_language_help": "Suche auf Deutsch und Englisch für eine bessere Abdeckung in Deutschland.",
        "theme": "☀️ Hell", "job_title": "Berufsbezeichnung", "job_title_placeholder": "z. B. Data Analyst, Cyber Security, Pflegefachkraft",
        "job_title_help": "Mehrere Berufe durch Kommas trennen. Deutsche Entsprechungen werden automatisch ergänzt.",
        "skills": "Kenntnisse und Zertifikate (optional)", "skills_placeholder": "z. B. Python, AWS, Deutsch B2, Visa Sponsorship",
        "skills_help": "Kenntnisse, Zertifikate, Sprachniveau, Visa Sponsorship oder Relocation hinzufügen.",
        "job_type": "Beschäftigungsart", "seniority": "Erfahrungsstufe", "workplace": "Arbeitsmodell",
        "eligibility": "⚙️ Filter für Berechtigung und Lokalisierung", "eligibility_caption": "Nur Anzeigen mit ausdrücklich geforderter lokaler Golf-Staatsangehörigkeit werden ausgeblendet.",
        "exclude_uae": "Nur für VAE-Staatsangehörige ausschließen", "exclude_saudi": "Nur für saudische Staatsangehörige ausschließen", "exclude_gcc": "Nur für GCC-Staatsangehörige ausschließen",
        "intern_no_exp": "Praktika ohne Berufserfahrung", "include_indeed": "Indeed durchsuchen", "include_posts": "LinkedIn-Recruiter-Beiträge durchsuchen",
        "germany_sources": "🇩🇪 Deutsche Jobquellen", "germany_sources_caption": "Standardmäßig aktiviert für Deutschland und deutsche Städte.",
        "bundesagentur": "Jobsuche der Bundesagentur", "fast_search": "Schnellsuche (eine Seite je Quelle)", "fast_search_help": "Deaktivieren für eine breitere, möglicherweise längere Suche.",
        "country": "Land", "city": "Stadt", "date": "Veröffentlicht", "date_help": "Bewerbungen in den ersten 24 Stunden oder der ersten Woche sind oft sichtbarer.",
        "custom_location": "Stadt oder Land auf Deutsch oder Englisch eingeben", "custom_location_help": "Beispiel: Leipzig, Germany oder Köln, Deutschland",
        "search": "Jobs in Deutschland finden", "linkedin_posts": "LinkedIn-Beiträge durchsuchen ↗", "google_xray": "Google X-Ray für LinkedIn-Beiträge ↗",
        "linkedin_help": "Öffnet die LinkedIn-Inhaltssuche; eventuell ist eine Anmeldung erforderlich.", "google_help": "Zusätzliche X-Ray-Suche nach öffentlichen Recruiting-Beiträgen.",
        "missing_title": "Bitte mindestens eine Berufsbezeichnung eingeben.", "missing_location": "Bitte Land oder Stadt auswählen.",
        "searching": "Führende deutsche und internationale Jobquellen werden durchsucht...", "search_error": "Bei der Suche ist ein Fehler aufgetreten: {error}. Bitte erneut versuchen.",
        "total": "Stellen insgesamt", "companies": "Unternehmen", "contracts": "Vertrag / Freelance", "internships": "Praktika", "remote": "Remote",
        "found": "{count} passende Stellen aus mehreren Quellen ohne Duplikate gefunden.", "outside": "{count} Ergebnis(se) außerhalb des gewählten Orts ausgeschlossen",
        "uae_excluded": "{count} Anzeige(n) nur für VAE-Staatsangehörige ausgeblendet", "saudi_excluded": "{count} Anzeige(n) nur für saudische Staatsangehörige ausgeblendet", "gcc_excluded": "{count} Anzeige(n) nur für GCC-Staatsangehörige ausgeblendet",
        "download": "Ergebnisse als CSV herunterladen", "untitled": "Stelle ohne Titel", "unknown": "Nicht angegeben", "apply": "Stelle ansehen und bewerben ↗", "open_post": "Recruiting-Beitrag öffnen ↗",
        "remote_badge": "Remote", "hybrid_badge": "Hybrid", "onsite_badge": "Vor Ort",
        "no_results": "Diesmal keine exakten Treffer. Versuchen Sie einen breiteren Titel, ganz Deutschland oder weniger Filter.",
        "contact": "Moustafa auf X kontaktieren", "forked": "Basiert auf", "uae_help": "Blendet Stellen aus, die ausdrücklich nur für VAE-Staatsangehörige bestimmt sind.", "saudi_help": "Blendet Stellen aus, die ausdrücklich nur für saudische Staatsangehörige bestimmt sind.", "gcc_help": "Blendet Stellen aus, die ausdrücklich nur für GCC-Staatsangehörige bestimmt sind.", "intern_help": "Schließt Praktika aus, die Berufserfahrung voraussetzen.", "posts_help": "Zeigt öffentliche Recruiting-Beiträge als Kontaktmöglichkeit; eventuell müssen Sie den Autor anschreiben.", "germany_focus": "Deutschlandweite Suche über StepStone, Jobsuche der Bundesagentur, XING, Indeed Deutschland, Make it in Germany und LinkedIn.",
    },
}

OPTION_TRANSLATIONS = {
    "all": {"ar": "الكل", "en": "All", "de": "Alle"},
    "full_time": {"ar": "دوام كامل", "en": "Full-time", "de": "Vollzeit"},
    "part_time": {"ar": "دوام جزئي", "en": "Part-time", "de": "Teilzeit"},
    "contract": {"ar": "عقد / عمل حر", "en": "Contract / Freelance", "de": "Vertrag / Freelance"},
    "internship": {"ar": "تدريب", "en": "Internship", "de": "Praktikum"},
    "entry": {"ar": "مبتدئ / حديث تخرج", "en": "Junior / Entry", "de": "Junior / Berufseinstieg"},
    "mid": {"ar": "متوسط الخبرة", "en": "Mid-level", "de": "Mittlere Erfahrung"},
    "senior": {"ar": "خبير / سينيور", "en": "Senior / Lead", "de": "Senior / Lead"},
    "director": {"ar": "إدارة وقيادة", "en": "Manager / Director", "de": "Manager / Leitung"},
    "remote": {"ar": "عن بُعد", "en": "Remote", "de": "Remote"},
    "hybrid": {"ar": "هجين", "en": "Hybrid", "de": "Hybrid"},
    "onsite": {"ar": "من مقر الشركة", "en": "On-site", "de": "Vor Ort"},
    "past_week": {"ar": "آخر أسبوع", "en": "Past week", "de": "Letzte Woche"},
    "past_24h": {"ar": "آخر 24 ساعة", "en": "Past 24 hours", "de": "Letzte 24 Stunden"},
}

COUNTRY_LABELS = {
    "مصر": {"ar": "مصر", "en": "Egypt", "de": "Ägypten"}, "السعودية": {"ar": "السعودية", "en": "Saudi Arabia", "de": "Saudi-Arabien"},
    "الإمارات": {"ar": "الإمارات", "en": "United Arab Emirates", "de": "Vereinigte Arabische Emirate"}, "قطر": {"ar": "قطر", "en": "Qatar", "de": "Katar"},
    "ألمانيا": {"ar": "🇩🇪 ألمانيا", "en": "🇩🇪 Germany", "de": "🇩🇪 Deutschland"}, "هولندا": {"ar": "هولندا", "en": "Netherlands", "de": "Niederlande"},
    "بلد تانية (كتابة يدوية)": {"ar": "دولة أخرى", "en": "Other country", "de": "Anderes Land"},
}


def tr(key: str, **kwargs) -> str:
    value = I18N[LANGUAGE_CODES.get(ui_language, "ar")][key]
    return value.format(**kwargs) if kwargs else value


def option_label(value: str) -> str:
    return OPTION_TRANSLATIONS.get(value, {}).get(LANGUAGE_CODES.get(ui_language, "ar"), value)


def localize_job_value(value: str) -> str:
    if ui_language == "العربية":
        return value
    replacements = {
        "غير محدد": "Not specified" if ui_language == "English" else "Nicht angegeben",
        "دوام كامل": "Full-time" if ui_language == "English" else "Vollzeit",
        "دوام جزئي": "Part-time" if ui_language == "English" else "Teilzeit",
        "تدريب": "Internship" if ui_language == "English" else "Praktikum",
        "مبتدئ": "Junior" if ui_language == "English" else "Berufseinstieg",
        "متوسط": "Mid-level" if ui_language == "English" else "Mittlere Erfahrung",
        "خبير": "Senior" if ui_language == "English" else "Senior",
        "عن بُعد": "Remote", "هجين": "Hybrid", "من المقر": "On-site" if ui_language == "English" else "Vor Ort",
    }
    localized = value
    for source, target in replacements.items():
        localized = localized.replace(source, target)
    return localized


language_col, theme_col = st.columns([4, 1])
with language_col:
    ui_language = st.selectbox(
        "Language / اللغة / Sprache",
        options=["العربية", "English", "Deutsch"],
        key="wasla_ui_language",
    )
with theme_col:
    st.toggle(tr("theme"), key="wasla_light_mode")

ui_direction = "rtl" if ui_language == "العربية" else "ltr"
text_align = "right" if ui_direction == "rtl" else "left"

st.markdown(
    f"""
    <div class="wasla-header">
        <div class="wasla-logo">
            <span class="wasla-logo-dot"></span>
            وصلة | Wasla
            <span class="wasla-logo-dot"></span>
        </div>
        <div class="wasla-title">Wasla <span>{tr('tagline')}</span></div>
        <div class="wasla-sub">{tr('germany_focus')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

search_language = st.selectbox(
    tr("result_language"),
    options=["English + Deutsch", "Deutsch / German"],
    index=0,
    help=tr("result_language_help"),
)

st.markdown(
    f"""
    <style>
      html, body, .stApp {{ direction: {ui_direction} !important; }}
      body, p, label, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6 {{ text-align: {text_align} !important; }}
      [data-testid="stHorizontalBlock"] {{ direction: {ui_direction} !important; width: 100% !important; overflow: visible !important; }}
      [data-testid="stColumn"] {{ direction: {ui_direction} !important; min-width: 0 !important; }}
      [data-testid="stExpander"] {{ direction: {ui_direction} !important; overflow: visible !important; }}
      [data-testid="stExpander"] summary {{ direction: {ui_direction} !important; text-align: {'right' if ui_direction == 'rtl' else 'left'} !important; white-space: normal !important; }}
      [data-testid="stCheckbox"], [data-testid="stRadio"] {{ direction: {ui_direction} !important; }}
      [data-testid="stCheckbox"] label, [data-testid="stRadio"] label {{ direction: {ui_direction} !important; text-align: {'right' if ui_direction == 'rtl' else 'left'} !important; }}
      .stSelectbox [data-baseweb="select"],
      .stSelectbox [data-baseweb="select"] > div,
      .stTextInput input {{ direction: {ui_direction} !important; text-align: {'right' if ui_direction == 'rtl' else 'left'} !important; }}
      .stRadio > label, .stSelectbox > label, .stTextInput > label {{ direction: {ui_direction} !important; }}
      [data-baseweb="popover"] *, ul[role="listbox"] *, li[role="option"] {{ direction: {ui_direction} !important; text-align: {'right' if ui_direction == 'rtl' else 'left'} !important; }}
      .jobs-container, .job-card, .job-card-main, .job-badges {{ direction: {ui_direction} !important; text-align: {text_align} !important; }}
      .job-card {{ flex-direction: {'row' if ui_direction == 'rtl' else 'row'}; }}
      @media (max-width: 760px) {{
        .stRadio > div {{ flex-wrap: wrap !important; gap: .25rem !important; }}
        .stRadio label {{ white-space: nowrap !important; }}
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


keywords_input = st.text_input(
    tr("job_title"),
    value="Data Analyst",
    placeholder=tr("job_title_placeholder"),
    help=tr("job_title_help"),
)

skill_keywords_input = st.text_input(
    tr("skills"),
    placeholder=tr("skills_placeholder"),
    help=tr("skills_help"),
)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

col_jt, col_sen, col_wp = st.columns(3)
with col_jt:
    job_type_label = st.selectbox(
        tr("job_type"),
        options=list(JOB_TYPES.keys()),
        index=0,
        format_func=lambda label: option_label(JOB_TYPES[label]),
    )
    selected_job_type = JOB_TYPES[job_type_label]

with col_sen:
    seniority_label = st.selectbox(
        tr("seniority"),
        options=list(SENIORITY_LEVELS.keys()),
        index=0,
        format_func=lambda label: option_label(SENIORITY_LEVELS[label]),
    )
    selected_seniority = SENIORITY_LEVELS[seniority_label]

with col_wp:
    workplace_label = st.selectbox(
        tr("workplace"),
        options=list(WORKPLACE_TYPES.keys()),
        index=0,
        format_func=lambda label: option_label(WORKPLACE_TYPES[label]),
    )
    selected_workplace = WORKPLACE_TYPES[workplace_label]

st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)
with st.expander(tr("eligibility"), expanded=False):
    st.caption(tr("eligibility_caption"))
    eligibility_col_uae, eligibility_col_saudi, eligibility_col_gcc = st.columns(3)
    with eligibility_col_uae:
        exclude_emirati_only = st.checkbox(
            tr("exclude_uae"),
            value=True,
            help=tr("uae_help"),
        )
    with eligibility_col_saudi:
        exclude_saudi_only = st.checkbox(
            tr("exclude_saudi"),
            value=True,
            help=tr("saudi_help"),
        )
    with eligibility_col_gcc:
        exclude_gcc_national_only = st.checkbox(
            tr("exclude_gcc"),
            value=True,
            help=tr("gcc_help"),
        )

filters_top_left, filters_top_right = st.columns(2)
with filters_top_left:
    internship_no_experience_only = st.checkbox(
        tr("intern_no_exp"),
        value=False,
        help=tr("intern_help"),
    )
filters_bottom_left, filters_bottom_right = st.columns(2)
with filters_bottom_left:
    include_indeed = st.checkbox(tr("include_indeed"), value=True)
with filters_bottom_right:
    include_recruiter_posts = st.checkbox(
        tr("include_posts"),
        value=True,
        help=tr("posts_help"),
    )
with st.expander(tr("germany_sources"), expanded=True):
    st.caption(tr("germany_sources_caption"))
    germany_source_one, germany_source_two, germany_source_three = st.columns(3)
    with germany_source_one:
        include_stepstone = st.checkbox("StepStone", value=True)
    with germany_source_two:
        include_bundesagentur = st.checkbox(tr("bundesagentur"), value=True)
    with germany_source_three:
        include_xing = st.checkbox("XING Jobs", value=True)
    germany_source_four, germany_source_five = st.columns(2)
    with germany_source_four:
        include_indeed_germany = st.checkbox("Indeed Deutschland", value=True)
    with germany_source_five:
        include_make_it_germany = st.checkbox("Make it in Germany", value=True)
fast_search = st.checkbox(
    tr("fast_search"),
    value=True,
    help=tr("fast_search_help"),
)



col_country, col_city, col_date = st.columns([1, 1.6, 1.2])
with col_country:
    country_options = ["ألمانيا"] + [country for country in COUNTRIES if country != "ألمانيا"]
    selected_country = st.selectbox(
        tr("country"),
        options=country_options,
        index=0,
        format_func=lambda country: COUNTRY_LABELS.get(country, {}).get(LANGUAGE_CODES.get(ui_language, "ar"), country),
    )
with col_city:
    available_cities = COUNTRIES[selected_country]
    selected_city_label = st.selectbox(
        tr("city"), options=list(available_cities.keys()), index=0,
        format_func=lambda city: city if ui_language == "العربية" else (
            city.split("(")[1].rstrip(")") if "(" in city else
            available_cities[city].replace(", Germany", "") if available_cities[city] != "__custom__" else
            ("Other city" if ui_language == "English" else "Andere Stadt")
        ),
    )
with col_date:
    date_posted_label = st.selectbox(
        tr("date"),
        options=list(DATE_POSTED_OPTIONS.keys()),
        index=0,
        format_func=lambda label: option_label(DATE_POSTED_OPTIONS[label]),
        help=tr("date_help"),
    )
    selected_date_posted = DATE_POSTED_OPTIONS[date_posted_label]

target_location_query = available_cities[selected_city_label]
if target_location_query == "__custom__":
    custom_loc = st.text_input(
        tr("custom_location"),
        value="Leipzig, Germany",
        help=tr("custom_location_help"),
    )
    target_location_query = custom_loc.strip()

st.markdown("</div>", unsafe_allow_html=True)


st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
search_clicked = st.button(tr("search"), type="primary", use_container_width=True)
language_terms = "hiring vacancy open position einstellen gesucht Bewerbung" if search_language == "English + Deutsch" else "einstellen gesucht Bewerbung Stellenausschreibung"
post_search_terms = " ".join(
    term for term in [keywords_input.strip(), skill_keywords_input.strip(), language_terms, target_location_query.strip()]
    if term
)
linkedin_content_search_url = (
    "https://www.linkedin.com/search/results/content/?keywords="
    + quote_plus(post_search_terms)
)
linkedin_xray_url = "https://www.google.com/search?q=" + quote_plus(
    f'site:linkedin.com/posts ({keywords_input.strip()}) ({target_location_query.strip()}) hiring'
)
link_col_one, link_col_two = st.columns(2)
with link_col_one:
    st.link_button(
        tr("linkedin_posts"),
        linkedin_content_search_url,
        use_container_width=True,
        help=tr("linkedin_help"),
    )
with link_col_two:
    st.link_button(
        tr("google_xray"),
        linkedin_xray_url,
        use_container_width=True,
        help=tr("google_help"),
    )
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)


if "scraped_jobs" not in st.session_state:
    st.session_state["scraped_jobs"] = []

search_fingerprint = (
    keywords_input.strip().lower(),
    skill_keywords_input.strip().lower(),
    selected_job_type,
    selected_seniority,
    selected_workplace,
    target_location_query.strip().lower(),
    selected_date_posted,
    exclude_emirati_only,
    exclude_saudi_only,
    exclude_gcc_national_only,
    include_indeed,
    include_recruiter_posts,
    include_stepstone,
    include_bundesagentur,
    include_xing,
    include_indeed_germany,
    include_make_it_germany,
    search_language,
    fast_search,
    internship_no_experience_only,
)
if "last_search_fingerprint" not in st.session_state:
    st.session_state["last_search_fingerprint"] = search_fingerprint


if st.session_state["last_search_fingerprint"] != search_fingerprint:
    st.session_state["scraped_jobs"] = []
    st.session_state["last_search_fingerprint"] = search_fingerprint


for _old_job in st.session_state["scraped_jobs"]:
    if "غير محدد" in _old_job.get("بيئة العمل", ""):
        _old_job["بيئة العمل"] = "غير محدد"

search_attempted = False

if search_clicked:
    st.session_state["last_search_fingerprint"] = search_fingerprint
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    skill_keywords = [k.strip() for k in skill_keywords_input.split(",") if k.strip()]

    if not keywords:
        st.error(tr("missing_title"))
    elif not target_location_query:
        st.error(tr("missing_location"))
    else:
        search_attempted = True
        effective_location = target_location_query.strip()
        effective_seniority = "internship" if internship_no_experience_only else selected_seniority
        engine = JobDiscoveryEngine(
            include_indeed=include_indeed,
            include_recruiter_posts=include_recruiter_posts,
            include_stepstone=include_stepstone,
            include_bundesagentur=include_bundesagentur,
            include_xing=include_xing,
            include_indeed_germany=include_indeed_germany,
            include_make_it_germany=include_make_it_germany,
        )
        progress_bar = st.progress(0)
        status_box = st.empty()

        def update_progress(ratio: float, msg: str):
            try:
                progress_bar.progress(min(max(float(ratio), 0.0), 1.0))
                status_box.info(tr("searching"))
            except Exception:
                pass

        try:
            with st.spinner(tr("searching")):
                jobs = engine.discover(
                    keywords=keywords,
                    location=effective_location,
                    job_type=selected_job_type,
                    seniority=effective_seniority,
                    workplace_type=selected_workplace,
                    date_posted=selected_date_posted,
                    skill_keywords=skill_keywords,
                    pages_per_keyword=1 if fast_search else 2,
                    exclude_emirati_only=exclude_emirati_only,
                    exclude_saudi_only=exclude_saudi_only,
                    exclude_gcc_national_only=exclude_gcc_national_only,
                    progress_callback=update_progress,
                )
            st.session_state["scraped_jobs"] = jobs
            st.session_state["discovery_metrics"] = getattr(engine, "last_metrics", {})
        except Exception as e:
            search_attempted = False
            st.session_state["scraped_jobs"] = []
            st.error(tr("search_error", error=e))
            try:
                with open("crash.log", "a", encoding="utf-8") as f:
                    import traceback
                    f.write(traceback.format_exc() + "\n")
            except Exception:
                pass
        finally:
            try:
                progress_bar.empty()
                status_box.empty()
            except Exception:
                pass


results = st.session_state["scraped_jobs"]

if results:
    df = pd.DataFrame(results)

    total_jobs = len(df)
    unique_companies = df["الشركة"].nunique()
    remote_count = len(df[df["بيئة العمل"].str.contains("عن بُعد", na=False)])

    if selected_job_type == "contract":
        col3_metric_label = tr("contracts")
        col3_metric_val = len(df[df["نوع الوظيفة"].str.contains("عقد|Contract|حر|Freelance", na=False)])
    else:
        col3_metric_label = tr("internships")
        col3_metric_val = len(df[df["نوع الوظيفة"].str.contains("تدريب|Intern", na=False)])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(tr("total"), total_jobs)
    col2.metric(tr("companies"), unique_companies)
    col3.metric(col3_metric_label, col3_metric_val)
    col4.metric(tr("remote"), remote_count)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    top_bar_col1, top_bar_col2 = st.columns([3, 1])
    with top_bar_col1:
        st.success(tr("found", count=total_jobs))
        metrics = st.session_state.get("discovery_metrics", {})
        location_excluded = metrics.get("location_excluded", 0)
        emirati_excluded = metrics.get("emirati_excluded", 0)
        saudi_excluded = metrics.get("saudi_excluded", 0)
        gcc_national_excluded = metrics.get("gcc_national_excluded", 0)
        if location_excluded or emirati_excluded or saudi_excluded or gcc_national_excluded:
            notes = []
            if location_excluded:
                notes.append(tr("outside", count=location_excluded))
            if emirati_excluded:
                notes.append(tr("uae_excluded", count=emirati_excluded))
            if saudi_excluded:
                notes.append(tr("saudi_excluded", count=saudi_excluded))
            if gcc_national_excluded:
                notes.append(tr("gcc_excluded", count=gcc_national_excluded))
            st.caption(" | ".join(notes))
    with top_bar_col2:
        export_columns = {
            "en": {"المسمى الوظيفي": "Job title", "الشركة": "Company", "المكان": "Location", "نوع الوظيفة": "Employment type", "مستوى الخبرة": "Experience level", "بيئة العمل": "Workplace", "تاريخ النشر": "Date posted", "رابط التقديم": "Application URL", "المصدر": "Source"},
            "de": {"المسمى الوظيفي": "Berufsbezeichnung", "الشركة": "Unternehmen", "المكان": "Ort", "نوع الوظيفة": "Beschäftigungsart", "مستوى الخبرة": "Erfahrungsstufe", "بيئة العمل": "Arbeitsmodell", "تاريخ النشر": "Veröffentlicht", "رابط التقديم": "Bewerbungslink", "المصدر": "Quelle"},
        }
        export_df = df.rename(columns=export_columns.get(LANGUAGE_CODES.get(ui_language, "ar"), {}))
        csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label=tr("download"),
            data=csv_bytes,
            file_name="wasla_job_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    cards_html = []
    for job in results:
        title = html.escape(str(job.get("المسمى الوظيفي", tr("untitled"))))
        company = html.escape(str(job.get("الشركة", tr("unknown"))))
        loc = html.escape(str(job.get("المكان", "Germany")))
        raw_job_type = str(job.get("نوع الوظيفة", "غير محدد"))
        raw_post_date = str(job.get("تاريخ النشر", "غير محدد"))
        job_type = html.escape(localize_job_value(raw_job_type))
        post_date = html.escape(localize_job_value(raw_post_date))
        raw_link = str(job.get("رابط التقديم", ""))
        parsed_link = urlparse(raw_link)
        link = raw_link if parsed_link.scheme in {"http", "https"} and parsed_link.netloc else ""

        sources = job.get("sources", [])
        if not sources:
            raw_source = str(job.get("المصدر", "LinkedIn"))
            sources = [s.strip() for s in raw_source.split("+") if s.strip()]

        if len(sources) > 1:
            sources_label = " · ".join(sources)
            source_html = f'<span class="job-badge job-badge-source-multi">✨ {sources_label}</span>'
            btn_text = tr("apply")
        elif "LinkedIn Recruiter Posts" in sources:
            source_html = '<span class="job-badge job-badge-source-post">LinkedIn Recruiter Post</span>'
            btn_text = tr("open_post")
        elif "Indeed" in sources:
            source_html = '<span class="job-badge job-badge-source-indeed">Indeed</span>'
            btn_text = tr("apply")
        elif "Tanqeeb" in sources:
            source_html = '<span class="job-badge job-badge-source-tanqeeb">Tanqeeb (تنقيب)</span>'
            btn_text = tr("apply")
        else:
            source_html = '<span class="job-badge job-badge-source-linkedin">LinkedIn</span>'
            btn_text = tr("apply")

        raw_seniority = str(job.get("مستوى الخبرة", "غير محدد"))
        seniority = html.escape(localize_job_value(raw_seniority))

        is_intern_type = "تدريب" in raw_job_type or "intern" in raw_job_type.lower()
        is_intern_seniority = "تدريب" in raw_seniority or "intern" in raw_seniority.lower()
        is_grad_type = "خريجين" in raw_job_type or "graduate" in raw_job_type.lower()
        is_grad_seniority = "خريجين" in raw_seniority or "graduate" in raw_seniority.lower()


        if (is_intern_type and is_intern_seniority) or (is_grad_type and is_grad_seniority) or (raw_job_type != "غير محدد" and raw_job_type == raw_seniority):
            seniority_html = ""
        elif raw_seniority != "غير محدد":
            seniority_badge_class = "job-badge-intern" if is_intern_seniority else "job-badge-seniority"
            seniority_html = f'<span class="job-badge {seniority_badge_class}">{seniority}</span>'
        else:
            seniority_html = ""

        if is_intern_type:
            type_badge_class = "job-badge-intern"
        elif "عقد" in raw_job_type or "Contract" in raw_job_type or "حر" in raw_job_type or "Freelance" in raw_job_type:
            type_badge_class = "job-badge-contract"
        else:
            type_badge_class = "job-badge-default"

        type_html = f'<span class="job-badge {type_badge_class}">{job_type}</span>' if raw_job_type != "غير محدد" else ""

        raw_workplace = str(job.get("بيئة العمل", ""))
        if "عن بُعد" in raw_workplace or "Remote" in raw_workplace:
            workplace_html = f'<span class="job-badge job-badge-remote">{tr("remote_badge")}</span>'
        elif "هجين" in raw_workplace or "Hybrid" in raw_workplace:
            workplace_html = f'<span class="job-badge job-badge-hybrid">{tr("hybrid_badge")}</span>'
        elif ("من المقر" in raw_workplace or "On-site" in raw_workplace) and ("غير محدد" not in raw_workplace):
            workplace_html = f'<span class="job-badge job-badge-default">{tr("onsite_badge")}</span>'
        else:
            workplace_html = ""

        date_html = f'<span class="job-badge job-badge-date">{post_date}</span>' if raw_post_date != "غير محدد" else ""
        eligibility_note = html.escape(str(job.get("eligibility_note", "")))
        eligibility_html = (
            f'<span class="job-badge job-badge-eligibility">⚠ {eligibility_note}</span>'
            if eligibility_note else ""
        )

        card_html = (
            f'<div class="job-card">'
            f'<div class="job-card-main">'
            f'<div class="job-card-header">'
            f'<div class="job-title">{title}</div>'
            f'<div class="job-company">{company}</div>'
            f'</div>'
            f'<div class="job-badges">'
            f'{source_html}'
            f'<span class="job-badge job-badge-loc">{loc}</span>'
            f'{type_html}'
            f'{seniority_html}'
            f'{workplace_html}'
            f'{date_html}'
            f'{eligibility_html}'
            f'</div>'
            f'</div>'
            f'<div class="job-card-action">'
            f'<a href="{html.escape(link, quote=True)}" target="_blank" rel="noopener noreferrer" class="job-apply-btn">'
            f'{btn_text}'
            f'</a>'
            f'</div>'
            f'</div>'
        )
        cards_html.append(card_html)

    full_cards_html = f'<div class="jobs-container">{"".join(cards_html)}</div>'
    st.markdown(full_cards_html, unsafe_allow_html=True)

elif search_attempted:
    st.warning(tr("no_results"))
else:
    st.markdown("""

    """,unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="wasla-footer">
        <span>وصلة | Wasla</span>
        <span>•</span>
        <a href="https://x.com/Prosox0x0" target="_blank" rel="noopener noreferrer">{tr('contact')}</a>
        <span>•</span>
        <span>{tr('forked')} <a href="https://github.com/qenawy1/EMAD" target="_blank" rel="noopener noreferrer">qenawy1/EMAD</a></span>
    </div>
    """,
    unsafe_allow_html=True,
)
