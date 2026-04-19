from neo4j import GraphDatabase
URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'toss1234')
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        result = session.run('MATCH (c:Candidate)-[r]->(s:Skill) RETURN c.name as cname, type(r) as rtype, r.raw_weight as w, s.name as sname LIMIT 5')
        for record in result:
            print(f"({record['cname']}) -[{record['rtype']}: {record['w']}]-> ({record['sname']})")
