import sqlite3
import json
import os
from neo4j import GraphDatabase
from tqdm import tqdm
from dynamic_parser_v2 import parse_resume_batch, valid_nodes
import dynamic_parser_v2

driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def save_edges_to_existing_node(name_kr, edges):
    if not edges: return
    
    with driver.session() as session:
        # 찾아야 할 대상 노드 (1개만)
        res = session.run("MATCH (c:Candidate {name_kr: $name_kr}) RETURN c.id as id LIMIT 1", name_kr=name_kr)
        record = res.single()
        if not record:
            return
        
        target_id = record['id']
        
        # 기존 엣지(액션) 일괄 삭제
        session.run("MATCH (c:Candidate {id: $id})-[r]->() DELETE r", id=target_id)
        
        # 새 엣지 인서트
        for edge in edges:
            action = getattr(edge, "action", "").upper()
            skill = getattr(edge, "skill", "")
            if not action or not skill: continue
            if skill not in valid_nodes: continue
            
            # 파이썬 neo4j 드라이버 제약으로 인해 관계 타입은 문자열 포매팅으로 주입
            session.run("""
                MATCH (c:Candidate {id: $id})
                MERGE (s:Skill {name: $skill})
                MERGE (c)-[r:`%s`]->(s)
                SET r.source = 'llm_batch_booster', r.confidence = 1.0
            """ % action, id=target_id, skill=skill)

def load_progress():
    if os.path.exists("processed_booster.json"):
        with open("processed_booster.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(data):
    with open("processed_booster.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def main():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute('SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL AND length(raw_text) > 10')
    rows = c.fetchall()
    conn.close()
    
    unique_candidates = {}
    for r in rows:
        unique_candidates[r[0]] = r[1]
    
    all_names = list(unique_candidates.keys())
    print(f"Total Candidates in SQLite: {len(all_names)}")
    
    processed = load_progress()
    batch_size = 5
    
    dynamic_parser_v2.cached_content_name = None # Clear cache boundary
    
    for i in tqdm(range(0, len(all_names), batch_size)):
        batch_names = all_names[i:i+batch_size]
        batch_dict = {}
        
        for name in batch_names:
            if name not in processed:
                batch_dict[name] = unique_candidates[name]
                
        if not batch_dict: continue
        
        parsed_results = parse_resume_batch(batch_dict)
        
        for name in batch_dict.keys():
            if name in parsed_results:
                edges = parsed_results[name]
                save_edges_to_existing_node(name, edges)
                processed[name] = True
            else:
                processed[name] = "FAILED"
                
        save_progress(processed)

if __name__ == "__main__":
    main()
