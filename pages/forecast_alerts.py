import streamlit as st
import pandas as pd
from utils.gemini_helper import generate_forecast

def show_forecast_alerts():
    is_bm = (st.session_state.lang == "BM")
    
    t_title = "Ramalan AI & Amaran" if is_bm else "AI Forecast & Alerts"
    t_alerts_h = "🚨 Amaran Anomali" if is_bm else "🚨 Anomaly Alerts"
    t_fc_h = "🤖 Ramalan Perbelanjaan AI" if is_bm else "🤖 AI Spending Forecast"
    t_refresh = "Segarkan Ramalan" if is_bm else "Refresh Forecast"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Investigate odd transaction spikes and load AI prediction caps.")
    st.divider()

    alerts = st.session_state.alerts
    txs = st.session_state.transactions
    budgets = st.session_state.budgets

    # 1. Anomalies lists
    st.markdown(f"#### {t_alerts_h}")
    active_alerts = [a for a in alerts if not a["dismissed"]]

    if not active_alerts:
        st.success("No active anomalies detected this month! 🎉" if not is_bm else "Tiada amaran anomali aktif dikesan bulan ini! 🎉")
    else:
        for idx, alert in enumerate(active_alerts):
            severity = alert["severity"]
            alert_text = f"**{alert['type']}**: Spent RM {alert['amount']:.2f} on *{alert['category']}* on {alert['date']}. (Anomaly warning detail)"
            
            # Draw st.error or st.warning
            if severity == "High":
                with st.container(border=True):
                    st.error(alert_text)
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("Abai" if is_bm else "Dismiss", key=f"dism_{alert['id']}"):
                            # Set dismissed
                            for a in st.session_state.alerts:
                                if a["id"] == alert["id"]:
                                    a["dismissed"] = True
                            st.rerun()
                    with col2:
                        if st.button("Semak" if is_bm else "Review", key=f"rev_{alert['id']}"):
                            st.session_state.page = "Transaction & Category Management"
                            st.rerun()
            else:
                with st.container(border=True):
                    st.warning(alert_text)
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("Abai" if is_bm else "Dismiss", key=f"dism_{alert['id']}"):
                            for a in st.session_state.alerts:
                                if a["id"] == alert["id"]:
                                    a["dismissed"] = True
                            st.rerun()
                    with col2:
                        if st.button("Semak" if is_bm else "Review", key=f"rev_{alert['id']}"):
                            st.session_state.page = "Transaction & Category Management"
                            st.rerun()

    st.divider()

    # 2. AI Forecast Section
    st.markdown(f"#### {t_fc_h}")
    st.caption("Based on your last 90 days of spending patterns" if not is_bm else "Berdasarkan corak perbelanjaan 90 hari terakhir anda")

    if st.button(t_refresh, key="btn_refresh_fc"):
        with st.spinner("Refreshing Gemini AI budget projections..." if not is_bm else "Menyegarkan ramalan belanjawan AI..."):
            # Call helper
            fc_data = generate_forecast(txs, budgets)
            st.session_state.active_fc = fc_data
            st.success("Forecast Model Updated!" if not is_bm else "Ramalan AI berjaya dikemaskini!")

    # Render forecast results if available in session state
    if "active_fc" in st.session_state:
        fc = st.session_state.active_fc
        
        st.write("")
        st.markdown(f"**AI Projected Spend: RM {fc.get('projected_total', 0.0):.2f}**")
        st.metric("Model Confidence Rating", fc.get("confidence", "Medium"))
        
        st.divider()
        st.write("Projected Category Caps For Tomorrow's Outings:")
        
        col_list = st.columns(len(budgets))
        for key_idx, (cat, proj_amt) in enumerate(fc.get("by_category", {}).items()):
            with col_list[key_idx % len(col_list)]:
                bg_limit = budgets.get(cat, 0.0)
                st.metric(label=cat, value=f"RM {proj_amt:.0f}", delta=f"Budget: RM {bg_limit:.0f}", delta_color="normal")
                
        st.info(f"💡 **AI Suggestion**: {fc.get('tip', '')}")
    else:
        st.info("Click 'Refresh Forecast' to query Gemini and unlock multi-category outlook charts." if not is_bm else "Klik 'Segarkan Ramalan' untuk membolehkan model AI memproses had perbelanjaan.")
