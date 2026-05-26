import streamlit as st
import pandas as pd
from compliance_core import build_report
import tempfile
import traceback

# -------------------------------
# UI HEADER
# -------------------------------
st.title("📊 Compliance Analyzer")

st.write("Upload a checklist and one or more course calendar files.")

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

    # ✅ Check uploads
    if not checklist_file or not course_files:
        st.error("Please upload both checklist and course files")
    else:
        st.write("🔄 Running analysis...")

        try:
            # ✅ Debug info
            st.write("Checklist uploaded:", checklist_file.name)
            st.write("Number of course files:", len(course_files))

            results = []

            # ✅ Save checklist file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_checklist:
                tmp_checklist.write(checklist_file.read())
                checklist_path = tmp_checklist.name

            # ✅ Loop through course files
            for file in course_files:

                st.write(f"Processing file: {file.name}")

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_course:
                    tmp_course.write(file.read())
                    course_path = tmp_course.name

                df = build_report(course_path, checklist_path)

                # ✅ Add school name
                df["School"] = file.name

                results.append(df)

            # ✅ Combine results
            if results:
                combined = pd.concat(results)
            else:
                combined = pd.DataFrame()

            st.write("Rows in result:", len(combined))

            # ✅ Ensure something always shows
            if combined.empty:
                combined = pd.DataFrame([{
