import streamlit as st
import pandas as pd
import json
import io

st.set_page_config(page_title="JSON ↔ Excel/CSV Converter", page_icon="🔄", layout="wide")

st.title("🔄 JSON ↔ Excel/CSV Converter")
st.markdown("---")

# --- Conversion direction radio ---
direction = st.radio(
    "Select Conversion Type:",
    ["📊 Excel/CSV → JSON", "📋 JSON → Excel/CSV"],
    horizontal=True
)

st.markdown("---")

# ============================================================
# DIRECTION 1: Excel/CSV → JSON
# ============================================================
if direction == "📊 Excel/CSV → JSON":
    st.subheader("Upload Excel or CSV File")
    uploaded_file = st.file_uploader(
        "Choose an Excel (.xlsx, .xls) or CSV (.csv) file",
        type=["xlsx", "xls", "csv"],
        key="excel_uploader"
    )

    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")

        # Sheet selector for Excel
        sheet_name = None
        if uploaded_file.name.endswith((".xlsx", ".xls")):
            xls = pd.ExcelFile(uploaded_file)
            sheets = xls.sheet_names
            if len(sheets) > 1:
                sheet_name = st.selectbox("Select Sheet", sheets)
            else:
                sheet_name = sheets[0]
            uploaded_file.seek(0)

        orient = st.selectbox(
            "JSON Orientation",
            ["records", "columns", "index", "split", "table"],
            help="'records' gives a list of row objects (most common)"
        )
        indent = st.slider("JSON Indent (spaces)", 0, 8, 2)

        if st.button("⚙️ Convert to JSON", type="primary"):
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                # Convert to JSON
                json_str = df.to_json(orient=orient, indent=indent, force_ascii=False, date_format="iso")
                # Pretty-parse for display
                parsed = json.loads(json_str)
                pretty_json = json.dumps(parsed, indent=indent, ensure_ascii=False)

                st.markdown("### 📄 JSON Output")
                st.text_area("JSON Data", value=pretty_json, height=400, key="json_output")

                # Download button
                st.download_button(
                    label="⬇️ Download JSON File",
                    data=pretty_json.encode("utf-8"),
                    file_name=uploaded_file.name.rsplit(".", 1)[0] + ".json",
                    mime="application/json"
                )

            except Exception as e:
                st.error(f"❌ Error during conversion: {e}")
    else:
        st.info("👆 Upload a file to get started.")

# ============================================================
# DIRECTION 2: JSON → Excel/CSV
# ============================================================
else:
    st.subheader("Upload JSON File")
    uploaded_file = st.file_uploader(
        "Choose a JSON (.json) file",
        type=["json"],
        key="json_uploader"
    )

    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")

        output_format = st.radio(
            "Select Output Format:",
            ["Excel (.xlsx)", "CSV (.csv)"],
            horizontal=True
        )

        if st.button("⚙️ Convert to Excel/CSV", type="primary"):
            try:
                raw = json.load(uploaded_file)

                # Normalize JSON to DataFrame
                if isinstance(raw, list):
                    df = pd.json_normalize(raw)
                elif isinstance(raw, dict):
                    # Try to find a list value inside
                    list_keys = [k for k, v in raw.items() if isinstance(v, list)]
                    if list_keys:
                        df = pd.json_normalize(raw[list_keys[0]])
                        st.info(f"ℹ️ Used key **'{list_keys[0]}'** from JSON object as data source.")
                    else:
                        df = pd.json_normalize([raw])
                else:
                    st.error("❌ Unsupported JSON structure.")
                    st.stop()

                st.markdown("### 📊 Preview (first 20 rows)")
                st.dataframe(df.head(20), use_container_width=True)

                base_name = uploaded_file.name.rsplit(".", 1)[0]

                if output_format == "Excel (.xlsx)":
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Sheet1")
                    buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=buffer,
                        file_name=base_name + ".xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    csv_str = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV File",
                        data=csv_str.encode("utf-8"),
                        file_name=base_name + ".csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"❌ Error during conversion: {e}")
    else:
        st.info("👆 Upload a JSON file to get started.")

st.markdown("---")
st.caption("Built with Streamlit · Supports Excel (.xlsx/.xls), CSV, and JSON formats")
st.caption("Designed and developed by Chandar.K Bala")
