import pandas as pd

# -------------------------------
# TEXT EXTRACTION (ROBUST)
# -------------------------------
def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text
        except:
            pass

    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except:
            pass

    return text.lower()


# -------------------------------
# SIMPLE MATCHING (SAFE)
# -------------------------------
def evaluate(item, text):
    if item.lower() in text:
        return "✅ Met", item, 1.0
    else:
        return "❌ Not Found", "", 0.0


# -------------------------------
# REPORT BUILDER
# -------------------------------
def build_report(course_file, checklist_file):

    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    items = checklist_text.split("\n")

    results = []

    for item in items:
        if len(item.strip()) < 5:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = (
            "Clearly present in document."
            if status == "✅ Met"
            else "Missing or unclear."
        )

        results.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": score,
            "Evidence": evidence,
            "Comment": comment
        })

    # ✅ GUARANTEE output
    if not results:
        results.append({
            "Checklist Item": "No checklist items detected",
            "Status": "❌",
            "Confidence": 0,
            "Evidence": "",
            "Comment": "Checklist parsing failed"
        })

    return pd.DataFrame(results)
