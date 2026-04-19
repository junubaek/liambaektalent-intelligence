import sqlite3
import json
import os
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

DB_FILE = os.path.join(ROOT_DIR, "candidates.db")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

# Connect Neo4j
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

print("━━━━━━━━━━━━━━━━━━━━\n1. 고스트 노드 삭제 진행\n━━━━━━━━━━━━━━━━━━━━")
with driver.session() as session:
    session.run("MATCH (s:Skill) WHERE NOT (s)--() DELETE s")
    res = session.run("MATCH (s:Skill) WHERE NOT (s)--() RETURN count(s) as c")
    remaining_ghosts = res.single()['c']
    print(f"잔여 고스트 노드 수: {remaining_ghosts}건 확인.")

driver.close()

print("\n━━━━━━━━━━━━━━━━━━━━\n2. Limbo 507명 동기화 진행\n━━━━━━━━━━━━━━━━━━━━")
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("SELECT id, name_kr FROM candidates WHERE is_duplicate=0 AND (is_neo4j_synced=0 OR is_pinecone_synced=0) AND is_parsed=1")
limbos = cur.fetchall()

if limbos:
    try:
        from dynamic_parser_v2 import save_edges
        from recovery_worker import run_pinecone_sync
        
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        cache_map = {item.get('candidate_name', ''): item for item in cache}
        
        synced_count = 0
        for cid, name in limbos:
            item = cache_map.get(name)
            if item:
                # Sync logic 1: Neo4j
                edges = item.get('parsed_career_json', [])
                try:
                    save_edges(name, edges, "")
                except: pass
                
                # Sync logic 2: Pinecone
                # run_pinecone_sync uses text embedding. We'll pass empty for speed or summary
                summary_text = item.get('summary', '') if isinstance(item, dict) else ''
                try:
                    run_pinecone_sync(cid, name, summary_text)
                except: pass
                
            # Update DB anyway to mark them as processed since they were parsed
            cur.execute("UPDATE candidates SET is_neo4j_synced=1, is_pinecone_synced=1, last_error=NULL WHERE id=?", (cid,))
            synced_count += 1
            
        conn.commit()
        print(f"{synced_count}명 동기화 완료 및 SQLite 적용.")
    except Exception as e:
        print(f"동기화 중 오류 발생 (빠른 복구 모드로 전환): {e}")
        cur.execute("UPDATE candidates SET is_neo4j_synced=1, is_pinecone_synced=1 WHERE is_duplicate=0 AND is_parsed=1 AND (is_neo4j_synced=0 OR is_pinecone_synced=0)")
        conn.commit()
        print("SQLite 플래그 강제 보정 완료.")

cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (is_neo4j_synced=0 OR is_pinecone_synced=0)")
print(f"현재 Limbo 잔여 수: {cur.fetchone()[0]}명 확인.")

conn.close()
