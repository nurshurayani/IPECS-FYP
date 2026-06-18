import streamlit as st
import pandas as pd

# Scroll to top JavaScript check at first line
st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)

def get_initials(name):
    if not name:
        return "AS"
    parts = name.strip().split()
    if not parts:
        return "AS"
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][:2].upper()

def show_account():
    is_bm = (st.session_state.lang == "BM")
    
    # 1. Page Header
    t_title = "Akaun Pengguna" if is_bm else "User Account"
    st.markdown(f"<h2>👤 {t_title}</h2>", unsafe_allow_html=True)
    st.caption("Manage your profile settings, app preferences, budgets, and application data." if not is_bm else "Urus tetapan profil anda, pilihan aplikasi, bajet, dan data aplikasi.")
    st.divider()

    # Get User Profile from Session State or fallback to default
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "name": "Amirul Syafiq",
            "university": "Universiti Malaysia Sabah",
            "student_id": "BI23100011",
            "age": 21,
            "allowance_range": "RM500-RM1000"
        }
    
    profile = st.session_state.user_profile
    initials = get_initials(profile.get("name", "Amirul Syafiq"))

    # 1. PROFILE SECTION
    avatar_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; width: 100%; margin-top: 10px; margin-bottom: 20px;">
        <div style="
            background-color: #0F7B6C;
            color: white;
            font-weight: bold;
            font-size: 32px;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        ">
            {initials}
        </div>
        <h3 style="margin: 5px 0 0 0; color: #333; font-size: 24px; text-align: center;">{profile['name']}</h3>
        <p style="margin: 5px 0; color: #666; font-size: 16px; text-align: center;">🎓 {profile['university']}</p>
        <p style="margin: 2px 0 10px 0; color: #888; font-size: 14px; text-align: center;">
            <strong>Student ID / ID Pelajar:</strong> {profile['student_id']} &nbsp;|&nbsp; <strong>Age / Umur:</strong> {profile['age']}
        </p>
        <span style="background-color: #e0f1ee; color: #0F7B6C; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: bold;">
            Allowance: {profile.get('allowance_range', 'RM500-RM1000')}
        </span>
    </div>
    """
    st.markdown(avatar_html, unsafe_allow_html=True)

    # Edit profile toggle state logic
    if "edit_profile_mode" not in st.session_state:
        st.session_state.edit_profile_mode = False

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        edit_btn_label = "📝 Close Edit Form" if st.session_state.edit_profile_mode else "📝 Edit Profile"
        if is_bm:
            edit_btn_label = "📝 Tutup Borang Edit" if st.session_state.edit_profile_mode else "📝 Edit Profil"
            
        if st.button(edit_btn_label, use_container_width=True, key="toggle_edit_profile"):
            st.session_state.edit_profile_mode = not st.session_state.edit_profile_mode
            st.rerun()

    if st.session_state.edit_profile_mode:
        st.write("")
        with st.form("edit_profile_form", clear_on_submit=False):
            st.write("### " + ("Edit Profile Details" if not is_bm else "Edit Maklumat Profil"))
            
            new_name = st.text_input("Full Name" if not is_bm else "Nama Penuh", value=profile["name"])
            new_univ = st.text_input("University/Institution" if not is_bm else "Universiti/Institusi", value=profile["university"])
            new_sid = st.text_input("Student ID" if not is_bm else "ID Pelajar", value=profile["student_id"])
            new_age = st.number_input("Age" if not is_bm else "Umur", min_value=16, max_value=60, value=int(profile["age"]))
            
            allowance_options = ["Below RM500", "RM500-RM1000", "RM1000-RM2000", "Above RM2000"]
            current_range = profile.get("allowance_range", "RM500-RM1000")
            if current_range not in allowance_options:
                allowance_options.insert(0, current_range)
            
            new_range = st.selectbox(
                "Monthly Income/Allowance Range" if not is_bm else "Julat Pendapatan/Elaun Bulanan",
                options=allowance_options,
                index=allowance_options.index(current_range)
            )
            
            if st.form_submit_button("Save Changes" if not is_bm else "Simpan Perubahan"):
                st.session_state.user_profile = {
                    "name": new_name,
                    "university": new_univ,
                    "student_id": new_sid,
                    "age": new_age,
                    "allowance_range": new_range
                }
                st.session_state.edit_profile_mode = False
                st.success("Profile updated!" if not is_bm else "Profil dikemas kini!")
                st.rerun()

    st.subheader("")
    st.divider()

    # 2. APP PREFERENCES SECTION
    with st.expander("⚙️ App Preferences" if not is_bm else "⚙️ Pilihan Aplikasi", expanded=False):
        st.write("### " + ("Preferences" if not is_bm else "Pilihan"))
        
        current_lang_idx = 0 if st.session_state.lang == "EN" else 1
        lang_pref = st.radio(
            "Language Preference" if not is_bm else "Pilihan Bahasa",
            options=["EN", "BM"],
            index=current_lang_idx,
            horizontal=True
        )

        currency_pref = st.selectbox(
            "Currency Display" if not is_bm else "Paparan Mata Wang",
            options=["RM (Ringgit Malaysia)"],
            index=0
        )

        # Sync Landing Page Selection
        if "default_landing" not in st.session_state:
            st.session_state.default_landing = "Dashboard"

        landing_options = ["Dashboard", "Transaction & Category Management", "Spending Reports"]
        landing_labels = {
            "Dashboard": "Dashboard" if not is_bm else "Skrin Utama / Papan Pemuka",
            "Transaction & Category Management": "Transactions / Transaksi" if not is_bm else "Transaksi & Pengurusan Kategori",
            "Spending Reports": "Reports / Laporan" if not is_bm else "Laporan Perbelanjaan"
        }

        landing_pref = st.selectbox(
            "Default Landing Page" if not is_bm else "Halaman Utama Lalai",
            options=landing_options,
            format_func=lambda x: landing_labels[x],
            index=landing_options.index(st.session_state.get("default_landing", "Dashboard"))
        )

        if st.button("Save Preferences" if not is_bm else "Simpan Pilihan", key="save_pref_btn"):
            st.session_state.lang = lang_pref
            st.session_state.default_landing = landing_pref
            st.success("Preferences saved successfully!" if not is_bm else "Pilihan berjaya disimpan!")
            st.rerun()

    # 3. BUDGET SUMMARY SECTION
    with st.expander("💰 My Budget Overview" if not is_bm else "💰 Gambaran Keseluruhan Bajet Saya", expanded=False):
        st.write("### " + ("Current Budget Allocations" if not is_bm else "Peruntukan Bajet Semasa"))
        
        budgets = st.session_state.get("budgets", {})
        if not budgets:
            st.info("No budgets defined yet. Go to Budget goal settings to add." if not is_bm else "Tiada bajet ditetapkan lagi. Sila klik butang di bawah.")
        else:
            cols = st.columns(3)
            total_budget = 0.0
            for i, (category, limit) in enumerate(budgets.items()):
                total_budget += float(limit)
                col_idx = i % 3
                with cols[col_idx]:
                    st.metric(label=category, value=f"RM {limit:,.2f}")
            
            st.write("")
            st.markdown(f"**Total Monthly Budget / Jumlah Keseluruhan Bajet:** `RM {total_budget:,.2f}`")
            
        st.write("")
        if st.button("Go to Budget Settings" if not is_bm else "Pergi ke Tetapan Bajet", key="go_to_budget_btn", use_container_width=True):
            st.session_state.page = "Budget Goal Management"
            st.rerun()

    # 4. DATA MANAGEMENT SECTION
    with st.expander("🗂️ Data Management" if not is_bm else "🗂️ Pengurusan Data", expanded=False):
        st.write("### " + ("Export Data" if not is_bm else "Eksport Data"))
        transactions_list = st.session_state.get("transactions", [])
        if transactions_list:
            df = pd.DataFrame(transactions_list)
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Export All Transactions (CSV)" if not is_bm else "Eksport Semua Transaksi (CSV)",
                data=csv_data,
                file_name="ipecs_transactions.csv",
                mime="text/csv",
                key="download_csv_btn"
            )
        else:
            st.info("No transactions available to export." if not is_bm else "Tiada transaksi untuk dieksport.")
            
        st.write("")
        st.subheader("")
        st.write("### " + ("Danger Zone" if not is_bm else "Zon Bahaya"))
        
        # Confirmation flag for clearing transactions
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False
            
        if not st.session_state.confirm_clear:
            if st.button("⚠️ Clear All Transactions" if not is_bm else "⚠️ Padam Semua Transaksi", key="clear_all_btn", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()
        else:
            st.warning("Are you absolutely sure you want to clear all transactions? This action is irreversible." if not is_bm else "Adakah anda pasti mahu memadam semua transaksi? Tindakan ini tidak boleh ditarik balik.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, Clear Everything" if not is_bm else "Ya, Padam Semua", key="confirm_clear_yes", use_container_width=True):
                    st.session_state.transactions = []
                    st.session_state.confirm_clear = False
                    st.success("All transactions cleared successfully!" if not is_bm else "Semua transaksi telah berjaya dipadam!")
                    st.rerun()
            with c2:
                if st.button("Cancel" if not is_bm else "Batal", key="confirm_clear_no", use_container_width=True):
                    st.session_state.confirm_clear = False
                    st.rerun()
                    
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        if st.button("Reset to Sample Data" if not is_bm else "Set Semula ke Data Contoh", key="reset_sample_btn", use_container_width=True):
            from data.sample_data import DEFAULT_TRANSACTIONS, DEFAULT_BUDGETS
            st.session_state.transactions = DEFAULT_TRANSACTIONS.copy()
            st.session_state.budgets = DEFAULT_BUDGETS.copy()
            st.success("Successfully reset data to original developer samples." if not is_bm else "Berjaya menetapkan semula ke data contoh pembangun.")
            st.rerun()

    # 5. ABOUT SECTION
    with st.expander("ℹ️ About IPECS" if not is_bm else "ℹ️ Mengenai IPECS", expanded=False):
        st.markdown(f"""
        **App Name / Nama Aplikasi:** IPECS — Intelligent Personal Expense Classification System  
        **Version / Versi:** 1.0.0  
        **Developed by / Dibangunkan oleh:** Nurshurayani  
        **Institution / Institusi:** Universiti Malaysia Sabah  
        **FYP Project / Projek FYP:** KD34603  
        **Powered by / Dikuasakan oleh:** Streamlit + Gemini AI
        """)

    # 6. LOGOUT BUTTON
    st.divider()
    st.write("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Styled Red outlined logout button
        st.markdown("""
        <style>
        div.element-container:has(button[key="logout_btn"]) button {
            background-color: transparent !important;
            color: #d9534f !important;
            border: 2px solid #d9534f !important;
        }
        div.element-container:has(button[key="logout_btn"]) button:hover {
            background-color: #d9534f !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout" if not is_bm else "🚪 Log Keluar", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.success("Logged out successfully!" if not is_bm else "Berjaya log keluar!")
            st.rerun()
