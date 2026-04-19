file_out = "dynamic_parser.py"

with open(file_out, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Extract lines up to line 169
new_lines = lines[:169]

new_code = """
# ── 진행상황 관리 및 중복 감지 ──────────────────────────────────
import hashlib
import re

phone_pattern = re.compile(r"010-\d{4}-\d{4}")
kr_name_pattern = re.compile(r"[가-힣]+")

def get_name_kr(raw_name):
    # Extract only Korean characters from filename
    matches = kr_name_pattern.findall(raw_name)
    return "".join(matches) if matches else ""

def detect_duplicates(name, text, processed):
    text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    
    # 1. Check Hash collision
    for v in processed.values():
        val_hash = v.get("text_hash", "")
        if val_hash and val_hash == text_hash:
            return "HASH_DUPE", {"text_hash": text_hash, "name_kr": "", "phone": ""}
            
    # 2. Check Name + Phone collision
    name_kr = get_name_kr(name)
    phones = phone_pattern.findall(text)
    phone = phones[0] if phones else ""
    
    meta_data = {"text_hash": text_hash, "name_kr": name_kr, "phone": phone}
    
    if phone and name_kr:
        for v in processed.values():
            if v.get("phone") == phone and v.get("name_kr") == name_kr:
                return "UPDATE_DUPE", meta_data
                
    return "OK", meta_data

def load_progress():
    import json, os
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Migration
                migrated = {name: {"text_hash": "", "name_kr": "", "phone": ""} for name in data}
                return migrated
            return data
    return {}

def save_progress(processed):
    import json
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

# ── 파일 목록 수집 ─────────────────────────────────
def collect_files():
    import os
    files = {}
    if os.path.exists(FOLDER1):
        for f in os.listdir(FOLDER1):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER1, f)
    if os.path.exists(FOLDER2):
        for f in os.listdir(FOLDER2):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER2, f)
    return files

# ── 메인 실행 ──────────────────────────────────────
def main():
    import time
    import json
    import os
    
    UPDATE_CANDIDATES_FILE = "update_candidates.json"
    files = collect_files()
    processed = load_progress()
    remaining = {k: v for k, v in files.items() if k not in processed}
    
    remaining = {k: v for k, v in remaining.items() if str(v).lower().endswith('.pdf') or str(v).lower().endswith('.docx')}
    
    print(f"전체: {len(files)}개 / 완료: {len(processed)}개 / 대상: {len(remaining)}개")
    
    # Batch Processing Logic
    remaining_items = list(remaining.items())
    batch_size = 5
    
    for i in tqdm(range(0, len(remaining_items), batch_size)):
        chunk = remaining_items[i : i+batch_size]
        batch_dict = {}
        batch_meta = {}
        
        for name, filepath in chunk:
            text = extract_text(filepath)
            if len(text) >= 100:
                reason, meta = detect_duplicates(name, text, processed)
                if reason == "HASH_DUPE":
                    print(f"\\n[해시 중복 감지] {name} - 스킵됨")
                    processed[name] = meta
                    continue
                elif reason == "UPDATE_DUPE":
                    print(f"\\n[업데이트 이력서 감지] {name} - 수동 확인 필요")
                    try:
                        if os.path.exists(UPDATE_CANDIDATES_FILE):
                            with open(UPDATE_CANDIDATES_FILE, "r", encoding="utf-8") as f:
                                up_list = json.load(f)
                        else:
                            up_list = []
                    except Exception:
                        up_list = []
                    up_list.append(name)
                    with open(UPDATE_CANDIDATES_FILE, "w", encoding="utf-8") as f:
                        json.dump(up_list, f, ensure_ascii=False, indent=2)
                    continue
                
                batch_dict[name] = text
                batch_meta[name] = meta
            else:
                processed[name] = {"text_hash": "", "name_kr": "", "phone": ""}  # skip empty
        
        if not batch_dict:
            if len(processed) % 10 < batch_size:
                save_progress(processed)
            continue
            
        print(f"\\n[Batch Parsing] {list(batch_dict.keys())}")
        batch_results = parse_resume_batch(batch_dict)
        
        # Fallback Check
        for name in batch_dict.keys():
            if name in batch_results:
                edges = batch_results[name]
                save_edges(name, edges)
                processed[name] = batch_meta.get(name, {})
            else:
                # LLM Omission Fallback
                print(f"\\n[Fallback] {name} 누락 감지. 개별 처리 재시도...")
                edges = parse_resume(batch_dict[name])
                save_edges(name, edges)
                processed[name] = batch_meta.get(name, {})
                
        if len(processed) % 10 < batch_size:  # Approximate save step
            save_progress(processed)
            
        time.sleep(1)
        
    save_progress(processed)
    print("완료!")

if __name__ == "__main__":
    main()
"""

with open(file_out, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
    f.write(new_code)

print("Patching dynamic_parser.py complete.")
