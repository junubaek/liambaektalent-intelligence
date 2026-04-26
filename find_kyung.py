import json
from neo4j import GraphDatabase

uri = 'neo4j+ssc://72de4959.databases.neo4j.io'
driver = GraphDatabase.driver(uri, auth=('72de4959', 'oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns'))

try:
    with driver.session() as s:
        res = s.run("""
            MATCH (c:Candidate)
            WHERE c.name_kr CONTAINS '경력기술' OR c.name CONTAINS '경력기술'
            RETURN c.id as id, c.name_kr as name_kr, c.name as name, c.parsed_career_json as careers
            LIMIT 50
        """).data()
        
        print(f'Found {len(res)} candidates.')
        for r in res:
            print(f"ID: {r['id']} | Name_KR: {r['name_kr']} | Name: {r['name']}")
            if r['careers']:
                try:
                    careers = json.loads(r['careers'])
                    for c in careers[:2]: 
                        print(f"  - Company: {c.get('company_name', '')}, Role: {c.get('role', '')}")
                except Exception as e:
                    pass
finally:
    driver.close()
