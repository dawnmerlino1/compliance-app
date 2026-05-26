import pandas as pd
import re

# -------------------------------
# TEXT EXTRACTION
# -------------------------------
def extract_text(file_path):
    text = ""

    # ✅ PDF extraction (PyMuPDF)
    if file_path.endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(file_path)

            for page in doc:
                page_text = page.get_text()
                if page_text:
                    text += page_text
        except:
            pass

    # ✅ DOCX extraction
    elif file_path.endswith(".docx"):
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        except:
            pass

    return text.lower()


# -------------------------------
# CHECKLIST PARSING (KEY FIX)
# -------------------------------
def parse_checklist(checklist_text):

    if not checklist_text:
        return ["No checklist content found"]

    # Normalize text
    clean_text = checklist_text.replace("\n", " ")

    # Split into chunks using punctuation / bullets
    rough_items = re.split(r'[.;:•\-]', clean_text)

    # Further refine items
    items = []
    for item in rough_items:

        parts = re.split(r'\band\b|\bor\b', item)

        for p in parts:
            p = p.strip()

            if len(p) > 15:
                items.append(p)

    # ✅ fallback if parsing still weak
    if not items:
        items = [clean_text[:200]]

    return items


# -------------------------------
# MATCHING FUNCTION
# -------------------------------
def evaluate(item, text):

    sentences = re.split(r'(?<=[.!?])\s+', text)

    words = re.findall(r'\b\w+\b', item.lower())

    stopwords = {
        "the","and","of","to","in","for","with","a","is","on",
        "that","by","as","at","be","from","this","will","are","it","or"
    }

    keywords = [w for w in words if w not in stopwords and len(w) > 3]

    best_score = 0
    best_sentence = ""

    for s in sentences:
        s_words = set(re.findall(r'\b\w+\b', s.lower()))

        if not keywords:
            continue

        matches = sum(1 for w in keywords if w in s_words)
        score = matches / len(keywords)

        if score > best_score:
            best_score = score
            best_sentence = s.strip()

    # -------------------------------
    # CLASSIFICATION + COMMENTS
    # -------------------------------
    if best_score > 0.6:
        status = "✅ Met"
        comment = (
            "This requirement is clearly addressed in the document. "
            "The policy or procedure is sufficiently described."
        )
