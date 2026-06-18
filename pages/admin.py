import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# 1. Scroll to top JavaScript check at first line
st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)

def show_admin():
    is_bm = (st.session_state.lang == "BM")
    
    # Check authentication state
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        
    # --- PASSWORD GATE ---
    if not st.session_state.admin_authenticated:
        # Centered beautiful login card
        st.write("")
        st.write("")
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("""
            <div style='text-align: center; margin-bottom: 25px;'>
                <h1 style='color: #B91C1C; margin-bottom: 5px;'>🔐 Panel Pentadbir</h1>
                <p style='color: #666; font-size: 14px;'>IPECS System Administration Portal</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("admin_login_form"):
                st.write("##### " + ("Admin Log In" if not is_bm else "Log Masuk Pentadbir"))
                passwd = st.text_input("Admin Password" if not is_bm else "Kata Laluan Pentadbir", type="password")
                
                btn_login_label = "Login as Admin" if not is_bm else "Log Masuk Pentadbir"
                submit_login = st.form_submit_button(btn_login_label)
                
                if submit_login:
                    if passwd == "admin123":
                        st.session_state.admin_authenticated = True
                        st.success("Successfully authenticated!" if not is_bm else "Pengesahan berjaya!")
                        st.rerun()
                    else:
                        st.error("Incorrect password / Kata laluan salah.")
            
            # Subtle hint for development review convenience
            st.caption("Password hint: `admin123`")
        return

    # --- ADMIN ACCESS GRANTED ---
    
    # Authenticated Layout Header with dark red accent
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("""
        <div style='border-left: 5px solid #B91C1C; padding-left: 15px; margin-bottom: 10px;'>
            <h1 style='color: #B91C1C; margin: 0;'>🔐 System Admin Portal</h1>
            <p style='color: #666; margin: 5px 0 0 0;'>Monitor database statistics, oversee transactions, moderate users, and customize expense taxonomy.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        # Logout Admin button styled with red outline
        st.markdown("""
        <style>
        div.element-container:has(button[key="admin_logout_btn"]) button {
            background-color: transparent !important;
            color: #B91C1C !important;
            border: 2px solid #B91C1C !important;
        }
        div.element-container:has(button[key="admin_logout_btn"]) button:hover {
            background-color: #B91C1C !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout Admin" if not is_bm else "🚪 Log Keluar Admin", key="admin_logout_btn", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.success("Admin Session Closed" if not is_bm else "Sesi Pentadbir Ditutup")
            st.rerun()

    st.divider()

    # --- INITIALIZE ADMIN POOLED RESOURCES IN SESSION STATE ---
    if "admin_users" not in st.session_state:
        st.session_state.admin_users = pd.DataFrame([
            {"User ID": "U1001", "Name": "Amirul Syafiq", "Institution": "Universiti Malaysia Sabah", "Age": 21, "Plan": "Pro", "Active": True, "Registered Date": "2025-01-10", "Total Transactions": 15},
            {"User ID": "U1002", "Name": "Siti Aminah", "Institution": "Universiti Malaya", "Age": 22, "Plan": "Free", "Active": True, "Registered Date": "2025-02-14", "Total Transactions": 8},
            {"User ID": "U1003", "Name": "Teoh Wei Jie", "Institution": "Universiti Sains Malaysia", "Age": 20, "Plan": "Pro", "Active": False, "Registered Date": "2025-03-05", "Total Transactions": 24},
            {"User ID": "U1004", "Name": "Arun Kumar", "Institution": "Universiti Teknologi Malaysia", "Age": 23, "Plan": "Free", "Active": True, "Registered Date": "2025-04-18", "Total Transactions": 12},
            {"User ID": "U1005", "Name": "Nurul Izzah", "Institution": "Universiti Malaysia Sarawak", "Age": 21, "Plan": "Pro", "Active": True, "Registered Date": "2025-05-22", "Total Transactions": 3},
        ])

    if "admin_categories" not in st.session_state:
        st.session_state.admin_categories = [
            {"Category Name": "Food & Dining", "Colour": "#FFA07A", "Default": True, "Active": True},
            {"Category Name": "Transport", "Colour": "#87CEFA", "Default": True, "Active": True},
            {"Category Name": "Shopping", "Colour": "#DA70D6", "Default": True, "Active": True},
            {"Category Name": "Bills", "Colour": "#FFD700", "Default": True, "Active": True},
            {"Category Name": "Entertainment", "Colour": "#ADFF2F", "Default": True, "Active": True},
            {"Category Name": "Other", "Colour": "#D3D3D3", "Default": True, "Active": True},
        ]

    if "admin_simulated_transactions" not in st.session_state:
        st.session_state.admin_simulated_transactions = [
            {"id": "TXN-2025-001", "user": "Siti Aminah", "merchant": "RapidKL LRT", "category": "Transport", "amount": 4.50, "date": "2025-06-02", "source": "manual", "flagged": False},
            {"id": "TXN-2025-002", "user": "Siti Aminah", "merchant": "Guardian Pharmacy", "category": "Shopping", "amount": 42.10, "date": "2025-06-03", "source": "ocr", "flagged": False},
            {"id": "TXN-2025-003", "user": "Siti Aminah", "merchant": "Mamak Corner", "category": "Food & Dining", "amount": 15.60, "date": "2025-06-05", "source": "manual", "flagged": False},
            {"id": "TXN-2025-004", "user": "Teoh Wei Jie", "merchant": "Steam Games Store", "category": "Entertainment", "amount": 120.00, "date": "2025-06-01", "source": "manual", "flagged": True},
            {"id": "TXN-2025-005", "user": "Teoh Wei Jie", "merchant": "Grab Food", "category": "Food & Dining", "amount": 34.50, "date": "2025-06-04", "source": "ocr", "flagged": False},
            {"id": "TXN-2025-006", "user": "Teoh Wei Jie", "merchant": "Digi Telecommunications", "category": "Bills", "amount": 50.00, "date": "2025-06-06", "source": "manual", "flagged": False},
            {"id": "TXN-2025-007", "user": "Arun Kumar", "merchant": "Shell Petrol", "category": "Transport", "amount": 40.00, "date": "2025-06-08", "source": "manual", "flagged": False},
            {"id": "TXN-2025-008", "user": "Arun Kumar", "merchant": "Giant Hypermarket", "category": "Shopping", "amount": 115.30, "date": "2025-06-11", "source": "ocr", "flagged": False},
            {"id": "TXN-2025-009", "user": "Arun Kumar", "merchant": "Kopi Kebun", "category": "Food & Dining", "amount": 18.00, "date": "2025-06-12", "source": "manual", "flagged": False},
            {"id": "TXN-2025-010", "user": "Nurul Izzah", "merchant": "Nasi Kandar Pelita", "category": "Food & Dining", "amount": 12.80, "date": "2025-06-14", "source": "ocr", "flagged": False},
        ]


    # 4 TABS NAVIGATION AREA
    tab_labels = [
        "👥 User Management" if not is_bm else "👥 Pengurusan Pengguna",
        "📊 System Overview" if not is_bm else "📊 Gambaran Sistem",
        "🗂️ Category Management" if not is_bm else "🗂️ Pengurusan Kategori",
        "📋 Transaction Oversight" if not is_bm else "📋 Pemantauan Transaksi"
    ]
    
    t1, t2, t3, t4 = st.tabs(tab_labels)

    # -------------------------------------------------------------
    # TAB 1 - USER MANAGEMENT
    # -------------------------------------------------------------
    with t1:
        st.write("### " + ("User Accounts" if not is_bm else "Akaun Pengguna"))
        
        # Upper KPI panel
        col_u1, col_u2 = st.columns([1, 3])
        with col_u1:
            st.metric(
                label="Registered Users" if not is_bm else "Jumlah Pengguna",
                value=len(st.session_state.admin_users)
            )
            
        with col_u2:
            search_u_q = st.text_input(
                "🔍 Search User by Name" if not is_bm else "🔍 Cari Pengguna Mengikut Nama",
                placeholder="e.g. Amirul",
                key="admin_user_search_query"
            )
            
        # Compile final list
        df_users = st.session_state.admin_users.copy()
        
        # Dynamic active user sync
        # Read current user stats dynamically
        current_tx_cnt = len(st.session_state.get("transactions", []))
        df_users.loc[df_users["User ID"] == "U1001", "Total Transactions"] = current_tx_cnt
        
        if search_u_q:
            df_users_filtered = df_users[df_users["Name"].str.contains(search_u_q, case=False)]
        else:
            df_users_filtered = df_users
            
        st.markdown(f"<p style='font-size:12px; color:#666;'><i>" + 
                    ("Double-click checkbox to toggle user activity status. Changes are saved instantly." if not is_bm else "Klik dua kali pada kotak semak untuk menukar status ahli. Perubahan disimpan terus.") +
                    "</i></p>", unsafe_allow_html=True)
                    
        edited_df_users = st.data_editor(
            df_users_filtered,
            column_config={
                "Active": st.column_config.CheckboxColumn(
                    "Status (Active/Inactive)" if not is_bm else "Status (Aktif/Tidak Aktif)",
                    help="Toggle the active status of this user" if not is_bm else "Tukar status keaktifan pengguna ini",
                    default=True
                )
            },
            disabled=["User ID", "Name", "Institution", "Age", "Plan", "Registered Date", "Total Transactions"],
            use_container_width=True,
            key="user_management_grid"
        )
        
        # Sync changes back to st.session_state.admin_users
        for idx, row in edited_df_users.iterrows():
            uid = row["User ID"]
            st.session_state.admin_users.loc[st.session_state.admin_users["User ID"] == uid, "Active"] = row["Active"]


    # -------------------------------------------------------------
    # TAB 2 - SYSTEM OVERVIEW
    # -------------------------------------------------------------
    with t2:
        st.write("### " + ("Core Server & Telemetry Data" if not is_bm else "Data Pelayan & Metrik Utama"))
        
        # 1. Metric Calculations
        total_registered_users = len(st.session_state.admin_users)
        
        sim_user_tx_sum = int(st.session_state.admin_users[df_users["User ID"] != "U1001"]["Total Transactions"].sum())
        current_user_tx_sum = len(st.session_state.get("transactions", []))
        total_transactions_db = sim_user_tx_sum + current_user_tx_sum
        
        current_user_ocr_cnt = sum(1 for tx in st.session_state.get("transactions", []) if tx.get("source") == "ocr")
        simulated_ocr_cnt = sum(1 for tx in st.session_state.admin_simulated_transactions if tx.get("source") == "ocr")
        total_receipts_uploaded = current_user_ocr_cnt + simulated_ocr_cnt
        
        current_alerts_count = sum(1 for a in st.session_state.get("alerts", []) if not a.get("dismissed", False))
        simulated_alerts_count = 3  # baseline simulated anomalies
        active_anomaly_alerts = current_alerts_count + simulated_alerts_count
        
        # Plot KPI Row
        kp1, kp2, kp3, kp4 = st.columns(4)
        with kp1:
            st.metric(label="Total Users" if not is_bm else "Jumlah Pengguna", value=total_registered_users)
        with kp2:
            st.metric(label="Database Transactions" if not is_bm else "Jumlah Transaksi", value=total_transactions_db)
        with kp3:
            st.metric(label="Receipts OCR Uploaded" if not is_bm else "Resit OCR Dimuatnaik", value=total_receipts_uploaded)
        with kp4:
            st.metric(label="Active Anomaly Alerts" if not is_bm else "Amaran Anomali Aktif", value=active_anomaly_alerts)
            
        st.write("")
        
        # 2. Charts Layout
        ch1, ch2 = st.columns(2)
        with ch1:
            # Transactions per category cross overview
            cat_counts = {}
            for t in st.session_state.get("transactions", []):
                c = t.get("category", "Other")
                cat_counts[c] = cat_counts.get(c, 0) + 1
                
            categories_base_data = {
                "Category": ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"],
                "Transactions": [
                    24 + cat_counts.get("Food & Dining", 0),
                    12 + cat_counts.get("Transport", 0),
                    18 + cat_counts.get("Shopping", 0),
                    8 + cat_counts.get("Bills", 0),
                    11 + cat_counts.get("Entertainment", 0),
                    4 + cat_counts.get("Other", 0)
                ]
            }
            df_cat = pd.DataFrame(categories_base_data)
            fig_bar = px.bar(
                df_cat,
                x="Category",
                y="Transactions",
                labels={"Transactions": "Volume" if not is_bm else "Isipadu", "Category": "Category" if not is_bm else "Kategori"},
                color_discrete_sequence=["#0F7B6C"],
                title="System Transactions per Category" if not is_bm else "Transaksi Sistem mengikut Kategori"
            )
            fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with ch2:
            # Daily system Volume line chart (June 2025)
            dates_list = [f"2025-06-{str(day).zfill(2)}" for day in range(1, 19)]
            daily_base_volume = [14, 16, 9, 13, 18, 12, 11, 15, 23, 14, 10, 16, 22, 15, 14, 19, 13, 16]
            
            user_daily_tx = {}
            for t in st.session_state.get("transactions", []):
                t_date = t.get("date", "")
                user_daily_tx[t_date] = user_daily_tx.get(t_date, 0) + 1
                
            daily_records = []
            for idx, date_str in enumerate(dates_list):
                vol_combined = daily_base_volume[idx] + user_daily_tx.get(date_str, 0)
                daily_records.append({"Date": date_str, "Volume": vol_combined})
                
            df_daily = pd.DataFrame(daily_records)
            fig_line = px.line(
                df_daily,
                x="Date",
                y="Volume",
                labels={"Volume": "Transaction Volume" if not is_bm else "Isipadu Transaksi", "Date": "Date" if not is_bm else "Tarikh"},
                color_discrete_sequence=["#B91C1C"],
                title="Daily Activity Rate (June 2025)" if not is_bm else "Kadar Aktiviti Harian (Jun 2025)"
            )
            fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_line, use_container_width=True)

        st.write("")
        st.write("---")
        st.write("### ⚙️ " + ("System Nodes Integrity" if not is_bm else "Integriti Node Sistem"))
        
        status_c1, status_c2, status_c3 = st.columns(3)
        with status_c1:
            st.success("💻 " + ("Database: Operational" if not is_bm else "Pangkalan Data: Beroperasi Cemerlang"))
        with status_c2:
            st.success("📸 " + ("OCR Service: Operational" if not is_bm else "Servis OCR: Beroperasi Cemerlang"))
        with status_c3:
            # Check GEMINI_API_KEY presence
            gemini_exists = "GEMINI_API_KEY" in os.environ or "GEMINI_API_KEY" in st.secrets
            if gemini_exists:
                st.success("🤖 " + ("Gemini AI: Active" if not is_bm else "Gemini AI: Aktif & Sedia"))
            else:
                st.warning("🤖 " + ("Gemini AI: Inactive (Unconfigured)" if not is_bm else "Gemini AI: Tidak Aktif (Perlu Konfigurasi)"))


    # -------------------------------------------------------------
    # TAB 3 - CATEGORY MANAGEMENT
    # -------------------------------------------------------------
    with t3:
        st.write("### " + ("Expense Classification Schema" if not is_bm else "Skema Klasifikasi Perbelanjaan"))
        
        # Simulated transaction counts & total spend
        category_simulated_stats = {
            "Food & Dining": {"count": 48, "amount": 1240.20},
            "Transport": {"count": 14, "amount": 280.40},
            "Shopping": {"count": 21, "amount": 1050.50},
            "Bills": {"count": 10, "amount": 790.00},
            "Entertainment": {"count": 12, "amount": 340.00},
            "Other": {"count": 5, "amount": 110.00},
        }
        
        # Build category dataframe elements
        cat_records = []
        for cat in st.session_state.admin_categories:
            name = cat["Category Name"]
            color = cat["Colour"]
            is_default = cat["Default"]
            is_active = cat["Active"]
            
            # Read real active user transactions statistics
            u_count = 0
            u_amount = 0.0
            for tx in st.session_state.get("transactions", []):
                if tx.get("category") == name:
                    u_count += 1
                    u_amount += float(tx.get("amount", 0.0))
                    
            base = category_simulated_stats.get(name, {"count": 0, "amount": 0.0})
            combined_count = base["count"] + u_count
            combined_amount = base["amount"] + u_amount
            
            display_name = f"🔒 {name}" if is_default else f"👤 {name}"
            
            cat_records.append({
                "Category Name": display_name,
                "Colour": color,
                "Total Transactions": combined_count,
                "Total Amount (RM)": combined_amount,
                "Active": is_active,
                "raw_name": name,
                "Default": is_default
            })
            
        df_cats = pd.DataFrame(cat_records)
        
        st.markdown(f"<p style='font-size:12px; color:#666;'><i>" + 
                    ("Default system-wide categories are locked with 🔒 and cannot be renamed or deleted." if not is_bm else "Kategori sistem lalai dikunci dengan 🔒 dan tidak boleh dinamakan semula atau dipadam.") +
                    "</i></p>", unsafe_allow_html=True)
                    
        edited_cats_grid = st.data_editor(
            df_cats[["Category Name", "Colour", "Total Transactions", "Total Amount (RM)", "Active"]],
            column_config={
                "Active": st.column_config.CheckboxColumn(
                    "Active Status" if not is_bm else "Status Aktif",
                    help="Toggle category visibility across user screens" if not is_bm else "Togal kebolehlihatan kategori pada skrin pengguna",
                    default=True
                ),
                "Total Amount (RM)": st.column_config.NumberColumn(
                    format="RM %.2f"
                )
            },
            disabled=["Category Name", "Colour", "Total Transactions", "Total Amount (RM)"],
            use_container_width=True,
            key="category_schema_grid"
        )
        
        # Sync back category activation
        for idx, row in edited_cats_grid.iterrows():
            raw_name = df_cats.iloc[idx]["raw_name"]
            for c in st.session_state.admin_categories:
                if c["Category Name"] == raw_name:
                    c["Active"] = row["Active"]
                    
        # Custom category Deletion module
        custom_categories = [c for c in st.session_state.admin_categories if not c.get("Default", False)]
        if custom_categories:
            st.divider()
            st.write("##### 🗑️ " + ("Delete Custom Categories" if not is_bm else "Padam Kategori Khusus"))
            
            for c in custom_categories:
                c_name = c["Category Name"]
                col_del_1, col_del_2 = st.columns([5, 1])
                with col_del_1:
                    st.markdown(f"**{c_name}** &nbsp; (Colour Code: <code style='color:{c['Colour']}; font-weight:bold;'>{c['Colour']}</code>)", unsafe_allow_html=True)
                with col_del_2:
                    if st.button("Delete" if not is_bm else "Padam", key=f"del_cat_btn_{c_name}", use_container_width=True):
                        st.session_state.category_to_delete = c_name
                        st.rerun()
                        
            if "category_to_delete" in st.session_state and st.session_state.category_to_delete:
                to_delete = st.session_state.category_to_delete
                st.warning(f"Are you sure you want to permanently delete custom category '{to_delete}'? This cannot be undone." if not is_bm else f"Adakah anda pasti mahu memadam kategori '{to_delete}' ini selamanya? Tindakan ini tidak boleh ditarik balik.")
                col_cf_1, col_cf_2 = st.columns(2)
                with col_cf_1:
                    if st.button("Yes, Permanent Delete" if not is_bm else "Ya, Padam Selamanya", key="confirm_perm_delete_cat_btn", use_container_width=True):
                        st.session_state.admin_categories = [c for c in st.session_state.admin_categories if c["Category Name"] != to_delete]
                        st.session_state.category_to_delete = None
                        st.success(f"Custom Category '{to_delete}' deleted successfully!" if not is_bm else f"Kategori '{to_delete}' berjaya dipadam!")
                        st.rerun()
                with col_cf_2:
                    if st.button("Cancel" if not is_bm else "Batal", key="cancel_delete_cat_btn", use_container_width=True):
                        st.session_state.category_to_delete = None
                        st.rerun()

        # Add New Category Module
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.write("---")
        st.write("##### ➕ " + ("Create New System Category" if not is_bm else "Daftar Kategori Sistem Baru"))
        
        form_c1, form_c2, form_c3 = st.columns([3, 1, 1])
        with form_c1:
            new_cat_title = st.text_input("Category Display Name" if not is_bm else "Nama Paparan Kategori", placeholder="e.g. Subscriptions / Fasting", key="admin_new_cat_title_val")
        with form_c2:
            new_cat_hex = st.color_picker("Aesthetic Hex Color" if not is_bm else "Warna Hex Estetik", "#9333EA", key="admin_new_cat_color_val")
        with form_c3:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button("➕ Add Category" if not is_bm else "➕ Daftar Kategori", use_container_width=True, key="admin_add_category_submit_btn"):
                clean_title = new_cat_title.strip()
                if not clean_title:
                    st.error("Name is required!" if not is_bm else "Nama diperlukan!")
                elif any(c["Category Name"].lower() == clean_title.lower() for c in st.session_state.admin_categories):
                    st.error("Category name already exists!" if not is_bm else "Nama kategori sudah berdaftar!")
                else:
                    st.session_state.admin_categories.append({
                        "Category Name": clean_title,
                        "Colour": new_cat_hex,
                        "Default": False,
                        "Active": True
                    })
                    st.success(f"Category '{clean_title}' registered successfully!" if not is_bm else f"Kategori '{clean_title}' berjaya didaftarkan!")
                    st.rerun()


    # -------------------------------------------------------------
    # TAB 4 - TRANSACTION OVERSIGHT
    # -------------------------------------------------------------
    with t4:
        st.write("### " + ("Multi-User Transaction Ledger" if not is_bm else "Lejar Transaksi Pelbagai Pengguna"))
        
        # Construct unified table
        ledger_list = []
        
        # 1. Active User Transactions
        for tx in st.session_state.get("transactions", []):
            if "flagged" not in tx:
                tx["flagged"] = False
            ledger_list.append({
                "id": str(tx.get("id")),
                "user": tx.get("user", "Amirul Syafiq"),
                "merchant": tx.get("merchant", "Unknown Merchant"),
                "category": tx.get("category", "Other"),
                "amount": float(tx.get("amount", 0.0)),
                "date": tx.get("date", "2025-06-18"),
                "source": tx.get("source", "manual").upper(),
                "flagged": tx["flagged"]
            })
            
        # 2. Simulated Pooled Transactions
        for tx in st.session_state.admin_simulated_transactions:
            ledger_list.append({
                "id": str(tx.get("id")),
                "user": tx.get("user", "Amirul Syafiq"),
                "merchant": tx.get("merchant", "Unknown Merchant"),
                "category": tx.get("category", "Other"),
                "amount": float(tx.get("amount", 0.0)),
                "date": tx.get("date", "2025-06-18"),
                "source": tx.get("source", "manual").upper(),
                "flagged": tx.get("flagged", False)
            })
            
        df_ledger = pd.DataFrame(ledger_list)
        
        # FILTER CONTROLS COLUMN ROW
        st.write("##### 🔍 " + ("Audit Filters" if not is_bm else "Saringan Audit"))
        filt_c1, filt_c2, filt_c3, filt_c4 = st.columns(4)
        with filt_c1:
            all_users_options = ["All" if not is_bm else "Semua Pengguna"] + sorted(list(df_ledger["user"].unique()))
            selected_filt_user = st.selectbox("Audited User Name" if not is_bm else "Nama Pengguna Diaudit", options=all_users_options, key="audit_filter_user")
        with filt_c2:
            all_cats_options = ["All" if not is_bm else "Semua Kategori"] + sorted(list(df_ledger["category"].unique()))
            selected_filt_cat = st.selectbox("Category Group" if not is_bm else "Kumpulan Kategori", options=all_cats_options, key="audit_filter_category")
        with filt_c3:
            df_ledger["Datetime"] = pd.to_datetime(df_ledger["date"])
            min_date_val = df_ledger["Datetime"].min().date() if not df_ledger.empty else datetime.date(2025, 6, 1)
            max_date_val = df_ledger["Datetime"].max().date() if not df_ledger.empty else datetime.date(2025, 6, 30)
            
            selected_filt_dates = st.date_input("Audit Date Range" if not is_bm else "Julat Tarikh Audit", value=(min_date_val, max_date_val), key="audit_filter_dates")
        with filt_c4:
            min_amt_val = float(df_ledger["amount"].min()) if not df_ledger.empty else 0.0
            max_amt_val = float(df_ledger["amount"].max()) if not df_ledger.empty else 200.0
            
            selected_filt_amts = st.slider(
                "Amount Horizon (RM)" if not is_bm else "Kadar Amaun (RM)",
                min_value=0.0,
                max_value=max_amt_val + 50.0,
                value=(0.0, max_amt_val + 50.0),
                key="audit_filter_amounts"
            )
            
        # Apply Filters Dynamically
        df_ledger_filtered = df_ledger.copy()
        
        if selected_filt_user not in ["All", "Semua Pengguna"]:
            df_ledger_filtered = df_ledger_filtered[df_ledger_filtered["user"] == selected_filt_user]
            
        if selected_filt_cat not in ["All", "Semua Kategori"]:
            df_ledger_filtered = df_ledger_filtered[df_ledger_filtered["category"] == selected_filt_cat]
            
        if isinstance(selected_filt_dates, tuple) and len(selected_filt_dates) == 2:
            f_start, f_end = selected_filt_dates
            df_ledger_filtered = df_ledger_filtered[
                (df_ledger_filtered["Datetime"].dt.date >= f_start) & 
                (df_ledger_filtered["Datetime"].dt.date <= f_end)
            ]
            
        df_ledger_filtered = df_ledger_filtered[
            (df_ledger_filtered["amount"] >= selected_filt_amts[0]) & 
            (df_ledger_filtered["amount"] <= selected_filt_amts[1])
        ]
        
        # Prepare aesthetic dataframe for user layout (st.dataframe)
        display_ledger_rows = []
        for idx, row in df_ledger_filtered.iterrows():
            is_flagged = row["flagged"]
            display_ledger_rows.append({
                "Transaction ID": row["id"],
                "User": row["user"],
                "Merchant": f"⚠️ {row['merchant']}" if is_flagged else row["merchant"],
                "Category": row["category"],
                "Amount (RM)": row["amount"],
                "Date": row["date"],
                "Source (OCR/Manual)": row["source"],
                "Ledger Status": "⚠️ Suspicious Flag" if is_flagged else "Normal/Approved"
            })
            
        df_ledger_render = pd.DataFrame(display_ledger_rows)
        
        if not df_ledger_render.empty:
            st.dataframe(
                df_ledger_render[["Transaction ID", "User", "Merchant", "Category", "Amount (RM)", "Date", "Source (OCR/Manual)", "Ledger Status"]],
                column_config={
                    "Amount (RM)": st.column_config.NumberColumn(format="RM %.2f")
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Export CSV block
            csv_lejer = df_ledger_render.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Ledger to CSV" if not is_bm else "📥 Eksport Lejar ke CSV",
                data=csv_lejer,
                file_name="ipecs_audit_ledger.csv",
                mime="text/csv",
                key="admin_download_ledger_csv_btn"
            )
        else:
            st.warning("No transactions match the given query boundaries." if not is_bm else "Tiada transaksi yang sepadan dengan kriteria carian anda.")

        st.write("")
        st.divider()
        st.write("##### ⚠️ " + ("Oversight Security Controls" if not is_bm else "Kawalan Keselamatan Pemantauan"))
        
        # Flag suspicious transaction action panel
        ctrl_c1, ctrl_c2 = st.columns([3, 1])
        with ctrl_c1:
            full_tx_options_map = {}
            full_tx_display_strings = []
            for tx in ledger_list:
                flag_label = " (⚠️ Flagged)" if tx["flagged"] else ""
                label_str = f"#{tx['id']} - {tx.get('user', 'Amirul Syafiq')} - {tx['merchant']} - RM {tx['amount']:.2f}{flag_label}"
                full_tx_options_map[label_str] = tx
                full_tx_display_strings.append(label_str)
                
            selected_tx_flag_label = st.selectbox(
                "Select target transaction row" if not is_bm else "Pilih baris transaksi sasaran",
                options=full_tx_display_strings,
                key="admin_target_tx_flag_selection"
            )
        with ctrl_c2:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if selected_tx_flag_label:
                tx_record_dict = full_tx_options_map[selected_tx_flag_label]
                t_id = tx_record_dict["id"]
                t_flagged = tx_record_dict["flagged"]
                
                toggle_btn_txt = "🏳️ Clear Flag" if t_flagged else "⚠️ Flag Suspicious"
                if is_bm:
                    toggle_btn_txt = "🏳️ Buang Bendera" if t_flagged else "⚠️ Tandakan Bahaya"
                    
                if st.button(toggle_btn_txt, use_container_width=True, key="admin_execute_toggle_flag_btn"):
                    # Apply changes
                    if t_id.startswith("sim_"):
                        # update simulated rows
                        for sim_t in st.session_state.admin_simulated_transactions:
                            if sim_t["id"] == t_id:
                                sim_t["flagged"] = not sim_t.get("flagged", False)
                                break
                    else:
                        # update user live session transactions
                        for u_t in st.session_state.transactions:
                            if str(u_t.get("id")) == str(t_id):
                                u_t["flagged"] = not u_t.get("flagged", False)
                                break
                    st.success("Ledger Entry updated successfully!" if not is_bm else "Kembar Lejar telah dikemas kini dengan jaya!")
                    st.rerun()
