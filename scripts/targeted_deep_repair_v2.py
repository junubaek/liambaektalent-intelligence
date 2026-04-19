import sqlite3
import json
import re
import difflib
import time
from neo4j import GraphDatabase
import google.generativeai as genai

BAD_KEYWORDS = [
    '정보', '생명', '은행', '랩스', '건설', '기반', '테크', '그룹', '엔지', 
    '마켓', '비전', '홀딩', '교원', '구글', '굿닥', '겟차', '공간', '글로벌', 
    '농협', '동아', '두산', '롯데', '리테일', '메리츠', '메타넷', '무신사', 
    '삼성', '신세계', '아모레', '현대', '카카오', '한국', '포스코', 
    '기술', '데이터', '마케', '분석', '기획', '개발', '영업', '인사', '회계', '재무',
    '컨설팅', '대학', '미상', '이름', '지원자', 'null', '원본', '없음', '홍길동', '무보직'
]

def is_suspicious(name):
    if not name: return True
    # Strip spaces
    name = name.replace(" ", "")
    # If purely English letters, it's just an english name, but we might want to check length
    if re.match(r'^[a-zA-Z]+$', name):
        if len(name) <= 1: return True
        return False
        
    if len(name) <= 1: return True
    if len(name) >= 4: return True # Korean names rarely > 3

    for bk in BAD_KEYWORDS:
        if bk in name:
            return True
    return False

def extract_name_with_llm(model, raw_text, filename):
    prompt = f"""
이력서 텍스트와 파일명 정보를 줄 테니, 이 지원자의 **진짜 본명(실명)**을 찾아줘.
답변은 오직 "이름" 딱 한 단어로만 해. 
찾을 수 없다면 "미상" 이라고 대답해. 직무명, 회사명, 부서명, '지원자', 'null' 등을 뽑지 마.

문서 파일명(참고용): {filename}
이력서 첫 500자:
{raw_text[:500]}
"""
    for attempt in range(3):
        try:
            res = model.generate_content(prompt)
            return res.text.strip()
        except:
            time.sleep(3)
    return "미상"

def repair_phase_2():
    print("\n[Phase 2 - 1] 🛠️ Name Deep Repair (Corporate/Placeholder bypasses)...")
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    genai.configure(api_key=secrets["GEMINI_API_KEY"])
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-8b")
        model.generate_content("test")
    except:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
    conn = sqlite3.connect("candidates.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, document_hash, raw_text FROM candidates")
    rows = cur.fetchall()
    
    fixes = {}
    candidates_checked = 0
    
    # Pre-select to avoid huge loop
    targets = []
    for row in rows:
        cid, name, doc, text = row
        if is_suspicious(name):
            targets.append(row)
            
    print(f"   => Found {len(targets)} suspicious names for LLM deeper extraction.")
    
    for idx, row in enumerate(targets):
        cid, old_name, doc, raw_text = row
        new_name = extract_name_with_llm(model, raw_text or "", doc or "")
        # Clean extra brackets if LLM messed up
        if new_name and '(' in new_name:
            new_name = new_name.split('(')[0].strip()
            
        if new_name and new_name != old_name and new_name != '미상' and len(new_name) <= 10:
            fixes[cid] = new_name
            print(f"      [LLM Fixed] {old_name} -> {new_name}")
            
        if (idx+1) % 50 == 0:
            print(f"      ... processed {idx+1}/{len(targets)}")

    if fixes:
        print(f"   => Updating {len(fixes)} names to SQLite...")
        for cid, new_name in fixes.items():
            cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, cid))
        conn.commit()
        
        print("   => Syncing to Neo4j...")
        driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
        with driver.session() as session:
            for cid, new_name in fixes.items():
                session.run("MATCH (c:Candidate {id: $cid}) SET c.name_kr = $name", cid=cid, name=new_name)
        driver.close()
        
    conn.close()
    print("✅ Name Deep Repair (Phase 2-1) Complete.")


def text_similarity(text1, text2):
    if not text1 or not text2: return 0.0
    text1 = text1[:500]
    text2 = text2[:500]
    sm = difflib.SequenceMatcher(None, text1, text2)
    return sm.ratio()

def deduplicate_phase_2():
    print("\n[Phase 2 - 2] ✂️ Text-Fingerprinting Deduplication Started...")
    conn = sqlite3.connect("candidates.db")
    cur = conn.cursor()
    
    # Only pull those who share the EXACT SAME name_kr
    cur.execute("SELECT name_kr, count(*) as c FROM candidates GROUP BY name_kr HAVING count(*) > 1")
    groups_data = cur.fetchall()
    
    print(f"   => Found {len(groups_data)} candidate name groups containing potential duplicates.")
    
    dupes_to_delete = []
    
    for grp in groups_data:
        name = grp[0]
        if not name: continue
        
        cur.execute("SELECT id, raw_text, length(raw_text), created_at FROM candidates WHERE name_kr = ?", (name,))
        members = cur.fetchall()
        
        # Sort by length of raw_text descending to keep the best one
        members.sort(key=lambda x: (x[2] or 0), reverse=True)
        
        # We greedily match and group by text similarity
        absorbed = set()
        
        for i in range(len(members)):
            if i in absorbed: continue
            base = members[i]
            
            for j in range(i+1, len(members)):
                if j in absorbed: continue
                target = members[j]
                
                # Check similarity
                sim = text_similarity(base[1], target[1])
                if sim >= 0.75: # 75% similarity in first 500 chars is definitely the same resume
                    print(f"      [Identical Person Detected] Name: {name} (Similarity: {sim*100:.1f}%) | Kept: {base[0][:8]} | Deleted: {target[0][:8]}")
                    dupes_to_delete.append(target[0])
                    absorbed.add(j)

    print(f"   => Found {len(dupes_to_delete)} completely identical text redundant copies.")
    
    if dupes_to_delete:
        print("   => Deleting from SQLite...")
        placeholders = ','.join(['?']*len(dupes_to_delete))
        cur.execute(f"DELETE FROM candidates WHERE id IN ({placeholders})", dupes_to_delete)
        conn.commit()
        
        print("   => Deleting from Neo4j...")
        driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
        with driver.session() as session:
            session.run(f"MATCH (c:Candidate) WHERE c.id IN $ids DETACH DELETE c", ids=dupes_to_delete)
        driver.close()
        
    conn.close()
    print(f"✅ Text-Fingerprinting Deduplication Complete. Removed {len(dupes_to_delete)} copies.")

if __name__ == '__main__':
    repair_phase_2()
    deduplicate_phase_2()
