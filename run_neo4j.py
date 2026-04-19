from neo4j import GraphDatabase
d = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
res = d.session().run("MATCH (s:Skill) WHERE s.name =~ '.*[가-힣].*' WITH s, count{(s)<-[]-(:Candidate)} as cnt WHERE cnt >= 5 RETURN s.name, cnt ORDER BY cnt DESC")
for r in res:
    print(f'{r.get("s.name")} ({r.get("cnt")})')
d.close()
