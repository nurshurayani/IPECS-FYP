import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def show_reports():
    is_bm = (st.session_state.lang == "BM")
    
    t_title = "Laporan Perbelanjaan" if is_bm else "Spending Reports"
    t_download = "Muat Turun Laporan (CSV)" if is_bm else "Download Report (CSV)"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Review historical analytics and download full offline spreadsheet records.")
    st.divider()

    txs = st.session_state.transactions

    # Period radio
    st.markdown("**Select report timeframe**")
    p_opt = ["This Month (June)", "Last Month (May)", "Last 3 Months", "Custom Range"]
    period_sel = st.radio("Select Period", p_opt, label_visibility="collapsed", horizontal=True)

    # Date range evaluations
    if "Custom" in period_sel:
        col_s, col_e = st.columns(2)
        with col_s:
            s_dt = st.date_input("Report Start Date", value=datetime.strptime("2025-06-01", "%Y-%m-%d").date())
        with col_e:
            e_dt = st.date_input("Report End Date", value=datetime.strptime("2025-06-18", "%Y-%m-%d").date())
    elif "This Month" in period_sel:
        s_dt, e_dt = datetime.strptime("2025-06-01", "%Y-%m-%d").date(), datetime.strptime("2025-06-30", "%Y-%m-%d").date()
    elif "Last Month" in period_sel:
        s_dt, e_dt = datetime.strptime("2025-05-01", "%Y-%m-%d").date(), datetime.strptime("2025-05-31", "%Y-%m-%d").date()
    else:
        s_dt, e_dt = datetime.strptime("2025-04-01", "%Y-%m-%d").date(), datetime.strptime("2025-06-30", "%Y-%m-%d").date()

    # Filtered DF
    df = pd.DataFrame(txs)
    if df.empty:
        st.info("No logs added.")
        return
        
    df["date_parsed"] = pd.to_datetime(df["date"]).dt.date
    filtered_df = df[(df["date_parsed"] >= s_dt) & (df["date_parsed"] <= e_dt)]

    if filtered_df.empty:
        st.info("No transaction values on selected timeframe.")
        return

    # Calculations
    total_spent = filtered_df["amount"].sum()
    
    # Highest category
    cat_sums = filtered_df.groupby("category")["amount"].sum()
    highest_cat = cat_sums.idxmax() if not cat_sums.empty else "-"
    
    # Most frequent merchant
    march_counts = filtered_df["merchant"].value_counts()
    modal_merchant = march_counts.idxmax() if not march_counts.empty else "-"
    
    # Average Daily spend
    unique_days = len(filtered_df["date_parsed"].unique())
    avg_daily = total_spent / (unique_days if unique_days > 0 else 1)

    # Summary row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Spent", f"RM {total_spent:.2f}")
    with c2:
        st.metric("Highest Category", highest_cat)
    with c3:
        st.metric("Most Frequent Merchant", modal_merchant)
    with c4:
        st.metric("Avg Daily Spend", f"RM {avg_daily:.2f}")

    st.write("")

    # Line Chart: Spend over period
    st.markdown("##### Daily Spending Trend")
    daily_sums = filtered_df.groupby("date")["amount"].sum().reset_index()
    fig_line = px.line(daily_sums, x="date", y="amount", title="Total Spent Daily (RM)", color_discrete_sequence=['#0F7B6C'])
    fig_line.update_layout(height=240, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_line, use_container_width=True)

    # Pies & Bars
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("##### Category Breakdown")
        df_cat = cat_sums.reset_index()
        fig_bar = px.bar(df_cat, x="category", y="amount", color_discrete_sequence=['#0F7B6C'])
        fig_bar.update_layout(height=240, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_r:
        st.markdown("##### Spent % Percentage")
        fig_p = px.pie(df_cat, values="amount", names="category", color_discrete_sequence=['#0F7B6C', '#1EA896', '#32BCA9', '#5CD2C3', '#cbd5e1'])
        fig_p.update_layout(height=240, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_p, use_container_width=True)

    # Breakdown Tables Details
    st.subheader("Analytics Breakdowns")
    df_cat_stats = filtered_df.groupby("category").agg(
        total_spend=("amount", "sum"),
        tx_count=("amount", "count"),
        avg_spend=("amount", "mean")
    ).reset_index()
    
    st.markdown("**Category Breakdown Details**")
    st.dataframe(df_cat_stats, use_container_width=True)

    # Export
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 {t_download}",
        data=csv,
        file_name=f"ipecs_report_{s_dt}_to_{e_dt}.csv",
        mime='text/csv'
    )
