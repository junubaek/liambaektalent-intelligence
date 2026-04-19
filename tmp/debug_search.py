import sys
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from neo4j import GraphDatabase

try:
    import jd_compiler
except ImportError:
    print("Could not import jd_compiler directly. Will try a different way.")

print("--- 1. Query JD Parsing ---")
try:
    # Attempt to parse the JD
    query = "6년차 이상 자금 담당자"
    print(f"Input Query: {query}")
    parsed_json = asyncio.run(jd_compiler.parse_jd_to_json(query))
    import json
    print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error parsing JD: {e}")

print("\n--- 2. Neo4j Edges for 김대중 ---")
try:
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE c.name_kr = '김대중'
            RETURN type(r) AS rel_type, s.name AS skill_name
            ORDER BY type(r)
        """)
        records = list(result)
        if records:
            for r in records:
                print(f"- [{r['rel_type']}] -> ({r['skill_name']})")
        else:
            print("No edges found for 김대중.")
    driver.close()
except Exception as e:
    print(f"Error querying Neo4j: {e}")

print("\nDone.")
