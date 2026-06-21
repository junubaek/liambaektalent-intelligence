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

node_query = """
MATCH (c:Candidate) WHERE c.name_kr IN ['오원교', '이상헌', '이영도'] OR c.name CONTAINS 'Wongyo'
RETURN c.id as id, c.name_kr as name_kr, c.name as name, c.current_company as current_company
"""

edge_query = """
MATCH (c:Candidate)-[r]->(s:Skill)
WHERE c.name_kr IN ['오원교', '이상헌', '이영도']
RETURN c.name_kr as name_kr, type(r) as rel, s.name as skill
"""

try:
    with driver.session() as session:
        print("\n--- Neo4j Nodes in Aura ---")
        nodes_res = session.run(node_query)
        nodes_found = False
        for r in nodes_res:
            nodes_found = True
            print(f"  ID: {r['id']} | name_kr: {r['name_kr']} | name: {r['name']} | 회사: {r['current_company']}")
        if not nodes_found:
            print("  오원교, 이상헌, 이영도 노드를 찾지 못했습니다.")
            
        print("\n--- Neo4j Edges in Aura ---")
        edges_res = session.run(edge_query)
        edges_found = False
        for r in edges_res:
            edges_found = True
            print(f"  [{r['name_kr']}] {r['rel']} -> {r['skill']}")
        if not edges_found:
            print("  노드들의 엣지(연결된 스킬)를 찾지 못했습니다.")
            
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.close()
