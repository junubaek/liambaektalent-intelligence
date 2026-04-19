import jd_compiler
import codecs

res = jd_compiler.run_jd_compiler('IPO 대비 자금 담당자 6년차')
with codecs.open('ranking.txt', 'w', encoding='utf-8') as f:
    for i, x in enumerate(res[:20]):
        rank = i + 1
        name = x.get('name_kr')
        if not name: name = x['name']
        f.write(f"{rank}. {name} | Score: {x['total_score']}\n")

from neo4j import GraphDatabase
d = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
edges = d.execute_query('MATCH (c:Candidate)-[r]->() RETURN count(c) AS total_edges, count(DISTINCT c) AS total_cands')[0][0]
with codecs.open('ranking.txt', 'a', encoding='utf-8') as f:
    f.write(f"\nTotal Candidates: {edges['total_cands']}")
    f.write(f"\nAvg Edges: {edges['total_edges']/edges['total_cands']:.2f}\n")

print('Done!')
