import sqlite3
import json
import os
import sys
import docx
import time

sys.stdout.reconfigure(encoding='utf-8')

def extract_docx_text(filepath):
    try:
        doc = docx.Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"Failed to read docx {filepath}: {e}")
        return ""

def run_supplement():
    print("=== Extracting Local Docx and Updating DB ===")
    
    with open('processed_step6.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
        
    zero_uids = [uid for uid, v in d.items() if v.get('edge_count', 0) == 0]
    
    db = sqlite3.connect('candidates.db')
    c = db.cursor()
    
    names_map = {}
    for uid in zero_uids:
        c.execute('SELECT name_kr FROM candidates WHERE id=?', (uid,))
        row = c.fetchone()
        if row:
            names_map[row[0]] = uid
            
    folder = r'C:\Users\cazam\Downloads\02_resume_converted_v8'
    files = os.listdir(folder) if os.path.exists(folder) else []
    
    updated_count = 0
    uids_to_reprocess = []
    
    for name, uid in names_map.items():
        for f in files:
            if name in f and f.endswith('.docx'):
                filepath = os.path.join(folder, f)
                text = extract_docx_text(filepath)
                if len(text) > 200: 
                    # Update SQLite
                    c.execute("UPDATE candidates SET raw_text=? WHERE id=?", (text, uid))
                    db.commit()
                    updated_count += 1
                    uids_to_reprocess.append(uid)
                break
                
    print(f"-> DB 업데이트 완료: {updated_count}명")
    
    # Remove from processed_step6.json so parser will run them again
    for uid in uids_to_reprocess:
        if uid in d:
            del d[uid]
            
    with open('processed_step6.json', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        
    print("-> processed_step6.json 초기화 완료. 이제 dynamic_parser_step6.py가 33명을 자동 보충합니다.")

if __name__ == "__main__":
    run_supplement()
