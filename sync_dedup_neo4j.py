import sqlite3
import sys
from neo4j import GraphDatabase

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'candidates.db'

def sync_neo4j():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Get all duplicate candidate IDs to delete from Neo4j
    cur.execute("SELECT id FROM candidates WHERE is_duplicate=1")
    dup_ids = [r[0] for r in cur.fetchall()]
    print(f"1. [Neo4j 중복 제거] 삭제 대상 중복 레코드: {len(dup_ids)}개")
    
    # 2. Get master candidates that need updating/syncing
    cur.execute('''SELECT id, name_kr, current_company, sector, profile_summary, email, phone
                   FROM candidates WHERE is_duplicate=0 AND is_neo4j_synced=0''')
    master_rows = cur.fetchall()
    print(f"2. [Neo4j 마스터 갱신] 동기화 대상 마스터 레코드: {len(master_rows)}개")
    
    # Setup Neo4j connection
    # We use neo4j+ssc as in sync_aura_recovered.py
    uri = 'neo4j+ssc://deb21ee0.databases.neo4j.io'
    auth = ('deb21ee0', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ')
    
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            # A. Delete duplicate candidate nodes
            if dup_ids:
                print("   - 중복 노드 삭제 중...")
                # Process in batches of 200
                for i in range(0, len(dup_ids), 200):
                    batch = dup_ids[i:i+200]
                    session.run('''
                        MATCH (c:Candidate)
                        WHERE c.id IN $ids
                        DETACH DELETE c
                    ''', ids=batch)
                print("   ✅ Neo4j 중복 노드 삭제 완료.")
                
            # B. Upsert/Update master candidate nodes
            if master_rows:
                print("   - 마스터 노드 정보 갱신 중...")
                for i in range(0, len(master_rows), 100):
                    batch = master_rows[i:i+100]
                    data = [{'id':r[0],'name':r[1],'company':r[2],'sector':r[3],
                             'summary':r[4],'email':r[5],'phone':r[6]} for r in batch]
                    session.run('''
                        UNWIND $batch as r
                        MERGE (c:Candidate {id: r.id})
                        SET c.name_kr = r.name,
                            c.current_company = r.company,
                            c.sector = r.sector,
                            c.summary = r.summary,
                            c.email = r.email,
                            c.phone = r.phone
                    ''', batch=data)
                    print(f'     {min(i+100,len(master_rows))}/{len(master_rows)} 완료')
                print("   ✅ Neo4j 마스터 정보 동기화 완료.")
                
        driver.close()
        
        # 3. Update SQLite sync state
        cur.execute('UPDATE candidates SET is_neo4j_synced=1 WHERE is_duplicate=0 AND is_neo4j_synced=0')
        conn.commit()
        print("3. [DB 반영] SQLite is_neo4j_synced 상태 업데이트 완료")
        
    except Exception as e:
        print(f"❌ Neo4j 동기화 실패: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    sync_neo4j()
