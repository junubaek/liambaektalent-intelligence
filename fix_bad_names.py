import sqlite3
from neo4j import GraphDatabase

def fix_names():
    # 수정 내역
    updates = [
        ("33522567-1b6f-816b-9be1-dfab6815c1d3", "여기어때", "김다혜"),
        ("32122567-1b6f-81db-8cba-f128443966d4", "자동화제(콘텐츠PD)", "송영")
    ]
    
    # SQLite 수정
    print("\n--- SQLite 수정 ---")
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    for cid, old_name, new_name in updates:
        cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, cid))
        print(f"SQLite updated: {old_name} -> {new_name}")
    conn.commit()
    conn.close()
    
    # Neo4j 수정
    print("\n--- Neo4j 수정 ---")
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        for cid, old_name, new_name in updates:
            q = """
            MATCH (c:Candidate {id: $cid})
            SET c.name_kr = $new_name, c.name = $new_name
            RETURN c.id
            """
            res = session.run(q, cid=cid, new_name=new_name)
            if res.single():
                print(f"Neo4j updated: {old_name} -> {new_name}")
            else:
                print(f"Neo4j update FAIL (node not found): {old_name}")
                
    driver.close()

if __name__ == '__main__':
    fix_names()
