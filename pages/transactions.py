import streamlit as st
import pandas as pd
from datetime import datetime

def show_transactions():
    is_bm = (st.session_state.lang == "BM")
    
    t_title = "Pengurusan Transaksi & Kategori" if is_bm else "Transaction & Category Management"
    t_filter = "Bahagian Atas — Penapis" if is_bm else "Top section — Filters"
    t_apply = "Guna Penapis" if is_bm else "Apply Filters"
    t_delete = "Padam Terpilih" if is_bm else "Delete Selected"
    t_manage = "⚙️ Urus Kategori" if is_bm else "⚙️ Manage Categories"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Spreadsheet data editor with dynamic item categorization filters.")
    st.divider()

    txs = st.session_state.transactions
    budgets = st.session_state.budgets

    # 1. Filters Card
    with st.expander(t_filter, expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            start_dt = st.date_input("Start Date", value=datetime.strptime("2025-06-01", "%Y-%m-%d").date())
        with col2:
            end_dt = st.date_input("End Date", value=datetime.strptime("2025-06-30", "%Y-%m-%d").date())
        with col3:
            cats = ["All"] + list(budgets.keys())
            sel_cat = st.selectbox("Category", cats)
        with col4:
            max_amt = st.slider("Max Amount (RM)", min_value=5.0, max_value=500.0, value=200.0, step=5.0)

    # Convert lists to Pandas DF for filtration
    df = pd.DataFrame(txs)
    
    if df.empty:
        st.info("No transaction values found in st.session_state.")
        return

    df["date_parsed"] = pd.to_datetime(df["date"])
    
    # Filter operations
    filtered_df = df[
        (df["date_parsed"].dt.date >= start_dt) &
        (df["date_parsed"].dt.date <= end_dt) &
        (df["amount"] <= max_amt)
    ]
    
    if sel_cat != "All":
        filtered_df = filtered_df[filtered_df["category"] == sel_cat]

    st.write("")
    
    # Render st.data_editor
    st.write("Double click cells to edit in spreadsheet grid:")
    edited_df = st.data_editor(
        filtered_df.drop(columns=["date_parsed"]),
        num_rows="dynamic",
        key="tx_editor_grid",
        use_container_width=True
    )
    
    # Sync edited DF changes back to Session state
    if st.button("Save Changes" if not is_bm else "Simpan Perubahan"):
        new_txs = edited_df.to_dict("records")
        # Ensure correct formats
        for tx in new_txs:
            tx["amount"] = float(tx["amount"])
            tx["id"] = str(tx["id"])
        st.session_state.transactions = new_txs
        st.success("Changes synced to st.session_state successfully!" if not is_bm else "Perubahan berjaya disimpan!")
        time_sleep = 0.5
        st.rerun()

    # Expanders: Manage Categories
    with st.expander(t_manage):
        st.subheader("Interactive Categories Overview" if not is_bm else "Gambaran Kesuluruhan Kategori")
        
        # Calculate stats
        cat_sums = {}
        cat_counts = {}
        for tx in txs:
            if tx["date"].startswith("2025-06"):
                cat_sums[tx["category"]] = cat_sums.get(tx["category"], 0.0) + float(tx["amount"])
                cat_counts[tx["category"]] = cat_counts.get(tx["category"], 0) + 1
        
        bva_rows = []
        for cat in budgets:
            bva_rows.append({
                "Category": cat,
                "Spent (RM June)": f"RM {cat_sums.get(cat, 0.0):.2f}",
                "Tx Count": cat_counts.get(cat, 0)
            })
            
        st.dataframe(pd.DataFrame(bva_rows), use_container_width=True)

        st.divider()
        st.markdown("**Add custom category**")
        new_name = st.text_input("New Category Name" if not is_bm else "Nama Kategori Baru")
        if st.button("Add Category" if not is_bm else "Tambah Kategori"):
            if new_name and new_name not in st.session_state.budgets:
                st.session_state.budgets[new_name] = 50.0  # default budget cap
                st.success(f"Custom Category '{new_name}' Added!" if not is_bm else f"Kategori Khas '{new_name}' Ditambah!")
                st.rerun()
