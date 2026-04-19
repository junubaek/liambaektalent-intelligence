import sqlite3
import json
import os

NAMES = ['홍기재', '오원교', '전예찬']

def prepare_reparse():
    # 1. DB에서 ID 찾기
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    ids_to_remove = set()
    for name in NAMES:
        # DB에는 이름 뒤에 직급이 붙어있을 수 있으므로 LIKE 적용, 또는 정확치 않으므로 앞부분 일치
        cur.execute("SELECT id, name_kr FROM candidates WHERE name_kr LIKE ?", (f"{name}%",))
        rows = cur.fetchall()
        for r in rows:
            ids_to_remove.add(r[0])
            print(f"Target found: {r[1]} -> ID: {r[0]}")
            
    conn.close()
    
    if not ids_to_remove:
        print("No targets found in SQLite!")
        return

    # 2. processed.json 에서 제거
    processed_file = 'processed.json'
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            try:
                processed_ids = json.load(f)
            except json.JSONDecodeError:
                processed_ids = []
                
        original_count = len(processed_ids)
        # remove Target IDs
        processed_ids = [pid for pid in processed_ids if pid not in ids_to_remove]
        new_count = len(processed_ids)
        
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(processed_ids, f)
            
        print(f"Removed {original_count - new_count} IDs from processed.json")
    else:
        print(f"{processed_file} does not exist.")
        
if __name__ == '__main__':
    prepare_reparse()
