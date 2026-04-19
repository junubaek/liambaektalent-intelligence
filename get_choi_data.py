from neo4j import GraphDatabase
import sqlite3

def check_choi():
    print("=== 1. Neo4j Edges ===")
    try:
        driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
        with driver.session() as s:
            res = s.run('MATCH (c:Candidate {name:"최호진"})-[r]->(s:Skill) RETURN s.name, type(r)')
            edges = [(rec["s.name"], rec["type(r)"]) for rec in res]
            for edge in edges:
                print(edge)
        driver.close()
    except Exception as e:
        print(f"Neo4j Error: {e}")

    print("\n=== 2. SQLite raw_text (First 1000 chars) ===")
    try:
        conn = sqlite3.connect('candidates.db')
        c = conn.cursor()
        c.execute('SELECT raw_text FROM candidates WHERE name_kr="최호진" OR raw_text LIKE "%최호진%"')
        row = c.fetchone()
        if row and row[0]:
            print(row[0][:1000])
        else:
            print("최호진 님을 DB에서 찾을 수 없거나 raw_text가 비어 있습니다.")
        conn.close()
    except Exception as e:
        print(f"SQLite Error: {e}")

if __name__ == '__main__':
    check_choi()
