import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

from jd_compiler import api_search_v8
from neo4j import GraphDatabase

def main():
    try:
        with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
            ds = json.load(f)
    except Exception as e:
        print(f"Error loading: {e}")
        return

    queries_dict = {}
    for item in ds:
        q = item.get('jd_query')
        name = item.get('candidate_name')
        if not q or not name: continue
        clean_name = name.split('(')[0].replace(' ', '').strip()
        if q not in queries_dict:
            queries_dict[q] = set()
        queries_dict[q].add(clean_name)

    print("━━━━━━━━━━━━━━━━━━━━\n1. 0.0 쿼리 분석 실행\n━━━━━━━━━━━━━━━━━━━━")
    
    zero_queries = []
    results = []

    # Identify 0.0 queries quickly
    for q, pos_names in queries_dict.items():
        try:
            res = api_search_v8(q)
            matched = res.get('matched', [])[:10]
            
            hit = False
            top3 = []
            for i, m in enumerate(matched):
                cname = m.get('name_kr', '').split('(')[0].replace(' ', '').strip()
                if i < 3: top3.append(cname)
                if cname in pos_names:
                    hit = True
            
            if not hit:
                zero_queries.append({
                    "query": q,
                    "expected": list(pos_names),
                    "actual_top3": top3
                })
        except Exception as e:
            pass

    print(f"Total 0.0 Queries found: {len(zero_queries)}\n")
    print("형식: 쿼리 | 정답 후보자 | 실제 상위 3명")
    print("-" * 50)
    for z in zero_queries:
        print(f"{z['query']} | {z['expected']} | {z['actual_top3']}")

    # 2. Heuristic Pattern Detection
    category_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    d_cases = []
    
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

    print("\n━━━━━━━━━━━━━━━━━━━━\n2 & 3. 실패 패턴 분류 및 D 유형 검증\n━━━━━━━━━━━━━━━━━━━━")
    for z in zero_queries:
        q = z['query']
        exp = z['expected']
        
        # A. Short Acronyms
        is_acronym = False
        words = q.split()
        if any(len(w) <= 3 and w.isupper() for w in words):
            is_acronym = True

        # Check DB / Graph
        c_missing = False
        d_missing = False
        
        target_name = exp[0]  # Just check the first for brevity
        with driver.session() as session:
            # Check node existence
            res_c = session.run("MATCH (c:Candidate) WHERE c.name_kr = $name OR c.name_kr STARTS WITH $name RETURN count(c) as cnt", name=target_name)
            if res_c.single()['cnt'] == 0:
                c_missing = True
            else:
                # Check edges
                res_d = session.run("MATCH (c:Candidate)-[r]->(s:Skill) WHERE c.name_kr = $name OR c.name_kr STARTS WITH $name RETURN s.name, type(r), count(r)", name=target_name)
                edges = [record for record in res_d]
                if len(edges) == 0:
                    d_missing = True
                    d_cases.append((target_name, edges))
                elif len(edges) <= 5:
                    d_cases.append((target_name, edges)) # Track low edges too

        if c_missing:
            category_counts['C'] += 1
        elif d_missing:
            category_counts['D'] += 1
        elif is_acronym:
            category_counts['A'] += 1
        elif " " in q and len(words) >= 4:
            category_counts['B'] += 1
        else:
            category_counts['E'] += 1

    print(f"유형별 분류 건수:")
    print(f"A (약어 쿼리): {category_counts['A']}건")
    print(f"B (범용 키워드 혼합): {category_counts['B']}건")
    print(f"C (DB 자체 누락): {category_counts['C']}건")
    print(f"D (그래프 엣지 미매핑): {category_counts['D']}건")
    print(f"E (기타/복합): {category_counts['E']}건")
    
    print("\n[D 유형 상세 (엣지가 없거나 극도로 적은 케이스)]")
    if not d_cases: print("없음")
    for name, edges in d_cases:
        print(f" - {name} : 엣지 {len(edges)}개")
    
    driver.close()

if __name__ == '__main__':
    main()
