import os
import json
import random
import pdfplumber
from docx import Document
import hashlib
import re

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
    except Exception as e:
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

    try:
        with open("update_candidates.json", "r", encoding="utf-8") as f:
            up_list = json.load(f)
    except:
        up_list = []

    group_A = []
    group_B = []
    group_C = []
    group_U = []

    existing_hashes = {}
    for k, v in processed.items():
        h = v.get("text_hash")
        if h:
            if h not in existing_hashes:
                existing_hashes[h] = []
            existing_hashes[h].append(k)
            
    for idx, name in enumerate(missing_names):
        filepath = files.get(name)
        if not filepath:
            continue
            
        text = ""
        meta = processed.get(name)
        
        if meta and meta.get("text_hash") == "":
            group_A.append((name, filepath))
            continue
            
        if name in up_list:
            group_B.append((name, filepath))
            continue

        text = extract_text(filepath)
        
        if len(text) < 100:
            group_A.append((name, filepath))
        else:
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            if name in processed:
                is_dupe = False
                if text_hash in existing_hashes and len([k for k in existing_hashes[text_hash] if k != name]) > 0:
                    is_dupe = True
                    
                if is_dupe:
                    group_B.append((name, filepath))
                else:
                    group_C.append((name, text))
            else:
                group_U.append((name, filepath))

    output = []
    output.append("================== 결과 요약 ==================")
    output.append(f"A그룹 (100자 미만 스캔본/보안PDF): {len(group_A)}명")
    output.append(f"B그룹 (해시 중복/업데이트본 스킵): {len(group_B)}명")
    output.append(f"C그룹 (Gemini 빈 배열 리턴, 실추출 실패): {len(group_C)}명")
    output.append(f"미처리 (시스템 큐 대기/파싱 안된 파일): {len(group_U)}명")
    
    output.append("\n================== C그룹 원인 파악 (샘플 5개) ==================")
    if group_C:
        samples = random.sample(group_C, min(5, len(group_C)))
        for s_idx, (name, txt) in enumerate(samples):
            output.append(f"\n[샘플 {s_idx + 1}] 후보자명: {name}")
            output.append(f"전체 글자수: {len(txt)}")
            preview = txt[:500].replace('\n', ' ')
            output.append(f"내용 앞부분: {preview}...")
    else:
        output.append("C그룹에 해당하는 후보자가 없습니다.")

    with open("classification_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

if __name__ == "__main__":
    main()
