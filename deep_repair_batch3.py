import sqlite3
import json
from neo4j import GraphDatabase

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

rules = {
    "Chief_Financial_Officer": ["CFO", "재무임원", "최고재무책임자", "재무총괄", "재무 담당 임원"],
    "Content_Marketing": ["콘텐츠 기획", "콘텐츠 전략", "에디터", "콘텐츠 제작", "미디어 기획"],
    "B2B영업": ["엔터프라이즈 영업", "법인 영업", "기업 영업", "B2B 세일즈", "대형 계약", "솔루션 영업"]
}

def build_candidates_map():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT document_hash, raw_text FROM candidates WHERE raw_text IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    
    matches = {skill: [] for skill in rules.keys()}
    for doc_hash, text in rows:
        text_lower = text.lower()
        for skill, kws in rules.items():
            if any(kw.lower() in text_lower for kw in kws):
                matches[skill].append(doc_hash)
    return matches

def run_repair():
    print("=== Deep Repair Batch 3 (3 Nodes) ===")
    matches = build_candidates_map()
    
    with driver.session() as session:
        for skill, doc_hashes in matches.items():
            print(f"Processing {skill} ({len(doc_hashes)} candidates)...")
            count = 0
            for dh in doc_hashes:
                res = session.run("""
                    MATCH (c:Candidate {id: $dh})
                    MERGE (s:Skill {name: $skill})
                    MERGE (c)-[r:MANAGED]->(s)
                    RETURN id(r)
                """, dh=dh, skill=skill)
                if res.single(): count += 1
            print(f" -> Inserted {count} edges for {skill}")

        print("\n=== Edge Counts per Node ===")
        for skill in rules.keys():
            res = session.run("MATCH ()-[r]->(s:Skill {name: $skill}) RETURN count(r) as cnt", skill=skill)
            cnt = res.single()['cnt']
            print(f" - {skill}: {cnt} 엣지")

if __name__ == "__main__":
    run_repair()
