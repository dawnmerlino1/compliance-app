import PyPDF2
import docx
import pandas as pd
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])


def evaluate(item, text):
    sentences = text.split(".")
    item_vec = model.encode(item, convert_to_tensor=True)

    best_score = 0
    best_sentence = ""

    for s in sentences:
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


def build_report(course_file, checklist_file):
    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    items = checklist_text.split("\n")

    data = []

    for item in items:
        if len(item.strip()) < 20:
            continue

        status, evidence, score = evaluate(item, course_text)

        comment = "Fully addressed." if status == "✅ Met" else "Needs improvement."

        data.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": round(score, 2),
            "Evidence": evidence,
            "Comment": comment
        })

    return pd.DataFrame(data)