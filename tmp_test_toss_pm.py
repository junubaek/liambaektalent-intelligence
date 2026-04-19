import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jd_compiler import parse_jd_to_json, expand_jd_keywords
from neo4j import GraphDatabase

def test_toss_pm():
    jd_text = "토스 정산 시스템 기획 운영을 담당할 Product Manager(PM)"
    print("--- Phase 1: Intent Extraction ---")
    conds = parse_jd_to_json(jd_text)
    print(json.dumps(conds, indent=2, ensure_ascii=False))
    
    print("\n--- Phase 2: TF-IDF with Vectorizer Fix ---")
    with open("candidates_cache_jd.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    expanded_jd = expand_jd_keywords(jd_text)
    corpus = [expanded_jd]
    valid_cands = []
    
    for c in candidates:
        corpus.append(c['summary'])
        valid_cands.append(c)
        
    # Use the fixed vectorizer
    vectorizer = TfidfVectorizer(max_features=10000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    for i, c in enumerate(valid_cands):
        c['sim'] = float(sims[i])
        
    valid_cands.sort(key=lambda x: x['sim'], reverse=True)
    
    kim_rank = -1
    for i, c in enumerate(valid_cands):
        if '김완희' in c['name']:
            kim_rank = i+1
            print(f">>> Phase 2 Result: 김완희 Rank: {kim_rank}, Sim: {c['sim']:.4f}")
            break
            
    top_100_names = [c['name'] for c in valid_cands[:100]]
    if kim_rank > 0 and kim_rank <= 100:
        print(">>> 김완희 is in Phase 2 Top 100!")
    else:
        print(">>> 김완희 is NOT in Phase 2 Top 100! Adding him manually to test Phase 3.")
        top_100_names.append('[토스인슈어런스] 김완희(Financial Systems Manager)부문')

    print("\n--- Phase 3: Neo4j Scoring (NO HURDLE) ---")
    uri = "neo4j://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    max_score = sum(cond['weight'] for cond in conds)
    if max_score == 0:
        print("NO extraction conditions!")
        return

    cypher = "MATCH (c:Candidate)\n"
    cypher += "WHERE c.name IN $names\n"
    
    for idx, cond in enumerate(conds):
        cypher += f"OPTIONAL MATCH (c)-[r{idx}:{cond['action']}]->(:Skill {{name: '{cond['skill']}'}})\n"
        
    cypher += "WITH c"
    for idx in range(len(conds)):
        cypher += f", r{idx}"
    cypher += ",\n"
    
    score_parts = []
    edges_parts = []
    for idx, cond in enumerate(conds):
        w = cond['weight']
        score_parts.append(f"(CASE WHEN r{idx} IS NOT NULL THEN {w} ELSE 0.0 END)")
        edges_parts.append(f"(CASE WHEN r{idx} IS NOT NULL THEN '{cond['action']}:{cond['skill']}' ELSE null END)")
        
    cypher += "   " + " + ".join(score_parts) + " AS total_score,\n"
    cypher += "   [" + ",".join(edges_parts) + "] AS matched_raw\n"
    
    cypher += f"WITH c, total_score, matched_raw\n"
    cypher += "RETURN c.name AS name, total_score, matched_raw\n"
    cypher += "ORDER BY total_score DESC LIMIT 200"
    
    with driver.session() as session:
        records = list(session.run(cypher, names=top_100_names))
        
    driver.close()
    
    for r in records:
        if '김완희' in r['name']:
            matched_edges = [x for x in r['matched_raw'] if x is not None]
            print(f">>> Phase 3 Result: 김완희 Raw Score = {r['total_score']:.2f} (Max: {max_score:.2f}, Threshold 60%: {max_score*0.6:.2f})")
            print(f"    Matched Edges: {matched_edges}")

if __name__ == "__main__":
    test_toss_pm()
