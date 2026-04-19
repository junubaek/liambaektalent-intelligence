import json
import re
import sqlite3
import os

def extract_name_from_string(raw):
    if not isinstance(raw, str) or not raw.strip():
        return ""
    
    # Base normalization
    s = raw.replace('~$', '').replace('부문', '').replace('원본', '').replace('지원서', '')
    s = s.replace('.doc', '').replace('.pdf', '').replace('_영문', '').replace('_프로젝트', '')
    s = s.replace('이력서', '').replace('사본', '').replace('복사본', '')
    s = re.sub(r'\[.*?\]', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[_\-\s]+', '_', s)
    
    parts = s.split('_')
    
    possible_names = []
    for p in parts:
        pure_ko = re.sub(r'[^가-힣]', '', p)
        if len(pure_ko) in [2, 3, 4] and pure_ko == p.replace(' ', ''): 
            if not any(w in pure_ko for w in ['개발', '기획', '영업', '디자인', '담당자', '무명', '마케터', '신사업', '서버', '팀장']):
                possible_names.append(pure_ko)
                
    if possible_names:
        return possible_names[-1]
    return ""

def test_if_valid_name(s):
    pure = re.sub(r'[^가-힣]', '', s)
    if 2 <= len(pure) <= 4 and pure == s:
        if not any(w in pure for w in ['개발', '기획', '영업', '팀장', '무명', '마케터']):
            return True
    return False

def run_cleansing():
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    file_map = {}
    if os.path.exists('notion_file_map.json'):
        with open('notion_file_map.json', 'r', encoding='utf-8') as f:
            file_map = json.load(f)
            
    conn = sqlite3.connect('candidates.db')
    
    unnamed_count = 0
    fixed_count = 0
    
    for c in cache:
        orig_name = c.get('name_kr') or c.get('name') or ''
        cid = str(c.get('id')).replace('-', '')
        
        # 1. Try to extract from the current string
        clean = extract_name_from_string(orig_name)
        
        # 2. If it fails, try the Filename from Notion
        if not clean and cid in file_map:
            fname = file_map[cid].get('filename', '')
            clean = extract_name_from_string(fname)
            
        # 3. If it fails, try the raw_text from DB
        if not clean:
            row = conn.execute("SELECT raw_text FROM candidates WHERE id = ? OR id = ?", (c.get('id'), cid)).fetchone()
            if row and row[0]:
                raw = row[0][:200] # Check first 200 chars
                # Look for patterns like "이름: 홍길동" or just try to find a 3-letter word
                m = re.search(r'이\s*름\s*[:\-\s]+([가-힣]{2,4})', raw)
                if m:
                    clean = m.group(1)
                    
        # 4. If everything fails, mark as 무명
        if clean:
            c['name_kr'] = clean
            c['name'] = clean
            fixed_count += 1
        else:
            c['name_kr'] = "무명 (이력서 링크 확인)"
            c['name'] = "무명 (이력서 링크 확인)"
            unnamed_count += 1
            
    with open('candidates_cache_jd_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    print(f"Cleansing completed. Fixed: {fixed_count}, Left as 무명: {unnamed_count}")

if __name__ == "__main__":
    run_cleansing()
