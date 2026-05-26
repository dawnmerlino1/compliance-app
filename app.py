import streamlit as st
import pandas as pd
st.write("✅ Import test bypass")
import tempfile

st.title("📊 Compliance Analyzer")

# Upload files
checklist_file = st.file_uploader("Upload Checklist", type=["pdf", "docx"])

course_files = st.file_uploader(
    "Upload Course Calendars",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# Run analysis
if st.button("Run Analysis"):

    if not checklist_file or not course_files:
        st.error("Please upload checklist and course files")

    else:
        st.write("🔄 Running analysis...")

        results = []

        # Save checklist
        with tempfile.NamedTemporaryFile(delete=False) as tmp_checklist:
            tmp_checklist.write(checklist_file.read())
            checklist_path = tmp_checklist.name

        # Process files
        for file in course_files:

            st.write(f"Processing: {file.name}")

            with tempfile.NamedTemporaryFile(delete=False) as tmp_course:
                tmp_course.write(file.read())
                course_path = tmp_course.name

            df = build_report(course_path, checklist_path)
            df["School"] = file.name

            results.append(df)

        combined = pd.concat(results)

        st.success("✅ Analysis complete")
        st.dataframe(combined)

        compliance = (combined["Status"] == "✅ Met").mean() * 100
        st.metric("Compliance Score", f"{compliance:.1f}%")
