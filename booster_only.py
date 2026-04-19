import sqlite3
import re
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP
from tqdm import tqdm

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def get_all_raw_texts():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute('SELECT name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL AND length(raw_text) > 10')
    rows = c.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

def main():
    print("Fetching raw_texts from SQLite...")
    raw_texts = get_all_raw_texts()
    
    print("Fetching all existing candidates and edges from Neo4j...")
    existing_data = {}
    with driver.session() as session:
        q = """
        MATCH (c:Candidate)
        OPTIONAL MATCH (c)-[r]->(s:Skill)
        RETURN c.name_kr AS name, c.id AS target_id, collect(DISTINCT s.name) AS skills
        """
        res = session.run(q)
        for record in res:
            name = record["name"]
            if name:
                skills_list = record["skills"]
                # Neo4j collect() ignores nulls, so empty means []
                existing_data[name] = {
                    'target_id': record["target_id"],
                    'skills': set(skills_list)
                }
    
    SCAN_KEYWORDS = list(CANONICAL_MAP.keys())
    
    new_edges_added = 0
    total_candidates_processed = 0
    total_edges_across_db = 0
    
    print(f"Total candidates to scan: {len(existing_data)}")
    
    with driver.session() as session:
        for name, data in tqdm(existing_data.items()):
            target_id = data['target_id']
            existing_skills = data['skills']
            total_edges_across_db += len(existing_skills)
            
            raw_text = raw_texts.get(name, "")
            if not raw_text:
                continue
                
            raw_lower = raw_text.lower()
            new_skills_to_add = set()
            
            for keyword in SCAN_KEYWORDS:
                # Noise reduction filters
                if len(keyword) < 4 and keyword.lower() in ["go", "ra", "si", "qa", "cdc", "aml", "pr", "ir", "md", "cv", "hr"]:
                    continue
                if len(keyword) < 2:
                    continue
                    
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, raw_lower):
                    canonical = CANONICAL_MAP[keyword]
                    if canonical not in existing_skills and canonical not in new_skills_to_add:
                        new_skills_to_add.add(canonical)
            
            if new_skills_to_add:
                # Upsert new edges
                for skill in new_skills_to_add:
                    session.run("""
                        MATCH (c:Candidate {id: $id})
                        MERGE (s:Skill {name: $skill})
                        MERGE (c)-[r:USED]->(s)
                        SET r.source = 'booster_scan', r.confidence = 1.0
                    """, id=target_id, skill=skill)
                    total_edges_across_db += 1
                    
                new_edges_added += len(new_skills_to_add)
            total_candidates_processed += 1

    print("\n[Keyword Scan Booster Summary]")
    print(f"Total Candidates Processed: {total_candidates_processed}")
    print(f"Total New 'USED' Edges Injected: {new_edges_added}")
    avg_edges = total_edges_across_db / max(1, total_candidates_processed)
    print(f"Average Edges per Candidate: {avg_edges:.2f}")

if __name__ == '__main__':
    main()
