import streamlit as st
import random
import time
from datetime import date

presets = [
  {"merchant": "Restoran Ali Maju Mamak", "amount": 12.50, "category": "Food & Dining", "confidence": 94},
  {"merchant": "MyRapid Bus KL", "amount": 2.10, "category": "Transport", "confidence": 98},
  {"merchant": "Lotus's Ara Damansara", "amount": 67.80, "category": "Shopping", "confidence": 91},
  {"merchant": "Unifi Monthly Bill", "amount": 89.00, "category": "Bills", "confidence": 97},
  {"merchant": "TGV Cinemas 1Utama", "amount": 23.00, "category": "Entertainment", "confidence": 89},
  {"merchant": "KK Super Mart UMS", "amount": 18.30, "category": "Food & Dining", "confidence": 93},
]

def show_receipt_entry():
    is_bm = (st.session_state.lang == "BM")
    
    t_title = "Kemasukan Resit & Transaksi" if is_bm else "Receipt & Transaction Entry"
    t_ocr_tab = "🔍 Muat Naik Resit OCR" if is_bm else "🔍 OCR Receipt Upload"
    t_manual_tab = "✏️ Borang Data Manual" if is_bm else "✏️ Manual Data Form"
    
    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Scan Mamak / RapidKL receipts or inputs manual spend.")
    st.divider()

    tabs = st.tabs([t_ocr_tab, t_manual_tab])
    
    # Categories list
    categories = ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

    with tabs[0]:
        st.subheader("Simulate Intelligent OCR" if not is_bm else "Simulasi OCR Pintar")
        
        uploaded_file = st.file_uploader("Upload your receipt" if not is_bm else "Muat naik resit anda", type=["jpg", "jpeg", "png"])
        cam_photo = st.camera_input("Or take a photo of your receipt" if not is_bm else "Atau ambil foto resit anda")

        if uploaded_file or cam_photo:
            # Trigger simulation
            if "last_ocr_val" not in st.session_state:
                with st.spinner("Extracting receipt data with Gemini OCR..." if not is_bm else "Mengekstrak data resit dengan Gemini OCR..."):
                    time.sleep(1.5)
                    preset = random.choice(presets).copy()
                    
                    # Random june Date
                    p_day = random.choice(["02", "06", "11", "15", "17"])
                    preset["date"] = f"2025-06-{p_day}"
                    st.session_state.last_ocr_val = preset
            
            # Show extracted card
            ocr = st.session_state.last_ocr_val
            st.success(f"Receipt Extracted Successfully! Confidence: {ocr['confidence']}%" if not is_bm else f"Resit Berjaya Diekstrak! Keyakinan: {ocr['confidence']}%")
            
            col1, col2 = st.columns(2)
            with col1:
                merch = st.text_input("Merchant Name" if not is_bm else "Nama Peniaga", value=ocr["merchant"])
                amt = st.number_input("Amount (RM)" if not is_bm else "Jumlah (RM)", value=float(ocr["amount"]), step=0.1)
            with col2:
                dt = st.text_input("Transaction Date" if not is_bm else "Tarikh Transaksi", value=ocr["date"])
                cat = st.selectbox("Category" if not is_bm else "Kategori", categories, index=categories.index(ocr["category"]))
                
            p_notes = st.text_input("Personal Notes" if not is_bm else "Nota Peribadi", value="OCR Scanned receipt")
            
            if st.button("Confirm & Save Transaction" if not is_bm else "Sahkan & Simpan Transaksi"):
                tx_id = str(int(time.time()))
                new_tx = {
                    "id": tx_id,
                    "merchant": merch,
                    "amount": float(amt),
                    "date": dt,
                    "category": cat,
                    "notes": p_notes,
                    "source": "ocr"
                }
                
                # Append
                st.session_state.transactions.insert(0, new_tx)
                
                # Check for dynamic alerts
                spent = sum(float(tx["amount"]) for tx in st.session_state.transactions if tx["date"].startswith("2025-06") and tx["category"] == cat)
                lim = st.session_state.budgets.get(cat, 0.0)
                if lim > 0 and spent > lim:
                    # Append alert
                    new_alert = {
                        "id": "a_" + tx_id,
                        "type": "Overspend Warning",
                        "category": cat,
                        "amount": float(amt),
                        "date": dt,
                        "severity": "Medium",
                        "dismissed": False
                    }
                    st.session_state.alerts.insert(0, new_alert)
                    
                st.toast(f"Transaction saved — RM {amt:.2f} added to {cat}" if not is_bm else f"Transaksi disimpan — RM {amt:.2f} ditambah ke {cat}")
                
                # Clears OCR cache
                del st.session_state.last_ocr_val
                st.rerun()

    with tabs[1]:
        st.subheader("Enter Spent Details Manually" if not is_bm else "Isi Butiran Sembunyi Manual")
        
        with st.form("manual_spent_form"):
            man_merch = st.text_input("Merchant Name" if not is_bm else "Nama Peniaga")
            man_amt = st.number_input("Amount (RM)" if not is_bm else "Jumlah (RM)", min_value=0.01, step=0.1)
            man_dt = st.date_input("Transaction Date" if not is_bm else "Tarikh Transaksi", value=date.today())
            man_cat = st.selectbox("Category" if not is_bm else "Kategori", categories)
            man_notes = st.text_area("Personal Notes" if not is_bm else "Nota Peribadi")
            
            save_lbl = "Save Transaction" if not is_bm else "Simpan Transaksi"
            submitted = st.form_submit_button(f"✅ {save_lbl}")
            
            if submitted:
                if not man_merch:
                    st.error("Please insert a valid Merchant name." if not is_bm else "Sila masukkan nama Peniaga.")
                else:
                    tx_id = str(int(time.time()))
                    new_tx = {
                        "id": tx_id,
                        "merchant": man_merch,
                        "amount": float(man_amt),
                        "date": str(man_dt),
                        "category": man_cat,
                        "notes": man_notes,
                        "source": "manual"
                    }
                    
                    st.session_state.transactions.insert(0, new_tx)
                    
                    # Trigger alert if overspent
                    spent = sum(float(tx["amount"]) for tx in st.session_state.transactions if tx["date"].startswith("2025-06") and tx["category"] == man_cat)
                    lim = st.session_state.budgets.get(man_cat, 0.0)
                    if lim > 0 and spent > lim:
                        new_alert = {
                            "id": "a_" + tx_id,
                            "type": "Overspend Warning",
                            "category": man_cat,
                            "amount": float(man_amt),
                            "date": str(man_dt),
                            "severity": "Medium",
                            "dismissed": False
                        }
                        st.session_state.alerts.insert(0, new_alert)
                        
                    st.success(f"Transaction saved — RM{man_amt:.2f} added to {man_cat}" if not is_bm else f"Transaksi disimpan — RM{man_amt:.2f} ditambah ke {man_cat}")
                    time.sleep(1.0)
                    st.rerun()
