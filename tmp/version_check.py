from neo4j import GraphDatabase

driver = GraphDatabase.driver(
  'neo4j://127.0.0.1:7687',
  auth=('neo4j', 'toss1234')
)

try:
    with driver.session() as session:
        result = session.run('CALL dbms.components()')
        for r in result:
            print("----")
            print("Name:", r.get("name"))
            print("Versions:", r.get("versions"))
            print("Edition:", r.get("edition"))
except Exception as e:
    print("Error:", e)
finally:
    driver.close()
