from neo4j import GraphDatabase
try:
    print("Testing local neo4j with markdown-talent...")
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'markdown-talent'))
    cnt = driver.session().run('RETURN 1').single()[0]
    print(f"Local SUCCESS: {cnt}")
except Exception as e:
    print(f"Local FAILED: {e}")
