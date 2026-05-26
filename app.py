import streamlit as st
import pandas as pd
from compliance_core import build_report
import tempfile
import traceback

st.title("📊 Compliance Analyzer")

checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])

course_files = st.file_uploader(
    "Upload Course Calendars",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if st.button("Run Analysis"):

    if not checklist_file or not course_files:
        st.error("Upload both checklist and course files")

    else:
        try:
            results = []

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_checklist:
                tmp_checklist.write(checklist_file.read())
                checklist_path = tmp_checklist.name

            for file in course_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_course:
                    tmp_course.write(file.read())
                    course_path = tmp_course.name

                df = build_report(course_path, checklist_path)
                df["School"] = file.name
                results.append(df)

            combined = pd.concat(results)

            st.success("✅ Done!")
            st.dataframe(combined)

            compliance = (combined["Status"] == "✅ Met").mean() * 100
            st.metric("Compliance Score", f"{compliance:.1f}%")

        except Exception as e:
            st.error("Error running analysis")
            st.text(str(e))
            st.text(traceback.format_exc())
