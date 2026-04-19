import os
import json
import pdfplumber
from docx import Document

PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"
FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"

def extract_text(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("docx", "doc"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""
    return ""

def main():
    files = {}
    if os.path.exists(FOLDER1):
        for f in os.listdir(FOLDER1):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER1, f)
    if os.path.exists(FOLDER2):
        for f in os.listdir(FOLDER2):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER2, f)
            
    with open("missing_candidates.txt", "r", encoding="utf-8") as f:
        missing_names = [line.strip() for line in f if line.strip()]

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            processed = json.load(f)
    except:
        processed = {}

    group_A = []

    for name in missing_names:
        filepath = files.get(name)
        if not filepath:
            continue
            
        meta = processed.get(name)
        # Optimized path
        if meta and meta.get("text_hash") == "":
            group_A.append(name)
            continue
            
        text = extract_text(filepath)
        if len(text) < 100:
            group_A.append(name)

    # Save to file
    with open("group_A_candidates.txt", "w", encoding="utf-8") as f:
        for name in group_A:
            f.write(name + "\n")
            
    print(f"저장 완료: 총 {len(group_A)}명의 A그룹 이력서 리스트 -> group_A_candidates.txt")

if __name__ == "__main__":
    main()
