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
        except Exception:
            pass

    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            pass

    return text.lower()


# -------------------------------
# SIMPLE MATCHING (VERY RELIABLE)
# -------------------------------
def evaluate(item, text):

    item_clean = item.lower()

    if item_clean in text:
        return "✅ Met", item, 0.9
    else:
        return "❌ Not Found", "", 0.0


# -------------------------------
# BUILD REPORT
# -------------------------------
def build_report(course_file, checklist_file):

    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    items = checklist_text.split("\n")

    results = []

    for item in items:
        if len(item.strip()) < 15:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = (
            "Clearly present in document."
            if status == "✅ Met"
            else "Not found or needs inclusion."
        )

        results.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": score,
            "Evidence": evidence[:200],
            "Comment": comment
        })

    return pd.DataFrame(results)
``
