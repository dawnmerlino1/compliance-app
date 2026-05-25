import PyPDF2
import docx
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')


# -------------------------------
# TEXT EXTRACTION (SAFE VERSION)
# -------------------------------
def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception:
            text = ""

    elif file_path.endswith(".docx"):
        try:
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            text = ""

    return text.strip() if text else ""


# -------------------------------
# MATCHING FUNCTION
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
# BUILD REPORT (SAFE VERSION)
# -------------------------------
def build_report(course_file, checklist_file):
    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    # ✅ Prevent crash here
    if not checklist_text:
        raise ValueError("Checklist file contains no readable text")

    if not course_text:
        raise ValueError("Course file contains no readable text")

    items = checklist_text.split("\n")

    data = []

    for item in items:
        if len(item.strip()) < 20:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = (
            "Fully addressed in document."
            if status == "✅ Met"
            else "Missing or needs clarification."
        )

        data.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": round(score, 2),
            "Evidence": evidence,
            "Comment": comment
        })

    return pd.DataFrame(data)
