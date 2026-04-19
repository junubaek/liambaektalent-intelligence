import sqlite3
import json
import time
import os
import sys
from openai import OpenAI
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

SYSTEM_PROMPT = """당신은 IT/Tech/비즈니스 전문 이력서 AI 엔진입니다.
주어진 이력서 정보에서 후보자가 보유한 핵심 기술, 프레임워크, 도구, 업무 역량(Skill) 키워드들을 추출하세요.
그리고 해당 기술을 이력서 문맥상 어떻게 활용했는지 가장 잘 묘사하는 행동(Action)을 한 단어로 선택하세요.

[사용 가능한 액션 목록]
BUILT (개발/구축/창작)
IMPROVED (개선/최적화)
LED (리드/관리/기획)
ANALYZED (분석/연구)
MAINTAINED (운영/유지보수)
USED (단순 활용/경험)

응답은 반드시 아래 JSON 규격을 철저히 준수해야 합니다.
{
  "skills": [
    {"skill": "Python", "action": "BUILT"},
    {"skill": "데이터분석", "action": "ANALYZED"}
  ]
}
(핵심 스킬 10~15개 내외 우선 추출 요망)
"""

def get_missing_ids(c, session):
    c.execute("SELECT id FROM candidates WHERE is_duplicate=0")
    active_ids = [r[0] for r in c.fetchall()]
    
    neo4j_res = session.run("MATCH (n:Candidate) RETURN n.id as id")
    neo4j_ids = {r['id'] for r in neo4j_res}
    
    missing_ids = [i for i in active_ids if i not in neo4j_ids]
    return missing_ids

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(root_dir, "secrets.json")
    db_path = os.path.join(root_dir, "candidates.db")
    
    with open(secrets_path, "r", encoding='utf-8') as f:
        secrets = json.load(f)
        
    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
    neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    with driver.session() as session:
        missing_ids = get_missing_ids(c, session)
        print(f"[*] Found {len(missing_ids)} Missing Active Candidates in Neo4j.")
        
        if not missing_ids:
            print("Everything already synced!")
            return
            
        success_count = 0
        for i, cid in enumerate(missing_ids):
            c.execute("SELECT name_kr, email, phone, raw_text FROM candidates WHERE id=?", (cid,))
            row = c.fetchone()
            if not row: continue
            
            name, email, phone, raw_text = row
            raw_text = raw_text or ""
            clean_text = ' '.join(raw_text[:6000].split())
            
            print(f"[{i+1}/{len(missing_ids)}] Processing: {name} ({cid[:8]})")
            
            # Step 1. Get Skills via LLM
            skills_extracted = []
            if len(clean_text) > 50:
                try:
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format={ "type": "json_object" },
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"이력서 텍스트:\n{clean_text}"}
                        ]
                    )
                    parsed = json.loads(res.choices[0].message.content)
                    skills_extracted = parsed.get("skills", [])
                except Exception as e:
                    print(f"LLM Error for {name}: {e}")
            else:
                print("Skipping LLM due to extremely short text.")
            
            # Step 2. Generate Candidate Node & Edges
            merge_cand_q = """
            MERGE (c:Candidate {id: $id})
            SET c.name_kr = $name,
                c.name = $name,
                c.email = COALESCE($email, ""),
                c.phone = COALESCE($phone, "")
            """
            session.run(merge_cand_q, id=cid, name=name, email=email, phone=phone)
            
            for sa in skills_extracted:
                skill_name = str(sa.get("skill", "")).strip()
                action = str(sa.get("action", "USED")).strip().upper()
                if not skill_name: continue
                
                # Sanitize Action string to be safe for Cypher relation type
                safe_action = ''.join(c for c in action if c.isalnum() or c == '_')
                if not safe_action: safe_action = "USED"
                
                edge_q = f"""
                MATCH (c:Candidate {{id: $cid}})
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:HAS_SKILL]->(s)
                SET r.action = $action
                """
                session.run(edge_q, cid=cid, skill=skill_name, action=safe_action)
                
            success_count += 1
            
        print(f"\\n[*] Operations complete. Synced {success_count} nodes to Neo4j.")

if __name__ == '__main__':
    main()
