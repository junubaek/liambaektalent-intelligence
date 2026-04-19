import sqlite3
import json
import re

def check_bad_names():
    conn = sqlite3.connect('candidates.db')
    c = conn.execute('SELECT id, name_kr FROM candidates').fetchall()
    
    bad = []
    for cid, name in c:
        if not name: continue
        pure = re.sub(r'[^가-힣]', '', name)
        
        # Conditions for a "suspicious" name
        if len(pure) < 2 or len(pure) > 4:
            bad.append(name)
        elif any(x in name for x in ['팀장', '매니저', '개발', '엔지니어', '프로필', '이력', '디자인', '기획', '마케팅', '대표', '대리']):
            bad.append(name)
            
    with open('bad_names.json', 'w', encoding='utf-8') as f:
        json.dump(bad, f, ensure_ascii=False, indent=2)
        
if __name__ == "__main__":
    check_bad_names()
