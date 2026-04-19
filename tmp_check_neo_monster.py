from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))

query = """
MATCH (c:Candidate)
WHERE c.name_kr IN ['마케터', '언론홍보', '경력기술', '자금', 'None', '김현우']
RETURN c.name as name, c.name_kr as name_kr, c.id as id
LIMIT 30
"""

with driver.session() as session:
    res = session.run(query)
    for r in res:
        name = r["name"]
        name_kr = r["name_kr"]
        cid = r.get("id")
        print(f"Name: {name} | Kr: {name_kr} | ID: {cid}")
