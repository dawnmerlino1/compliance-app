import streamlit as st

st.title("✅ Compliance App Running")

st.write("If you see this page, the app is working correctly.")

# Try importing backend safely
try:
    import pandas as pd
    from compliance_core import build_report
    import tempfile

    st.success("✅ Backend loaded successfully")

except Exception as e:
    st.error("❌ Backend failed to load")
    st.text(str(e))


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
        st.write("🔄 Running analysis...")

        results = []

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_checklist:
                tmp_checklist.write(checklist_file.read())
                checklist_path = tmp_checklist.name

            for file in course_files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_course:
                    tmp_course.write(file.read())
                    course_path = tmp_course.name

                df = build_report(course_path, checklist_path)
                df["School"] = file.name
                results.append(df)

            combined = pd.concat(results)

            st.success("✅ Analysis complete!")
            st.dataframe(combined)

            compliance = (combined["Status"] == "✅ Met").mean() * 100
            st.metric("Compliance Score", f"{compliance:.1f}%")

        except Exception as e:
            st.error("❌ Error during analysis")
            st.text(str(e))
