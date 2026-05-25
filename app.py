import streamlit as st

st.title("✅ Compliance App Running")

st.write("If you see this page, the app is working correctly.")

# Try importing backend safely
try:
    import pandas as pd
    from compliance_core import build_report
    import tempfile
    import traceback

    st.success("✅ Backend loaded successfully")

except Exception as e:
    st.error("❌ Backend failed to load")
    st.text(str(e))

# File upload UI
checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])
course_files = st.file_uploader(
    "Upload Course Calendars",
    type=["pdf", "docx"],
