import time
from neo4j import GraphDatabase

print("Waiting 6 seconds for rate limit to reset...")
time.sleep(6)

for pwd in ['toss1234', 'markdown-talent']:
    try:
        print(f"Testing local neo4j / {pwd}")
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', pwd))
        cnt = driver.session().run("RETURN 1").single()[0]
        print(f"SUCCESS with {pwd}: {cnt}")
        break
    except Exception as e:
        print(f"FAILED with {pwd}: {type(e).__name__} - {e}")
