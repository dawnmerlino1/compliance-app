import streamlit as st
import pandas as pd
from compliance_core import build_report
import tempfile
import traceback

# -------------------------------
# UI HEADER
# -------------------------------
st.title("📊 Course Calendar Compliance Analyzer")
st.write("Upload a checklist and course calendar(s) to analyze compliance.")

st.success("✅ App loaded successfully")

# -------------------------------
# FILE UPLOAD
# -------------------------------
checklist_file = st.file_uploader(
    "Upload Checklist", 
    type=["pdf", "docx"]
)

course_files = st.file_uploader(
    "Upload Course Calendars",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# -------------------------------
# RUN ANALYSIS
# -------------------------------
if st.button("Run Analysis"):

    if not checklist_file or not course_files:
        st.error("Please upload both checklist and course file(s)")

    else:
        st.write("🔄 Running analysis...")

        results = []

        try:
            # Save checklist to temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_checklist:
                tmp_checklist.write(checklist_file.read())
                checklist_path = tmp_checklist.name

            # Process each course file
            for file in course_files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_course:
                    tmp_course.write(file.read())
