import streamlit as st
import os
from data.sample_data import DEFAULT_TRANSACTIONS, DEFAULT_BUDGETS, DEFAULT_ALERTS

# Set page config
st.set_page_config(
    page_title="IPECS - Intelligent Personal Expense Classification System",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS brand styling as requested
st.markdown("""
<style>
    /* Brand colour: teal #0F7B6C */
    .stButton > button {
        background-color: #0F7B6C;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0a5c51;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fffe;
    }
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 1. Initialize session_states
if "transactions" not in st.session_state:
    st.session_state.transactions = DEFAULT_TRANSACTIONS.copy()

if "budgets" not in st.session_state:
    st.session_state.budgets = DEFAULT_BUDGETS.copy()

if "alerts" not in st.session_state:
    st.session_state.alerts = DEFAULT_ALERTS.copy()

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# 2. Sidebar Layout
with st.sidebar:
    st.markdown("<h2 style='color:#0F7B6C; margin-bottom:0;'>💳 IPECS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#0a5c51; font-size:11px; text-transform:uppercase; font-family:monospace; margin-top:0;'>Intelligent Expense</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # User profile
    st.markdown("""
    <div style='background-color: white; padding: 12px; border-radius: 8px; border: 1px solid #e0f1ee; margin-bottom: 15px;'>
        <p style='color: #0F7B6C; font-size: 10px; font-family: monospace; font-weight: bold; margin: 0;'>CURRENT USER</p>
        <p style='margin: 3px 0 0 0; font-size: 13px; font-weight: bold; color: #333;'>Amirul Syafiq</p>
        <p style='margin: 0; font-size: 11px; color: #666;'>UM Student • 21 y/o</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation options
    pages = [
        "🏠 Dashboard",
        "🧾 Receipt & Transaction Entry",
        "🔀 Transaction & Category Management",
        "🎯 Budget Goal Management",
        "📊 Spending Reports",
        "🤖 AI Forecast & Alerts"
    ]
    
    # Pre-select matching page selection
    current_idx = 0
    clean_page_name = st.session_state.page
    for i, p in enumerate(pages):
        if clean_page_name in p:
            current_idx = i
            break
            
    selected_page_item = st.radio("Navigation", pages, index=current_idx, label_visibility="collapsed")
    st.session_state.page = selected_page_item[2:].strip()

    st.divider()
    
    # Language Toggle
    bm_active = st.toggle("Bahasa Malaysia (BM)", value=(st.session_state.lang == "BM"))
    st.session_state.lang = "BM" if bm_active else "EN"

# 3. Pages Route Handlers
if st.session_state.page == "Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard()
elif st.session_state.page == "Receipt & Transaction Entry":
    from pages.receipt_entry import show_receipt_entry
    show_receipt_entry()
elif st.session_state.page == "Transaction & Category Management":
    from pages.transactions import show_transactions
    show_transactions()
elif st.session_state.page == "Budget Goal Management":
    from pages.budget import show_budget
    show_budget()
elif st.session_state.page == "Spending Reports":
    from pages.reports import show_reports
    show_reports()
elif st.session_state.page == "AI Forecast & Alerts":
    from pages.forecast_alerts import show_forecast_alerts
    show_forecast_alerts()
