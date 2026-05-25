import streamlit as st
import pandas as pd
from compliance_core import build_report
import tempfile

st.write("✅ App is running correctly")
st.title("Course Calendar Compliance Analyzer")

checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])
course_files = st.file_uploader(
    "Upload Course Calendars",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

if st.button("Run Analysis"):

    if not checklist_file or not course_files:
        st.error("Please upload both checklist and course file(s)")

    else:
        # Save checklist to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_checklist:
            tmp_checklist.write(checklist_file.read())
            checklist_path = tmp_checklist.name

        results = []

        for file in course_files:
            # Save each course file to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_course:
                tmp_course.write(file.read())
                course_path = tmp_course.name

            # Run analysis
            df = build_report(course_path, checklist_path)
            df["School"] = file.name

            results.append(df)

        combined = pd.concat(results)

        st.success("✅ Analysis complete!")

        st.dataframe(combined)

        compliance = (combined["Status"] == "✅ Met").mean() * 100
        st.metric("Compliance Score", f"{compliance:.1f}%")
