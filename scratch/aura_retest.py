from neo4j import GraphDatabase

try:
    print("Testing neo4j / pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ")
    driver = GraphDatabase.driver('neo4j+ssc://deb21ee0.databases.neo4j.io', auth=('neo4j', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'))
    cnt = driver.session().run("RETURN 1").single()[0]
    print(f"SUCCESS: {cnt}")
except Exception as e:
    print(f"FAILED: {e}")

try:
    print("Testing neo4j / markdown-talent")
    driver = GraphDatabase.driver('neo4j+ssc://deb21ee0.databases.neo4j.io', auth=('neo4j', 'markdown-talent'))
    cnt = driver.session().run("RETURN 1").single()[0]
    print(f"SUCCESS: {cnt}")
except Exception as e:
    print(f"FAILED: {e}")
