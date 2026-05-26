from neo4j import GraphDatabase

try:
    print("Testing local neo4j / toss1234")
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
    cnt = driver.session().run("RETURN 1").single()[0]
    print(f"SUCCESS: {cnt}")
except Exception as e:
    print(f"FAILED: {e}")
