import json
from neo4j import GraphDatabase

with open("search_out.txt", "w", encoding="utf-8") as f:
    try:
        d = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
        f.write("=== Neo4j Action Counts ===\n")
        f.write(f"LAUNCHED: {d.execute_query('MATCH ()-[r:LAUNCHED]->() RETURN count(r)')[0][0][0]}\n")
        f.write(f"NEGOTIATED: {d.execute_query('MATCH ()-[r:NEGOTIATED]->() RETURN count(r)')[0][0][0]}\n")
        f.write(f"GREW: {d.execute_query('MATCH ()-[r:GREW]->() RETURN count(r)')[0][0][0]}\n")
        
        f.write("\n=== Zero Node Check ===\n")
        data = json.load(open('processed.json', encoding='utf-8'))
        report = json.load(open('pattern_report.json', encoding='utf-8'))
        for n in report.get('zero_edge_candidates', [])[:5]:
            summary = ""
            for c in data:
                if c['name'] == n:
                    summary = c.get('summary', '')[:100]
                    break
            f.write(f"[{n}] -> {summary}\n")
    except Exception as e:
        f.write(str(e))
