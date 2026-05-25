import streamlit as st
import pandas as pd
from compliance_core import build_report
import tempfile
import traceback

# -------------------------------
# UI
# -------------------------------
st.title("📊 Course Calendar Compliance Analyzer")
st.write("Upload a checklist and course calendar(s) to analyze compliance.")

st.success("✅ App loaded successfully")

# -------------------------------
# FILE UPLOAD
# -------------------------------
checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])

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

        try:
            results = []

            # ✅ Save checklist safely
            with tempfile.NamedTemporaryFile(delete=False) as tmp_checklist:
                tmp_checklist.write(checklist_file.read())
                checklist_path = tmp_checklist.name

            # ✅ Process each uploaded course file
            for file in course_files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_course:
                    tmp_course.write(file.read())
                    course_path = tmp_course.name

                df = build_report(course_path, checklist_path)
                df["School"] = file.name
                results.append(df)

            # ✅ Combine results
            combined = pd.concat(results)

            st.success("✅ Analysis complete!")
            st.dataframe(combined)

            # ✅ Compliance score
            compliance = (combined["Status"] == "✅ Met").mean() * 100
            st.metric("Compliance Score", f"{compliance:.1f}%")

        except Exception as e:
            st.error("❌ Error during analysis")
            st.text(str(e))
            st.text("🔍 Full error details:")
            st.text(traceback.format_exc())
