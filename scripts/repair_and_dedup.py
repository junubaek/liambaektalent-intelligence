import sqlite3
import json
import re
import os
import hashlib
from neo4j import GraphDatabase

def clean_name(raw_name):
    if not raw_name: return ""
    # Remove everything after (
    name = raw_name.split('(')[0].strip()
    return name

def is_suspicious(name):
    # Check if the name looks like a real Korean/English name.
    if len(name) < 2 and not name.encode().isalpha(): # 1 char Korean is rare but possible, 0 char is bad. We skip 1 char for now unless it's english
        return True
    bad_keywords = ['미상', '이름', '지원자', 'null', '원본', '없음', '홍길동', '무보직', '컨설팅', '대학', '홀딩', '그룹']
    for b in bad_keywords:
        if b in name: return True
    # If it's pure Korean and > 4 chars, usually a job title/company
    # But some might be two-word names.
    ko_chars = re.findall(r'[가-힣]', name)
    if len(ko_chars) == len(name.replace(' ', '')) and len(ko_chars) > 4:
        return True
    return False

def extract_name_with_llm(model, raw_text, filename):
    import time
    prompt = f"""
이력서 텍스트와 파일명 정보를 줄 테니, 이 지원자의 **진짜 본명(실명)**을 찾아줘.
답변은 오직 "이름" 딱 한 단어로만 해. 
찾을 수 없다면 "미상" 이라고 대답해. 직무명, 회사명, '지원자', 'null' 등을 뽑지 마.

문서 파일명(참고용): {filename}
이력서 첫 500자:
{raw_text[:500]}
"""
    for _ in range(3):
        try:
            res = model.generate_content(prompt)
            return res.text.strip()
        except:
            time.sleep(2)
    return "미상"

def repair_names():
    print("[1] 🛠️ Name Deep Repair Started...")
    import google.generativeai as genai
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    genai.configure(api_key=secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash-8b") # Use 8b for ultra fast fast/cheap extraction if possible, or fallback to flash
    try:
        model.generate_content("test")
    except:
        model = genai.GenerativeModel("gemini-2.5-flash")
    
    conn = sqlite3.connect("candidates.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, document_hash, raw_text FROM candidates")
    rows = cur.fetchall()
    
    fixes = {}
    suspicious_count = 0
    clean_count = 0
    
    for row in rows:
        cid, old_name, doc_hash, raw_text = row
        if not old_name: old_name = ""
        cname = clean_name(old_name)
        
        needs_fix = False
        if '(' in old_name or old_name != cname:
            needs_fix = True
            
        if is_suspicious(cname) or not cname:
            cname = extract_name_with_llm(model, raw_text or "", doc_hash or "")
            suspicious_count += 1
            needs_fix = True
            
        if needs_fix and cname and cname != old_name:
            fixes[cid] = cname
            clean_count += 1

    
    print(f"   => Found {clean_count} names to fix (LLM used {suspicious_count} times). Updating SQLite...")
    
    # Update SQLite
    for cid, new_name in fixes.items():
        cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, cid))
    conn.commit()
    
    # Update Neo4j
    print("   => Syncing True Names to Neo4j...")
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # Since Neo4j keeps name property usually synced with filename, we can set name_kr property
        # Actually some candidates might match on `name_kr` property or `name`. But the ID in SQLite is NOT the Neo4j Node ID directly, wait!
        # Neo4j has property `id` which is identical to SQLite `id`.
        # c:Candidate {id: cid}  can be matched.
        for cid, new_name in fixes.items():
            session.run("MATCH (c:Candidate {id: $cid}) SET c.name_kr = $name", cid=cid, name=new_name)
    
    driver.close()
    conn.close()
    print("✅ Name Repair Complete.")
    return fixes


def deduplicate():
    print("\n[2] ✂️ Deduplication Started...")
    conn = sqlite3.connect("candidates.db")
    cur = conn.cursor()
    
    # Group by name_kr + phone
    cur.execute("SELECT id, name_kr, phone, email, created_at, length(raw_text), document_hash FROM candidates")
    rows = cur.fetchall()
    
    # Simple hash map to group
    groups = {}
    for row in rows:
        cid, name, phone, email, created_at, text_len, doc = row
        # Normalize phone
        norm_phone = phone.replace("-", "").strip() if phone else ""
        norm_name = name.strip() if name else ""
        if not norm_name: continue
        
        # Primary key for dedup: Name + (Phone or Email)
        key = None
        if norm_phone:
            key = f"{norm_name}_{norm_phone}"
        elif email:
            key = f"{norm_name}_{email}"
        else:
            # If no contact info, grouping just by name might be risky (동명이인)
            # but if we trust unique doc hash, it's fine. We skip pure name matching to be safe.
            continue
            
        if key not in groups:
            groups[key] = []
        groups[key].append({
            'id': cid, 'created': created_at, 'text_len': text_len or 0, 'doc': doc
        })
        
    dupes_to_delete = []
    
    for key, members in groups.items():
        if len(members) > 1:
            # Sort by text_len descending, then created_at descending
            members.sort(key=lambda x: (x['text_len'], x['created']), reverse=True)
            # Keep first (best), delete the rest
            best = members[0]
            redundant = members[1:]
            for r in redundant:
                dupes_to_delete.append(r['id'])
                print(f"   [Duplicate Detected] Key: {key} | Keeping: DOC {best['doc']} | Deleting: {r['id']}")

    print(f"   => Found {len(dupes_to_delete)} redundant candidate records.")
    
    if dupes_to_delete:
        print("   => Deleting from SQLite...")
        # SQLite Delete
        placeholders = ','.join(['?']*len(dupes_to_delete))
        cur.execute(f"DELETE FROM candidates WHERE id IN ({placeholders})", dupes_to_delete)
        conn.commit()
        
        print("   => Deleting from Neo4j...")
        driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
        with driver.session() as session:
            session.run(f"MATCH (c:Candidate) WHERE c.id IN $ids DETACH DELETE c", ids=dupes_to_delete)
        driver.close()
        
    conn.close()
    print(f"✅ Deduplication Complete. Removed {len(dupes_to_delete)} copies.")

if __name__ == '__main__':
    repair_names()
    deduplicate()
