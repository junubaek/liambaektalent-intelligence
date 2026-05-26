from neo4j import GraphDatabase

for pwd in ['password', 'admin']:
    try:
        print(f"Testing local neo4j / {pwd}")
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', pwd))
        cnt = driver.session().run("RETURN 1").single()[0]
        print(f"SUCCESS with {pwd}: {cnt}")
        break
    except Exception as e:
        print(f"FAILED with {pwd}: {e}")
