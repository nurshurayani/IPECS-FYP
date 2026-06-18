import streamlit as st
import os
from data.sample_data import DEFAULT_TRANSACTIONS, DEFAULT_BUDGETS, DEFAULT_ALERTS

# MUST be first Streamlit call
st.set_page_config(
    page_title="IPECS - Intelligent Personal Expense Categorization System",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide built-in Streamlit page nav
st.markdown("""
<style>
    section[data-testid="stSidebarNav"] { display: none !important; }
    div[data-testid="stSidebarNavItems"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    .stButton > button {
        background-color: #0F7B6C;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0a5c51;
    }
    [data-testid="stMetric"] {
        background-color: white;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Login gate
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;color:#0F7B6C'>💳 IPECS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#555;'>Intelligent Personal Expense Classification System</p>", unsafe_allow_html=True)
    st.write("")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if username == "amirul" and password == "ipecs2025":
                st.session_state.logged_in = True
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Incorrect username or password")
        st.caption("Demo credentials — Username: amirul | Password: ipecs2025")
    st.stop()

# Initialize session states
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

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "name": "Amirul Syafiq",
        "university": "Universiti Malaysia Sabah",
        "student_id": "BI23100011",
        "age": 21,
        "allowance_range": "RM500-RM1000"
    }

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color:#0F7B6C; margin-bottom:0;'>💳 IPECS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#0a5c51; font-size:9px; text-transform:uppercase; font-family:monospace; margin-top:0;'>Intelligent Personal Expense Classification System</p>", unsafe_allow_html=True)

    st.divider()

    if st.session_state.get("admin_authenticated"):
        st.error("🔐 ADMIN MODE")

    is_bm = (st.session_state.lang == "BM")

    if st.session_state.get("admin_authenticated"):
        user_header = "PENTADBIR" if is_bm else "ADMINISTRATOR"
        admin_name = "Pentadbir Sistem" if is_bm else "System Administrator"
        admin_role = "Admin • Akses Penuh" if is_bm else "Admin • Full Access"
        st.markdown(f"""
        <div style='background-color:white;padding:12px;border-radius:8px;border:1px solid #e0f1ee;margin-bottom:15px;'>
            <p style='color:#0F7B6C;font-size:10px;font-family:monospace;font-weight:bold;margin:0;'>{user_header}</p>
            <p style='margin:3px 0 0 0;font-size:13px;font-weight:bold;color:#333;'>{admin_name}</p>
            <p style='margin:0;font-size:11px;color:#666;'>{admin_role}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        profile = st.session_state.user_profile
        user_header = "PENGGUNA SEMASA" if is_bm else "CURRENT USER"
        st.markdown(f"""
        <div style='background-color:white;padding:12px;border-radius:8px;border:1px solid #e0f1ee;margin-bottom:15px;'>
            <p style='color:#0F7B6C;font-size:10px;font-family:monospace;font-weight:bold;margin:0;'>{user_header}</p>
            <p style='margin:3px 0 0 0;font-size:13px;font-weight:bold;color:#333;'>{profile['name']}</p>
            <p style='margin:0;font-size:11px;color:#666;'>{profile['university']} • {profile['age']} y/o</p>
        </div>
        """, unsafe_allow_html=True)

    account_label = "👤 Akaun Pengguna" if is_bm else "👤 User Account"
    admin_label = "🔐 Panel Admin" if is_bm else "🔐 Admin Panel"
    pages = [
        "🏠 Dashboard",
        "🧾 Receipt & Transaction Entry",
        "🔀 Transaction & Category Management",
        "🎯 Budget Goal Management",
        "📊 Spending Reports",
        "🤖 AI Forecast & Alerts",
        account_label,
        admin_label
    ]

    current_idx = 0
    clean_page_name = st.session_state.page

    if clean_page_name in ["User Account", "Akaun Pengguna"]:
        clean_page_name = "Akaun Pengguna" if is_bm else "User Account"
        st.session_state.page = clean_page_name
    elif clean_page_name in ["Admin Panel", "Panel Admin"]:
        clean_page_name = "Panel Admin" if is_bm else "Admin Panel"
        st.session_state.page = clean_page_name

    for i, p in enumerate(pages):
        if clean_page_name in p:
            current_idx = i
            break

    selected_page_item = st.radio("Navigation", pages, index=current_idx, label_visibility="collapsed")
    st.session_state.page = selected_page_item[2:].strip()

    st.divider()

    bm_active = st.toggle("Bahasa Malaysia (BM)", value=(st.session_state.lang == "BM"))
    st.session_state.lang = "BM" if bm_active else "EN"

    st.divider()

    if st.button("🚪 Log Keluar" if is_bm else "🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Page routing
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
elif st.session_state.page in ["User Account", "Akaun Pengguna"]:
    from pages.account import show_account
    show_account()
elif st.session_state.page in ["Admin Panel", "Panel Admin"]:
    from pages.admin import show_admin
    show_admin()

# Mobile bottom navigation using Streamlit buttons
is_bm = (st.session_state.lang == "BM")
st.markdown("---")
st.markdown(f"<p style='text-align:center;font-size:11px;color:#aaa;'>{'Navigasi Pantas' if is_bm else 'Quick Navigation'}</p>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    if st.button("🏠\nHome" if not is_bm else "🏠\nUtama", use_container_width=True):
        st.session_state.page = "Dashboard"
        st.rerun()
with c2:
    if st.button("🧾\nAdd" if not is_bm else "🧾\nTambah", use_container_width=True):
        st.session_state.page = "Receipt & Transaction Entry"
        st.rerun()
with c3:
    if st.button("🔀\nTxn" if not is_bm else "🔀\nTranx", use_container_width=True):
        st.session_state.page = "Transaction & Category Management"
        st.rerun()
with c4:
    if st.button("🎯\nBudget" if not is_bm else "🎯\nBajet", use_container_width=True):
        st.session_state.page = "Budget Goal Management"
        st.rerun()
with c5:
    if st.button("🤖\nAlerts" if not is_bm else "🤖\nAmaran", use_container_width=True):
        st.session_state.page = "AI Forecast & Alerts"
        st.rerun()