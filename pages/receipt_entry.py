import streamlit as st
import time
import json
import io
from datetime import date
import PIL.Image

# ── Gemini Setup ──────────────────────────────────────────────
import google.generativeai as genai

def get_gemini_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        return None

def extract_with_gemini(image_bytes):
    """Extract receipt data using Gemini Vision API"""
    model = get_gemini_model()
    
    if model is None:
        return {
            "merchant": "Unknown Merchant",
            "amount": 0.0,
            "date": str(date.today()),
            "category": "Other",
            "confidence": 0,
            "error": "Gemini API key not configured. Please add GEMINI_API_KEY to .streamlit/secrets.toml"
        }
    
    try:
        img = PIL.Image.open(io.BytesIO(image_bytes))
        
        prompt = """
        You are a receipt scanning assistant for a Malaysian expense tracking app.
        
        Analyze this receipt image carefully and extract the following information.
        Return ONLY a valid JSON object with these exact keys and nothing else — no markdown, no explanation, just the raw JSON:
        
        {
            "merchant": "the business or store name, usually the largest text at the top of the receipt",
            "amount": 0.00,
            "date": "YYYY-MM-DD",
            "category": "Food & Dining",
            "confidence": 85
        }
        
        Rules:
        - merchant: Look for the store/restaurant/business name, usually at the very top. For Malaysian receipts this could be in English or Malay.
        - amount: Look for TOTAL, JUMLAH, GRAND TOTAL, AMAUN. Extract the final amount as a number only, no RM symbol. If multiple totals exist, use the largest/final one.
        - date: Convert any date format to YYYY-MM-DD. Common formats on Malaysian receipts: DD/MM/YYYY, DD-MM-YYYY, DD MMM YYYY.
        - category: Choose exactly one from this list based on the merchant type:
            * "Food & Dining" — restaurants, cafes, mamak, fast food, bubble tea, groceries
            * "Transport" — petrol stations, Grab, parking, bus, LRT, MRT, toll
            * "Shopping" — clothing, electronics, pharmacies, beauty, department stores
            * "Bills" — utilities, phone bills, internet, insurance, subscriptions
            * "Entertainment" — cinema, games, sports, concerts, streaming services
            * "Other" — anything that does not fit the above
        - confidence: Your confidence in the extraction accuracy, from 0 to 100. Be honest — if the image is blurry or text is hard to read, give a lower score.
        
        If you cannot determine a field, use these defaults:
        - merchant: "Unknown Merchant"
        - amount: 0.00
        - date: today's date in YYYY-MM-DD
        - category: "Other"
        - confidence: 30
        
        Return ONLY the JSON object. No markdown code blocks. No explanation text.
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Clean markdown formatting if Gemini adds it
        text = text.replace('```json', '').replace('```', '').strip()
        
        data = json.loads(text)
        
        # Validate and sanitize
        valid_categories = ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
        category = data.get("category", "Other")
        if category not in valid_categories:
            category = "Other"
        
        return {
            "merchant": str(data.get("merchant", "Unknown Merchant")).strip(),
            "amount":   float(data.get("amount", 0.0)),
            "date":     str(data.get("date", str(date.today()))),
            "category": category,
            "confidence": min(100, max(0, int(data.get("confidence", 75))))
        }
        
    except json.JSONDecodeError as e:
        return {
            "merchant": "Unknown Merchant",
            "amount":   0.0,
            "date":     str(date.today()),
            "category": "Other",
            "confidence": 0,
            "error": f"Could not parse Gemini response: {str(e)}"
        }
    except Exception as e:
        return {
            "merchant": "Unknown Merchant",
            "amount":   0.0,
            "date":     str(date.today()),
            "category": "Other",
            "confidence": 0,
            "error": f"Gemini extraction failed: {str(e)}"
        }


# ── Main Page ─────────────────────────────────────────────────
def show_receipt_entry():
    is_bm = (st.session_state.get("lang", "EN") == "BM")

    t_title      = "Kemasukan Resit & Transaksi"         if is_bm else "Receipt & Transaction Entry"
    t_ocr_tab    = "🔍 Muat Naik Resit OCR"              if is_bm else "🔍 OCR Receipt Upload"
    t_manual_tab = "✏️ Borang Data Manual"               if is_bm else "✏️ Manual Data Form"

    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption("Scan your Malaysian receipts or enter transactions manually." if not is_bm else "Imbas resit Malaysia anda atau masukkan transaksi secara manual.")
    st.divider()

    categories = ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
    tabs = st.tabs([t_ocr_tab, t_manual_tab])

    # ═══════════════════════════════════════════════════════════
    # TAB 1 — OCR RECEIPT UPLOAD
    # ═══════════════════════════════════════════════════════════
    with tabs[0]:
        st.subheader("Gemini Vision OCR" if not is_bm else "OCR Gemini Vision")

        # ── Clear previous scan ───────────────────────────────
        if "last_ocr_val" in st.session_state:
            if st.button("🔄 Scan New Receipt" if not is_bm else "🔄 Imbas Resit Baru", key="clear_ocr"):
                del st.session_state["last_ocr_val"]
                st.rerun()

        # ── Upload or Camera ──────────────────────────────────
        upload_method = st.radio(
            "How would you like to add your receipt?" if not is_bm else "Bagaimana anda mahu menambah resit?",
            ["📁 Upload from gallery" if not is_bm else "📁 Muat naik dari galeri",
             "📷 Take a photo"        if not is_bm else "📷 Ambil foto"],
            horizontal=True,
            key="upload_method"
        )

        uploaded_file = None
        cam_photo     = None

        if "Upload" in upload_method or "Muat" in upload_method:
            uploaded_file = st.file_uploader(
                "Choose a receipt image (JPG or PNG)" if not is_bm else "Pilih imej resit (JPG atau PNG)",
                type=["jpg", "jpeg", "png"],
                key="receipt_uploader"
            )
        else:
            cam_photo = st.camera_input(
                "Point your camera at the receipt and capture" if not is_bm else "Arahkan kamera ke resit dan tangkap foto",
                key="receipt_camera"
            )

        image_source = cam_photo or uploaded_file

        # ── Run extraction when image is provided ─────────────
        if image_source:

            # Show preview
            st.image(image_source, caption="Receipt Preview" if not is_bm else "Pratonton Resit", width=300)

            # Run Gemini OCR if not already done for this image
            if "last_ocr_val" not in st.session_state:
                with st.spinner("Extracting receipt data with Gemini Vision AI..." if not is_bm else "Mengekstrak data resit dengan Gemini Vision AI..."):
                    image_bytes = image_source.getvalue()
                    result = extract_with_gemini(image_bytes)
                    st.session_state["last_ocr_val"] = result

            ocr = st.session_state["last_ocr_val"]

            # ── Show error if extraction failed ───────────────
            if "error" in ocr and ocr.get("confidence", 0) == 0:
                st.error(f"⚠️ Extraction issue: {ocr['error']}" if not is_bm else f"⚠️ Masalah pengekstrakan: {ocr['error']}")
                st.info("Please fill in the fields manually below." if not is_bm else "Sila isi medan di bawah secara manual.")
            else:
                # Confidence badge
                conf = ocr.get("confidence", 0)
                if conf >= 80:
                    badge_color = "green"
                    badge_icon  = "✅"
                elif conf >= 50:
                    badge_color = "orange"
                    badge_icon  = "⚠️"
                else:
                    badge_color = "red"
                    badge_icon  = "❌"

                st.markdown(
                    f'<div style="background:{"#d4edda" if conf>=80 else "#fff3cd" if conf>=50 else "#f8d7da"};'
                    f'border-radius:8px;padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.9rem;">'
                    f'{badge_icon} {"Receipt Extracted Successfully" if not is_bm else "Resit Berjaya Diekstrak"} — '
                    f'{"Confidence" if not is_bm else "Keyakinan"}: <b>{conf}%</b></div>',
                    unsafe_allow_html=True
                )

            # ── Editable extracted fields ─────────────────────
            st.markdown("#### " + ("Verify & Edit Extracted Data" if not is_bm else "Semak & Edit Data Diekstrak"))
            st.caption("Review the extracted information and correct any errors before saving." if not is_bm else "Semak maklumat yang diekstrak dan betulkan sebarang kesilapan sebelum menyimpan.")

            col1, col2 = st.columns(2)
            with col1:
                merch = st.text_input(
                    "Merchant Name" if not is_bm else "Nama Peniaga",
                    value=ocr.get("merchant", ""),
                    key="ocr_merchant"
                )
                amt = st.number_input(
                    "Amount (RM)" if not is_bm else "Jumlah (RM)",
                    value=float(ocr.get("amount", 0.0)),
                    min_value=0.0,
                    step=0.10,
                    format="%.2f",
                    key="ocr_amount"
                )
            with col2:
                # Parse date safely
                raw_date = ocr.get("date", str(date.today()))
                try:
                    parsed_date = date.fromisoformat(raw_date)
                except Exception:
                    parsed_date = date.today()

                dt = st.date_input(
                    "Transaction Date" if not is_bm else "Tarikh Transaksi",
                    value=parsed_date,
                    key="ocr_date"
                )

                # Pre-select extracted category
                ocr_cat = ocr.get("category", "Other")
                if ocr_cat not in categories:
                    ocr_cat = "Other"
                cat = st.selectbox(
                    "Category" if not is_bm else "Kategori",
                    categories,
                    index=categories.index(ocr_cat),
                    key="ocr_category"
                )

            p_notes = st.text_input(
                "Personal Notes" if not is_bm else "Nota Peribadi",
                value="OCR Scanned receipt" if not is_bm else "Resit diimbas OCR",
                key="ocr_notes"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Save button ───────────────────────────────────
            btn_label = "✅ Confirm & Save Transaction" if not is_bm else "✅ Sahkan & Simpan Transaksi"
            if st.button(btn_label, key="btn_save_ocr", type="primary", use_container_width=True):
                if not merch.strip():
                    st.error("Merchant name cannot be empty." if not is_bm else "Nama peniaga tidak boleh kosong.")
                elif amt <= 0:
                    st.error("Amount must be greater than 0." if not is_bm else "Jumlah mesti lebih daripada 0.")
                else:
                    tx_id  = str(int(time.time()))
                    new_tx = {
                        "id":       tx_id,
                        "merchant": merch.strip(),
                        "amount":   float(amt),
                        "date":     str(dt),
                        "category": cat,
                        "notes":    p_notes,
                        "source":   "ocr"
                    }

                    if "transactions" not in st.session_state:
                        st.session_state.transactions = []
                    st.session_state.transactions.insert(0, new_tx)

                    # Check budget overspend and create alert
                    if "budgets" in st.session_state:
                        spent = sum(
                            float(tx["amount"])
                            for tx in st.session_state.transactions
                            if tx["date"].startswith(str(dt)[:7]) and tx["category"] == cat
                        )
                        lim = st.session_state.budgets.get(cat, 0.0)
                        if lim > 0 and spent > lim:
                            if "alerts" not in st.session_state:
                                st.session_state.alerts = []
                            st.session_state.alerts.insert(0, {
                                "id":        "a_" + tx_id,
                                "type":      "Overspend Warning",
                                "category":  cat,
                                "amount":    float(amt),
                                "date":      str(dt),
                                "severity":  "Medium",
                                "dismissed": False
                            })

                    st.toast(f"✅ Saved — RM {amt:.2f} | {merch} | {cat}" if not is_bm else f"✅ Disimpan — RM {amt:.2f} | {merch} | {cat}")

                    # Clear OCR cache and reset
                    if "last_ocr_val" in st.session_state:
                        del st.session_state["last_ocr_val"]
                    st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TAB 2 — MANUAL ENTRY
    # ═══════════════════════════════════════════════════════════
    with tabs[1]:
        st.subheader("Enter Spent Details Manually" if not is_bm else "Isi Butiran Perbelanjaan Manual")

        with st.form("manual_spent_form", clear_on_submit=True):
            man_merch = st.text_input(
                "Merchant Name" if not is_bm else "Nama Peniaga",
                placeholder="e.g. Restoran Ali, Shell Petrol" if not is_bm else "cth. Restoran Ali, Shell Petrol"
            )
            man_amt = st.number_input(
                "Amount (RM)" if not is_bm else "Jumlah (RM)",
                min_value=0.01, step=0.10, format="%.2f"
            )
            man_dt  = st.date_input(
                "Transaction Date" if not is_bm else "Tarikh Transaksi",
                value=date.today()
            )
            man_cat = st.selectbox(
                "Category" if not is_bm else "Kategori",
                categories
            )
            man_notes = st.text_area(
                "Personal Notes (optional)" if not is_bm else "Nota Peribadi (pilihan)",
                placeholder="Any extra details about this transaction..." if not is_bm else "Sebarang butiran tambahan..."
            )

            save_lbl  = "Save Transaction" if not is_bm else "Simpan Transaksi"
            submitted = st.form_submit_button(f"✅ {save_lbl}", use_container_width=True)

            if submitted:
                if not man_merch.strip():
                    st.error("Please enter a valid merchant name." if not is_bm else "Sila masukkan nama peniaga yang sah.")
                elif man_amt <= 0:
                    st.error("Amount must be greater than 0." if not is_bm else "Jumlah mesti lebih daripada 0.")
                else:
                    tx_id  = str(int(time.time()))
                    new_tx = {
                        "id":       tx_id,
                        "merchant": man_merch.strip(),
                        "amount":   float(man_amt),
                        "date":     str(man_dt),
                        "category": man_cat,
                        "notes":    man_notes,
                        "source":   "manual"
                    }

                    if "transactions" not in st.session_state:
                        st.session_state.transactions = []
                    st.session_state.transactions.insert(0, new_tx)

                    # Check budget overspend
                    if "budgets" in st.session_state:
                        spent = sum(
                            float(tx["amount"])
                            for tx in st.session_state.transactions
                            if tx["date"].startswith(str(man_dt)[:7]) and tx["category"] == man_cat
                        )
                        lim = st.session_state.budgets.get(man_cat, 0.0)
                        if lim > 0 and spent > lim:
                            if "alerts" not in st.session_state:
                                st.session_state.alerts = []
                            st.session_state.alerts.insert(0, {
                                "id":        "a_" + tx_id,
                                "type":      "Overspend Warning",
                                "category":  man_cat,
                                "amount":    float(man_amt),
                                "date":      str(man_dt),
                                "severity":  "Medium",
                                "dismissed": False
                            })

                    st.success(f"✅ Transaction saved — RM {man_amt:.2f} added to {man_cat}" if not is_bm else f"✅ Transaksi disimpan — RM {man_amt:.2f} ditambah ke {man_cat}")
                    time.sleep(0.8)
                    st.rerun()