import streamlit as st
import pandas as pd
import plotly.express as px

def show_budget():
    is_bm = (st.session_state.lang == "BM")
    
    t_title = "Pengurusan Matlamat Bajet" if is_bm else "Budget Goal Management"
    t_track = "✅ Bersesuaian Jangkaan" if is_bm else "✅ On Track"
    t_risk = "⚠️ Berisiko Lebihan" if is_bm else "⚠️ At Risk"
    t_over = "🔴 Melebihi Bajet" if is_bm else "🔴 Over Budget"
    t_limit = "Had Bajet" if is_bm else "Budget Limit"
    t_spent = "Jumlah Dibelanjakan" if is_bm else "Amount Spent"
    t_remain = "Baki Sisa" if is_bm else "Remaining"
    t_save = "Simpan Semua Bajet" if is_bm else "Save All Budgets"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Custom allocations and spend alerts across default targets.")
    st.divider()

    txs = st.session_state.transactions
    budgets = st.session_state.budgets

    # Tab 1: Current Month / Tab 2: History
    tabs = st.tabs(["Current Month" if not is_bm else "Bulan Semasa", "History" if not is_bm else "Sejarah"])

    # 1. Calculations
    total_budget = sum(budgets.values())
    total_spent_this_month = sum(float(tx["amount"]) for tx in txs if tx["date"].startswith("2025-06"))
    budget_usage = (total_spent_this_month / total_budget * 100) if total_budget > 0 else 0

    cat_sums = {}
    for tx in txs:
        if tx["date"].startswith("2025-06"):
            cat_sums[tx["category"]] = cat_sums.get(tx["category"], 0.0) + float(tx["amount"])

    with tabs[0]:
        # Overall Card
        st.subheader("Monthly Progress" if not is_bm else "Perkembangan Bulanan")
        
        # Track Status
        status_label = t_track
        if budget_usage >= 100:
            status_label = t_over
        elif budget_usage >= 80:
            status_label = t_risk

        st.markdown(f"""
        <div style='background-color: #f8fffe; border: 1px solid #b4e2da; border-radius: 12px; padding: 20px; margin-bottom: 25px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <h5 style='margin:0; color:#333;'>OVERALL ALLOCATION</h5>
                    <p style='font-size:18px; font-weight:bold; margin: 5px 0 0 0; color:#0F7B6C;'>Spent RM {total_spent_this_month:.2f} of RM {total_budget:.2f}</p>
                </div>
                <div style='font-size: 14px; font-weight:bold; padding: 6px 16px; border-radius: 20px; background-color: white; border: 20px;'>
                    {status_label}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(budget_usage / 100.0, 1.0))
        st.write("")

        # Per category inputs cols
        st.markdown(f"#### Edit Limits" if not is_bm else "#### Had Kemasukan")
        
        # Form to submit bulk updates
        with st.form("budget_limits_form"):
            new_limits = {}
            for cat, limit in budgets.items():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 3])
                
                spent = cat_sums.get(cat, 0.0)
                remaining = limit - spent
                ratio = (spent / limit) if limit > 0 else 0
                
                with col1:
                    st.markdown(f"**{cat}**")
                with col2:
                    new_val = st.number_input(f"RM Limit for {cat}", value=float(limit), label_visibility="collapsed", key=f"input_{cat}")
                    new_limits[cat] = float(new_val)
                with col3:
                    st.write(f"Spent: RM {spent:.2f}")
                with col4:
                    st.write(f"Baki: RM {remaining:.2f}")
                with col5:
                    st.progress(min(ratio, 1.0))
                    
            if st.form_submit_button(f"💾 {t_save}"):
                st.session_state.budgets = new_limits
                st.success("Budgets updated successfully!" if not is_bm else "Bajet berjaya disimpan!")
                st.rerun()

    with tabs[1]:
        st.subheader("Historical Spends Comparing Budgets" if not is_bm else "Sejarah Belanja Berbanding Bajet")
        
        # Construct Dummy Multi-month Grouped dataframe
        history_list = []
        for cat, limit in budgets.items():
            jun_spent = cat_sums.get(cat, 0.0)
            
            # Simulated history
            history_list.append({"Category": cat, "Period": "June Actual", "Spend (RM)": jun_spent})
            history_list.append({"Category": cat, "Period": "May Actual", "Spend (RM)": limit * 0.95})
            history_list.append({"Category": cat, "Period": "April Actual", "Spend (RM)": limit * 0.85})
            history_list.append({"Category": cat, "Period": "Monthly Limit", "Spend (RM)": limit})
            
        df_hist = pd.DataFrame(history_list)
        fig = px.bar(df_hist, x="Category", y="Spend (RM)", color="Period", barmode="group", color_discrete_sequence=['#2dd4bf', '#fca5a5', '#93c5fd', '#cbd5e1'])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
