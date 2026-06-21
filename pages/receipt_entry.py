import streamlit as st
import time
import json
import io
from datetime import date
import PIL.Image
from google import genai

# ── Gemini Extraction ─────────────────────────────────────────
def extract_with_gemini(image_bytes):
    """Extract receipt data using Gemini Vision API (google-genai SDK)"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        return {
            "merchant":   "Unknown Merchant",
            "amount":     0.0,
            "date":       str(date.today()),
            "category":   "Other",
            "confidence": 0,
            "error":      "GEMINI_API_KEY not found in .streamlit/secrets.toml"
        }

    try:
        client = genai.Client(api_key=api_key)
        img    = PIL.Image.open(io.BytesIO(image_bytes))

        prompt = """
        You are a receipt scanning assistant for a Malaysian expense tracking app.

        Analyze this receipt image carefully and extract the following information.
        Return ONLY a valid JSON object with these exact keys and nothing else.
        No markdown, no explanation, just raw JSON:

        {
            "merchant": "business name at the top of the receipt",
            "amount": 0.00,
            "date": "YYYY-MM-DD",
            "category": "Food & Dining",
            "confidence": 85
        }

        Rules:
        - merchant: Store or restaurant name, usually the largest text at the top of the receipt
        - amount: Look for TOTAL, JUMLAH, GRAND TOTAL, AMAUN. Return as number only, no RM symbol
        - date: Convert any date format to YYYY-MM-DD. Common Malaysian formats: DD/MM/YYYY, DD-MM-YYYY, DD MMM YYYY
        - category: Choose exactly ONE from this list:
            Food & Dining — restaurants, cafes, mamak, fast food, bubble tea, kopitiam, bakery
            Transport — petrol stations, Grab, parking, bus, LRT, MRT, toll, taxi
            Shopping — clothing, electronics, pharmacies, beauty, department stores, supermarkets
            Bills — utilities, phone bills, internet, insurance, subscriptions
            Entertainment — cinema, games, sports, concerts, streaming
            Other — anything that does not fit the above
        - confidence: Your confidence in extraction accuracy from 0 to 100

        If you cannot read a field clearly, use these defaults:
        - merchant: Unknown Merchant
        - amount: 0.00
        - date: today in YYYY-MM-DD
        - category: Other
        - confidence: 30

        Return ONLY the JSON object. No markdown. No extra text.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, img]
        )

        text = response.text.strip()
        text = text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)

        valid_categories = [
            "Food & Dining", "Transport", "Shopping",
            "Bills", "Entertainment", "Other"
        ]
        category = data.get("category", "Other")
        if category not in valid_categories:
            category = "Other"

        return {
            "merchant":   str(data.get("merchant", "Unknown Merchant")).strip(),
            "amount":     float(data.get("amount", 0.0)),
            "date":       str(data.get("date", str(date.today()))),
            "category":   category,
            "confidence": min(100, max(0, int(data.get("confidence", 75))))
        }

    except json.JSONDecodeError as e:
        return {
            "merchant":   "Unknown Merchant",
            "amount":     0.0,
            "date":       str(date.today()),
            "category":   "Other",
            "confidence": 0,
            "error":      f"Could not parse Gemini response: {str(e)}"
        }
    except Exception as e:
        return {
            "merchant":   "Unknown Merchant",
            "amount":     0.0,
            "date":       str(date.today()),
            "category":   "Other",
            "confidence": 0,
            "error":      f"Gemini extraction failed: {str(e)}"
        }


# ── Main Page ─────────────────────────────────────────────────
def show_receipt_entry():
    is_bm = (st.session_state.get("lang", "EN") == "BM")

    t_title      = "Kemasukan Resit & Transaksi"    if is_bm else "Receipt & Transaction Entry"
    t_ocr_tab    = "🔍 Muat Naik Resit OCR"         if is_bm else "🔍 OCR Receipt Upload"
    t_manual_tab = "✏️ Borang Data Manual"          if is_bm else "✏️ Manual Data Form"

    st.markdown(f"<h2>{t_title}</h2>", unsafe_allow_html=True)
    st.caption(
        "Imbas resit Malaysia anda atau masukkan transaksi secara manual." if is_bm
        else "Scan your Malaysian receipts or enter transactions manually."
    )
    st.divider()

    categories = ["Food & Dining", "Transport", "Shopping", "Bills", "Entertainment", "Other"]
    tabs = st.tabs([t_ocr_tab, t_manual_tab])

    # ═══════════════════════════════════════════════════════════
    # TAB 1 — OCR RECEIPT UPLOAD
    # ═══════════════════════════════════════════════════════════
    with tabs[0]:
        st.subheader("Gemini Vision OCR" if not is_bm else "OCR Gemini Vision")

        # Clear previous scan button
        if "last_ocr_val" in st.session_state:
            if st.button(
                "🔄 Scan New Receipt" if not is_bm else "🔄 Imbas Resit Baru",
                key="clear_ocr"
            ):
                del st.session_state["last_ocr_val"]
                st.rerun()

        # Upload method selector
        upload_method = st.radio(
            "How would you like to add your receipt?" if not is_bm else "Bagaimana anda mahu menambah resit?",
            [
                "📁 Upload from gallery" if not is_bm else "📁 Muat naik dari galeri",
                "📷 Take a photo"        if not is_bm else "📷 Ambil foto"
            ],
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

        # Run extraction when image is provided
        if image_source:

            # Show preview
            st.image(
                image_source,
                caption="Receipt Preview" if not is_bm else "Pratonton Resit",
                width=300
            )

            # Run Gemini OCR only once per image
            if "last_ocr_val" not in st.session_state:
                with st.spinner(
                    "Extracting receipt data with Gemini Vision AI..." if not is_bm
                    else "Mengekstrak data resit dengan Gemini Vision AI..."
                ):
                    image_bytes = image_source.getvalue()
                    result = extract_with_gemini(image_bytes)
                    st.session_state["last_ocr_val"] = result

            ocr = st.session_state["last_ocr_val"]

            # Show error if extraction failed
            if "error" in ocr and ocr.get("confidence", 0) == 0:
                st.error(
                    f"⚠️ Extraction issue: {ocr['error']}" if not is_bm
                    else f"⚠️ Masalah pengekstrakan: {ocr['error']}"
                )
                st.info(
                    "Please fill in the fields manually below." if not is_bm
                    else "Sila isi medan di bawah secara manual."
                )
            else:
                # Confidence badge
                conf = ocr.get("confidence", 0)
                if conf >= 80:
                    bg    = "#d4edda"
                    icon  = "✅"
                elif conf >= 50:
                    bg    = "#fff3cd"
                    icon  = "⚠️"
                else:
                    bg    = "#f8d7da"
                    icon  = "❌"

                st.markdown(
                    f'<div style="background:{bg};border-radius:8px;padding:0.6rem 1rem;'
                    f'margin-bottom:1rem;font-size:0.9rem;">'
                    f'{icon} {"Receipt Extracted Successfully" if not is_bm else "Resit Berjaya Diekstrak"} — '
                    f'{"Confidence" if not is_bm else "Keyakinan"}: <b>{conf}%</b></div>',
                    unsafe_allow_html=True
                )

            # Editable extracted fields — shown even if error (for manual correction)
            st.markdown("#### " + (
                "Verify & Edit Extracted Data" if not is_bm else "Semak & Edit Data Diekstrak"
            ))
            st.caption(
                "Review the extracted information and correct any errors before saving." if not is_bm
                else "Semak maklumat yang diekstrak dan betulkan sebarang kesilapan sebelum menyimpan."
            )

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

            # Save button
            if st.button(
                "✅ Confirm & Save Transaction" if not is_bm else "✅ Sahkan & Simpan Transaksi",
                key="btn_save_ocr",
                type="primary",
                use_container_width=True
            ):
                if not merch.strip():
                    st.error(
                        "Merchant name cannot be empty." if not is_bm
                        else "Nama peniaga tidak boleh kosong."
                    )
                elif amt <= 0:
                    st.error(
                        "Amount must be greater than 0." if not is_bm
                        else "Jumlah mesti lebih daripada 0."
                    )
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

                    # Budget overspend check
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

                    st.toast(
                        f"✅ Saved — RM {amt:.2f} | {merch} | {cat}" if not is_bm
                        else f"✅ Disimpan — RM {amt:.2f} | {merch} | {cat}"
                    )

                    if "last_ocr_val" in st.session_state:
                        del st.session_state["last_ocr_val"]
                    st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TAB 2 — MANUAL ENTRY
    # ═══════════════════════════════════════════════════════════
    with tabs[1]:
        st.subheader(
            "Enter Spent Details Manually" if not is_bm
            else "Isi Butiran Perbelanjaan Manual"
        )

        with st.form("manual_spent_form", clear_on_submit=True):
            man_merch = st.text_input(
                "Merchant Name" if not is_bm else "Nama Peniaga",
                placeholder="e.g. Restoran Ali, Shell Petrol" if not is_bm
                            else "cth. Restoran Ali, Shell Petrol"
            )
            man_amt = st.number_input(
                "Amount (RM)" if not is_bm else "Jumlah (RM)",
                min_value=0.01, step=0.10, format="%.2f"
            )
            man_dt = st.date_input(
                "Transaction Date" if not is_bm else "Tarikh Transaksi",
                value=date.today()
            )
            man_cat = st.selectbox(
                "Category" if not is_bm else "Kategori",
                categories
            )
            man_notes = st.text_area(
                "Personal Notes (optional)" if not is_bm else "Nota Peribadi (pilihan)",
                placeholder="Any extra details..." if not is_bm else "Sebarang butiran tambahan..."
            )

            submitted = st.form_submit_button(
                "✅ Save Transaction" if not is_bm else "✅ Simpan Transaksi",
                use_container_width=True
            )

            if submitted:
                if not man_merch.strip():
                    st.error(
                        "Please enter a valid merchant name." if not is_bm
                        else "Sila masukkan nama peniaga yang sah."
                    )
                elif man_amt <= 0:
                    st.error(
                        "Amount must be greater than 0." if not is_bm
                        else "Jumlah mesti lebih daripada 0."
                    )
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

                    # Budget overspend check
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

                    st.success(
                        f"✅ Saved — RM {man_amt:.2f} added to {man_cat}" if not is_bm
                        else f"✅ Disimpan — RM {man_amt:.2f} ditambah ke {man_cat}"
                    )
                    time.sleep(0.8)
                    st.rerun()