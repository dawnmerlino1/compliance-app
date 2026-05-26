import pandas as pd
import re

# -------------------------------
# TEXT EXTRACTION
# -------------------------------
def extract_text(file_path):
    text = ""

    # PDF
    if file_path.endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
        except:
            pass

    # DOCX
    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except:
            pass

    return text.lower()


# -------------------------------
# CHECKLIST PARSING (SAFE)
# -------------------------------
def parse_checklist(text):

    if not text:
        return ["No checklist content found"]

    # Split into chunks using punctuation
    items = re.split(r'[.\n;:•\-]', text)

    # Clean + filter
    clean_items = []
    for item in items:
        item = item.strip()
        if len(item) > 20:
            clean_items.append(item)

    if not clean_items:
        clean_items = [text[:200]]

    return clean_items


# -------------------------------
# MATCHING FUNCTION
# -------------------------------
def evaluate(item, text):

    words = set(re.findall(r'\b\w+\b', text))
    item_words = re.findall(r'\b\w+\b', item)

    keywords = [w for w in item_words if len(w) > 4]

    if not keywords:
        return "❌ Not Found", 0, "", "No keywords detected", "Review checklist item"

    matches = sum(1 for w in keywords if w in words)
    score = matches / len(keywords)

    if score > 0.6:
        return "✅ Met", score, item[:100], "Clearly addressed", "No action required"
    elif score > 0.3:
        return "⚠️ Partial", score, item[:100], "Partially addressed", "Expand content"
    else:
        return "❌ Not Found", score, "", "Missing from document", "Add this content"


# -------------------------------
# MAIN REPORT BUILDER
# -------------------------------
def build_report(course_file, checklist_file):

    course_text = extract_text(course_file)
    checklist_text = extract_text(checklist_file)

    items = parse_checklist(checklist_text)

    results = []

    for item in items:

        status, score, evidence, comment, rec = evaluate(item, course_text)

        results.append({
            "Checklist Item": item,
            "Status": status,
            "Confidence": round(score, 2),
            "Evidence": evidence,
            "Comment": comment,
            "Recommendation": rec
        })

    return pd.DataFrame(results)
