import streamlit as st
import pandas as pd
import plotly.express as px
from decimal import Decimal

def show_dashboard():
    # Translation keys
    lang = st.session_state.lang
    is_bm = (lang == "BM")
    
    # Text definitions
    t_title = "Papan Pemuka" if is_bm else "Dashboard"
    t_spent = "Jumlah Belanja Bulan Ini" if is_bm else "Total Spent This Month (RM)"
    t_remain = "Baki Bajet" if is_bm else "Budget Remaining (RM)"
    t_tx = "Transaksi Minggu Ini" if is_bm else "Transactions This Week"
    t_alerts = "Amaran Aktif" if is_bm else "Active Alerts"
    t_chart1 = "Perbelanjaan mengikut Kategori" if is_bm else "Spending by Category"
    t_chart2 = "Bajet vs Sebenar mengikut Kategori" if is_bm else "Budget vs Actual per Category"
    t_recent = "Transaksi Terkini" if is_bm else "Recent Transactions"
    t_view = "Lihat Semua Transaksi" if is_bm else "View All Transactions"
    t_upload = "📤 Muat Naik Resit" if is_bm else "📤 Upload Receipt"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("IPECS • Intelligent Personal Expense Classification System")
    st.divider()

    txs = st.session_state.transactions
    budgets = st.session_state.budgets
    alerts = st.session_state.alerts

    # 1. Calculations
    total_budget = sum(budgets.values())
    total_spent_this_month = sum(float(tx["amount"]) for tx in txs if tx["date"].startswith("2025-06"))
    budget_remaining = total_budget - total_spent_this_month
    pct_remaining = (budget_remaining / total_budget * 100) if total_budget > 0 else 0

    tx_week_count = len([tx for tx in txs if "2025-06-12" <= tx["date"] <= "2025-06-18"])
    active_alerts_count = len([a for a in alerts if not a["dismissed"]])

    # Row 1 - 4 metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t_spent, f"RM {total_spent_this_month:.2f}")
    with col2:
        delta_color = "normal" if pct_remaining >= 20 else "inverse"
        st.metric(t_remain, f"RM {budget_remaining:.2f}", delta=f"{pct_remaining:.1f}% left", delta_color=delta_color)
    with col3:
        st.metric(t_tx, f"{tx_week_count} txs")
    with col4:
        st.metric(t_alerts, f"{active_alerts_count} active", delta="Check Alerts!" if active_alerts_count > 0 else "Safe", delta_color="inverse" if active_alerts_count > 0 else "normal")

    st.write("")

    # Row 2 - Donut chart and bar comparison
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"<h5>{t_chart1}</h5>", unsafe_allow_html=True)
        # Sum category spending
        cat_sums = {}
        for tx in txs:
            if tx["date"].startswith("2025-06"):
                cat_sums[tx["category"]] = cat_sums.get(tx["category"], 0.0) + float(tx["amount"])
        
        if not cat_sums:
            st.info("No spending recorded yet.")
        else:
            df_cat = pd.DataFrame([{"Category": cat, "Amount": amt} for cat, amt in cat_sums.items()])
            fig = px.pie(df_cat, values='Amount', names='Category', hole=0.5, color_discrete_sequence=['#0F7B6C', '#1EA896', '#32BCA9', '#5CD2C3', '#96E7DC'])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=260)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown(f"<h5>{t_chart2}</h5>", unsafe_allow_html=True)
        # Budget vs Actual Dataframe construction
        bva_list = []
        for cat in budgets:
            actual = cat_sums.get(cat, 0.0)
            limit = budgets[cat]
            pct = (actual / limit * 100) if limit > 0 else 0
            
            # Colour determination
            color = "#10B981" # Green
            if pct >= 100:
                color = "#EF4444" # Red
            elif pct >= 80:
                color = "#F59E0B" # Amber

            bva_list.append({
                "Category": cat,
                "Budget": limit,
                "Actual": actual,
                "percentage": pct,
                "color": color
            })
            
        df_bva = pd.DataFrame(bva_list)
        fig_bar = px.bar(df_bva, x=["Actual", "Budget"], y="Category", barmode='group', orientation='h', color_discrete_sequence=['#0F7B6C', '#cbd5e1'])
        fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=260, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Row 3 - Recent Transactions
    st.markdown(f"<h4>{t_recent}</h4>", unsafe_allow_html=True)
    
    # Show last 5
    sorted_txs = sorted(txs, key=lambda x: x["date"], reverse=True)[:5]
    
    emoji_map = {
        "Food & Dining": "🍔",
        "Transport": "🚗",
        "Shopping": "🛍️",
        "Bills": "💵",
        "Entertainment": "🎬",
        "Other": "📦"
    }

    display_rows = []
    for tx in sorted_txs:
        emo = emoji_map.get(tx["category"], "📦")
        display_rows.append({
            "Date": tx["date"],
            "Merchant": tx["merchant"],
            "Category": f"{emo} {tx['category']}",
            "Amount (RM)": f"RM {float(tx['amount']):.2f}",
            "Source": tx["source"].upper()
        })
        
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True)

    # Floating action trigger
    if st.button(t_upload):
        st.session_state.page = "Receipt & Transaction Entry"
        st.rerun()
