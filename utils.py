from PyPDF2 import PdfReader
from docx import Document
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import re

def extract_text(path):
    if path.lower().endswith(".pdf"):
        txt=""
        for p in PdfReader(path).pages:
            txt += p.extract_text() or ""
        return txt
    if path.lower().endswith(".docx"):
        return "\n".join(p.text for p in Document(path).paragraphs)
    return open(path,encoding="utf-8",errors="ignore").read()

def analyze(resume,jd):
    rw=set(re.findall(r"[A-Za-z+#.]{2,}",resume.lower()))-ENGLISH_STOP_WORDS
    jw=set(re.findall(r"[A-Za-z+#.]{2,}",jd.lower()))-ENGLISH_STOP_WORDS
    matched=sorted(rw & jw)
    missing=sorted(jw-rw)
    score=0 if not jw else round(len(matched)/len(jw)*100)
    suggestions=[f"Add '{m}' if you have experience." for m in missing[:5]]
    return {"score":score,"matched":matched,"missing":missing,"suggestions":suggestions}
