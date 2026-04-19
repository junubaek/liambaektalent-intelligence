import sys
import io
import logging
from jd_compiler import parse_jd_to_json, prefilter_candidates, expand_jd_keywords
from neo4j import GraphDatabase

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

def find_rank():
    jd_text = "IPO/펀딩 대비 자금 담당자 6년차 자금 Treasury Cash FX 환리스크"
    
    parsed = parse_jd_to_json(jd_text)
    extracted_conditions = parsed.get("conditions", [])
    min_years = parsed.get("min_years", 0)
    expanded_jd = expand_jd_keywords(jd_text)
    
    # 1. TF-IDF
    top_100_names = prefilter_candidates(expanded_jd, num_candidates=300)
    
    # 2. Cypher
    uri = "neo4j://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    mandatory_skills = []
    optional_skills = []
    for cond in extracted_conditions:
        if cond.get('is_mandatory'):
            mandatory_skills.append(cond['skill'])
        else:
            optional_skills.append(cond['skill'])
            
    cypher = "MATCH (c:Candidate)\nWHERE c.name IN $names\n"
    if min_years > 0:
        cypher += f"  AND (c.total_years IS NULL OR c.total_years >= {min_years})\n"
        
    all_skills = mandatory_skills + optional_skills
    for i, req in enumerate(all_skills):
        cypher += f"OPTIONAL MATCH (c)-[r{i}:MANAGED]->(:Skill {{name: '{req}'}})\n"
        
    cypher += "WITH c"
    for i in range(len(all_skills)):
        cypher += f", r{i}"
    cypher += ",\n"
    
    score_parts = []
    raw_matched = []
    for i, req in enumerate(all_skills):
        w = 1.0 if req in mandatory_skills else 0.8
        score_parts.append(f"(CASE WHEN r{i} IS NOT NULL THEN {w} ELSE 0.0 END)")
        raw_matched.append(f"(CASE WHEN r{i} IS NOT NULL THEN 'MANAGED:{req}' ELSE null END)")
        
    cypher += "   " + " + ".join(score_parts) + " AS total_score,\n"
    cypher += "   [" + ",".join(raw_matched) + "] AS matched_raw\n"
    cypher += "WITH c, total_score, matched_raw\n"
    
    cypher += "WHERE total_score >= 0.0\n" # FIX CUTOFF
    
    for i in range(len(mandatory_skills)):
        cypher += f"  AND r{i} IS NOT NULL\n"
        
    cypher += "RETURN c.name AS name, total_score, matched_raw\n"
    cypher += "ORDER BY total_score DESC LIMIT 300"
    
    print("\n[CYPHER QUERY]")
    print(cypher)
    print("\n[PARAMS LENGTH]")
    print(len(top_100_names))
    
    with driver.session() as session:
        results = session.run(cypher, names=top_100_names)
        records = list(results)
    driver.close()
    
    print(f"Total candidates matching mandatory rules: {len(records)}\n")
    for idx, r in enumerate(records):
        name = r['name']
        score = r['total_score']
        edges = [x for x in r['matched_raw'] if x]
        if "대중" in name or "범기" in name:
            print(f"[{idx + 1}위] {name}")
            print(f"   Score: {score}")
            print(f"   Edges: {edges}\n")

if __name__ == "__main__":
    find_rank()
