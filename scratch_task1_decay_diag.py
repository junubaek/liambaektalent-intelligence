from neo4j import GraphDatabase
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

uri = secrets["NEO4J_URI"]
username = secrets["NEO4J_USERNAME"]
password = secrets["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(uri, auth=(username, password))

# [1] Target Candidates
targets = ['이석현', '전형준', '강종훈', '배문성', '김정수', '윤석훈', '김완희', '김대중', '이강원', '김은형']

query_1 = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE c.name_kr IN $targets
RETURN c.name_kr as name_kr, r.last_used_year as last_used_year, count(*) as cnt
ORDER BY c.name_kr, r.last_used_year
"""

# [2] Check 0-score queries (we need to know who the target candidates for these queries are)
# Wait, let's find the target candidates for "Financial Systems Manager" and "Partner Alliance Manager" in golden_dataset_v8.json
with open("golden_dataset_v8.json", "r", encoding="utf-8") as f:
    golden = json.load(f)

zero_queries = ["Financial Systems Manager", "Partner Alliance Manager"]
zero_targets = []
for q in golden:
    if q.get("query") in zero_queries:
        print(f"Query: {q.get('query')}")
        for cand in q.get("relevant_candidates", []):
            name = cand.get("name_kr")
            cid = cand.get("candidate_id")
            zero_targets.append(name)
            print(f"  Target: {name} (ID: {cid}, Relevance: {cand.get('relevance_score')})")

query_2 = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE c.name_kr IN $zero_targets
RETURN c.name_kr as name_kr, s.name as skill_name, type(r) as rel_type, r.last_used_year as last_used_year, r.weight as weight
ORDER BY c.name_kr, r.last_used_year
"""

try:
    with driver.session() as session:
        print("\n=== [1] Target Candidate last_used_year Distributions ===")
        res1 = session.run(query_1, targets=targets)
        for row in res1:
            print(f"Candidate: {row['name_kr']} | last_used_year: {row['last_used_year']} | Count: {row['cnt']}")

        if zero_targets:
            print("\n=== [2] Zero Score Queries Candidates Edges ===")
            res2 = session.run(query_2, zero_targets=list(set(zero_targets)))
            for row in res2:
                print(f"Candidate: {row['name_kr']} | Skill: {row['skill_name']} | Rel: {row['rel_type']} | last_used_year: {row['last_used_year']} | weight: {row['weight']}")
        else:
            print("\n=== [2] No targets found in golden_dataset_v8.json for zero_queries ===")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.close()
