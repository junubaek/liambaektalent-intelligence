import json
from neo4j import GraphDatabase

def main():
    # Load Golden Dataset
    with open('golden_dataset_v4.json', 'r', encoding='utf-8') as f:
        ds = json.load(f)
    
    # Load hits from eval4
    # The hits are printed on a single line after "목록"
    hits_names = []
    with open('eval4.txt', 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if '목록 (' in line and '김' in line:
                # 꼼수: 이름들이 쉼표로 나열된 라인 찾기
                parts = line.strip().split(', ')
                for p in parts:
                    name = p.split()[-1].strip() # Get last word to strip prefixes
                    hits_names.append(name)

    print("=== 1. Top-10 Hits (Queries) ===")
    hit_queries = []
    miss_queries = []
    
    for case in ds:
        name = case['candidate_name']
        query = case['jd_query']
        
        # Check if name is in the hit line from eval4
        # We look into the original raw file manually if we have to, but let's match substring
        is_hit = False
        with open('eval4.txt', 'r', encoding='utf-8', errors='replace') as ev:
            text = ev.read()
            if name in text[text.find('3. '):text.find('4. 미발')]:
                is_hit = True
                
        if is_hit:
            hit_queries.append({"name": name, "query": query})
        else:
            miss_queries.append({"name": name, "query": query})
            
    for h in hit_queries:
        print(f"[{h['name']}] {h['query']}")
        
    print(f"\nTotal Hits Identified: {len(hit_queries)}")
    
    print("\n=== 2. Analysis for 5 Missed Cases ===")
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    
    for m in miss_queries[:5]:
        name = m['name']
        query = m['query']
        print(f"\n[Target: {name}] Query: '{query}'")
        
        # 1. Total Edges
        with driver.session() as s:
            res = s.run('MATCH (c:Candidate {name_kr:$name})-[r]->(sk:Skill) RETURN sk.name, type(r)', name=name)
            edges = [(rec['sk.name'], rec['type(r)']) for rec in res]
            print(f"  - Total Neo4j Edges: {len(edges)}")
        
            queries = query.lower().split()
            found_skills = set()
            for edge_sk, r in edges:
                sk_lower = edge_sk.lower()
                for q in queries:
                    if q in sk_lower or sk_lower in q:
                        found_skills.add(f"{edge_sk} ({r})")
            
            print(f"  - Query Keywords mapped to Edges: {list(found_skills) if found_skills else 'None'}")

if __name__ == '__main__':
    main()
