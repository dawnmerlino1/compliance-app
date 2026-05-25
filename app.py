import streamlit as st
import pandas as pd
from compliance_core import build_report
st.write("✅ App is running correctly")
``
st.title("Course Calendar Compliance Analyzer")

checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])
course_files = st.file_uploader("Upload Course Calendars", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("Run Analysis"):

    if not checklist_file or not course_files:
        st.error("Please upload both checklist and course file(s)")

    else:
        with open("checklist.pdf", "wb") as f:
            f.write(checklist_file.read())

        results = []

        for file in course_files:
            with open(file.name, "wb") as f:
                f.write(file.read())

            df = build_report(file.name, "checklist.pdf")
            df["School"] = file.name

            results.append(df)

        combined = pd.concat(results)

        st.dataframe(combined)

        compliance = (combined["Status"] == "✅ Met").mean() * 100
        st.metric("Compliance Score", f"{compliance:.1f}%")
