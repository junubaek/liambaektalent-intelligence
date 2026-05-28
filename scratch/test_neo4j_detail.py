import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

result = session.run('''
    MATCH (c:Candidate)
    WHERE c.name_kr = '김국현' OR c.name = '김국현'
    RETURN c.id as id, c.name_kr as name_kr, c.sector as sector, c.summary as summary, c.current_company as current_company, c.profile_summary as profile_summary
''').data()

print(f"Total nodes found for '김국현': {len(result)}")
for r in result:
    print("--- Candidate Node ---")
    print("  id:", r.get('id'))
    print("  name_kr:", r.get('name_kr'))
    print("  sector:", r.get('sector'))
    print("  current_company:", r.get('current_company'))
    print("  summary:", repr(r.get('summary')[:80] if r.get('summary') else None))
    print("  profile_summary:", repr(r.get('profile_summary')[:80] if r.get('profile_summary') else None))

driver.close()
