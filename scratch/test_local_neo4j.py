from neo4j import GraphDatabase

LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_AUTH = ("neo4j", "toss1234")

try:
    driver = GraphDatabase.driver(LOCAL_URI, auth=LOCAL_AUTH)
    with driver.session() as s:
        cnt = s.run("MATCH (c:Candidate) RETURN count(c)").single()[0]
        print(f"Local Neo4j is RUNNING. Candidate count: {cnt}")
    driver.close()
except Exception as e:
    print("Local Neo4j is NOT running or failed to connect:", e)
