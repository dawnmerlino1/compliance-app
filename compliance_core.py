import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load NLP model
model = SentenceTransformer('all-MiniLM-L6-v2')


# -------------------------------
# ROBUST TEXT EXTRACTION
# -------------------------------
def extract_text(file_path):
    text = ""

    # ✅ Use PyMuPDF for PDF (very reliable)
    if file_path.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)

            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text

        except Exception:
            text = ""

    # ✅ Word documents
    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])

        except Exception:
            text = ""

    return text.strip() if text else ""


# -------------------------------
# NLP MATCHING
# -------------------------------
def evaluate(item, text):
    sentences = text.split(".")

    item_vec = model.encode(item, convert_to_tensor=True)

    best_score = 0
    best_sentence = ""

    for s in sentences:
        if not s.strip():
            continue

        s_vec = model.encode(s, convert_to_tensor=True)
        score = util.cos_sim(item_vec, s_vec).item()

        if score > best_score:
            best_score = score
            best_sentence = s

    if best_score > 0.55:
        status = "✅ Met"
    elif best_score > 0.40:
        status = "⚠️ Partially Met"
    else:
        status = "❌ Not Found"

    return status, best_sentence, best_score


# -------------------------------
# REPORT BUILDER
# -------------------------------
def build_report(course_file, checklist_file):

    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    # ✅ Prevent crashes + give clear errors
    if not checklist_text:
        raise ValueError("Checklist file contains no readable text")

    if not course_text:
        raise ValueError("Course file contains no readable text")

    items = checklist_text.split("\n")

    results = []

    for item in items:
        if len(item.strip()) < 20:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = (
            "Fully addressed in document."
            if status == "✅ Met"
            else "Missing or needs clarification."
        )

        results.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": round(score, 2),
            "Evidence": evidence,
            "Comment": comment
        })

    return pd.DataFrame(results)
