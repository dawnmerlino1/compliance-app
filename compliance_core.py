import pandas as pd
from sentence_transformers import SentenceTransformer, util

# -------------------------------
# LIGHTWEIGHT MODEL (more stable in cloud)
# -------------------------------
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')


# -------------------------------
# ROBUST TEXT EXTRACTION
# -------------------------------
def extract_text(file_path):
    text = ""

    # ✅ Try PyMuPDF first
    if file_path.endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(file_path)

            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text
        except Exception:
            pass

        # ✅ Fallback to PyPDF2
        if not text:
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text
            except Exception:
                pass

    # ✅ DOCX
    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            pass

    return text.strip()


# -------------------------------
# MATCHING FUNCTION
# -------------------------------
def evaluate(item, text):
    if not text:
        return "❌ Not Found", "", 0.0

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
# REPORT BUILDER (NO HARD FAILURE)
# -------------------------------
def build_report(course_file, checklist_file):

    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    # ✅ Prevent crash but still proceed
    if not checklist_text:
        checklist_text = "Checklist text could not be extracted."

    if not course_text:
        course_text = ""

    items = checklist_text.split("\n")

    results = []

    for item in items:
        if len(item.strip()) < 15:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = (
            "Fully addressed in document."
            if status == "✅ Met"
            else "Missing or unclear."
        )

        results.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": round(score, 2),
            "Evidence": evidence[:300],
            "Comment": comment
        })

    return pd.DataFrame(results)
