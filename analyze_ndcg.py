import json
from neo4j import GraphDatabase

def analyze():
    # 1. Parse eval4.txt
    hits = []
    misses = []
    mode = None
    
    with open('eval4.txt', 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if '기수직 파악' in line or '기수직 찾음' in line or '발견' in line and 'Top-10' in line and '미' not in line:
                mode = 'hit'
            elif '미발견' in line or '미발' in line and 'Top-10' in line:
                mode = 'miss'
            elif line.strip().startswith('- '):
                # parse "- 강건욱 (Layer 2/3 protocols RoCE Silicon Validation)"
                parts = line.strip()[2:].split(' (')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    query = parts[1].replace(')', '').strip()
                    if mode == 'hit':
                        hits.append({"name": name, "query": query})
                    elif mode == 'miss':
                        misses.append({"name": name, "query": query})

    print(f"=== Top-10 Hits ({len(hits)} queries) ===")
    for h in hits:
        print(f"Query: '{h['query']}' -> Target: {h['name']}")

    print("\n=== Analysis for 5 Missed Cases ===")
    
    if not misses:
        print("No misses found or parsing failed.")
        return

    sample_misses = misses[:5]
    
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    
    with driver.session() as s:
        for m in sample_misses:
            name = m['name']
            query = m['query']
            print(f"\nTarget: {name} | Query: '{query}'")
            
            # Get edges
            res = s.run('MATCH (c:Candidate {name_kr:$name})-[r]->(sk:Skill) RETURN sk.name, type(r)', name=name)
            edges = [(rec['sk.name'], rec['type(r)']) for rec in res]
            
            print(f"  - Total Neo4j Edges: {len(edges)}")
            
            queries = query.lower().split()
            found_skills = set()
            for edge_sk, r in edges:
                sk_lower = edge_sk.lower()
                for q in queries:
                    if q in sk_lower or sk_lower in q:
                        found_skills.add((q, edge_sk))
            
            print(f"  - Query Keywords mapped to Edges: {found_skills if found_skills else 'None'}")
            
    driver.close()

if __name__ == '__main__':
    analyze()
