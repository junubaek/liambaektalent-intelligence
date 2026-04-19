import os
import json
import hashlib
import re
import time
import pdfplumber
from docx import Document
import win32com.client
import pythoncom

RESUME_DIR = r"C:\Users\cazam\Downloads\02_resume 전처리"
PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"
UPDATE_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\update_candidates.json"

phone_pattern = re.compile(r"010-\d{4}-\d{4}")
kr_name_pattern = re.compile(r"[가-힣]+")

def get_name_kr(raw_name):
    matches = kr_name_pattern.findall(raw_name)
    return "".join(matches) if matches else ""

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        pass
    return text

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        return ""

def extract_text_from_doc(file_path):
    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        abs_path = os.path.abspath(file_path)
        doc = word.Documents.Open(abs_path)
        text = doc.Range().Text
        doc.Close()
        word.Quit()
        return text
    except Exception as e:
        return ""

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.doc':
        return extract_text_from_doc(file_path)
    return ""

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                migrated = {name: {"text_hash": "", "name_kr": "", "phone": ""} for name in data}
                return migrated
            return data
    return {}

def detect_duplicates(name, text, processed):
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    
    for v in processed.values():
        val_hash = v.get("text_hash", "")
        if val_hash and val_hash == text_hash:
            return "HASH_DUPE", {"text_hash": text_hash, "name_kr": "", "phone": ""}
            
    name_kr = get_name_kr(name)
    phones = phone_pattern.findall(text)
    phone = phones[0] if phones else ""
    
    meta_data = {"text_hash": text_hash, "name_kr": name_kr, "phone": phone}
    
    if phone and name_kr:
        for v in processed.values():
            if v.get("phone") == phone and v.get("name_kr") == name_kr:
                return "UPDATE_DUPE", meta_data
                
    return "OK", meta_data

def main():
    print("--- 430 Resume Deduplication Pre-flight ---")
    processed = load_progress()
    files = {}
    cutoff_time = time.time() - (86400 * 30) # 30 days
    for f in os.listdir(RESUME_DIR):
        if f.lower().endswith(('.pdf', '.docx', '.doc')) and not f.startswith("~$"):
            filepath = os.path.join(RESUME_DIR, f)
            if os.path.getmtime(filepath) >= cutoff_time:
                name = os.path.splitext(f)[0]
                files[name] = filepath
            
    remaining = {k: v for k, v in files.items() if k not in processed}
    print(f"Total files: {len(files)}, Processed before: {len(processed)}, Remaining to check: {len(remaining)}")

    hash_dupes = []
    update_dupes = []
    unique_new = []

    count = 0
    total = len(remaining)
    for name, filepath in remaining.items():
        count += 1
        if count % 50 == 0:
            print(f"  -> Scanning {count}/{total}...")
        text = extract_text(filepath)
        if len(text) < 50:
            continue
            
        reason, meta = detect_duplicates(name, text, processed)
        
        if reason == "HASH_DUPE":
            hash_dupes.append(name)
            processed[name] = meta
        elif reason == "UPDATE_DUPE":
            update_dupes.append(name)
        else:
            unique_new.append(name)
            processed[name] = meta

    print(f"\n--- Results ---")
    print(f"Hash Duplicates (Exact matches): {len(hash_dupes)}")
    print(f"Update Duplicates (Same Phone+Name but Diff File/Content): {len(update_dupes)}")
    print(f"Truly Unique New Resumes: {len(unique_new)}")

    with open("preflight_unique.json", "w", encoding="utf-8") as f:
        json.dump(unique_new, f, ensure_ascii=False, indent=2)

    with open("preflight_updates.json", "w", encoding="utf-8") as f:
        json.dump(update_dupes, f, ensure_ascii=False, indent=2)
        
    print("Saved 'preflight_unique.json' and 'preflight_updates.json'")

if __name__ == "__main__":
    main()
