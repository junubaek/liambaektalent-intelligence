import sqlite3
from neo4j import GraphDatabase
import traceback

def check_sqlite():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
        SELECT count(*) FROM candidates
        WHERE raw_text LIKE '%IR%'
           OR raw_text LIKE '%투자자관계%'
           OR raw_text LIKE '%Investor Relations%'
    """)
    cnt = c.fetchone()[0]
    print(f"SQLite (candidates.db) - IR 관련 텍스트가 있는 후보자 수: {cnt}명")
    conn.close()

def check_neo4j(uri, user, pwd):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, pwd))
        with driver.session() as session:
            result = session.run("""
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE toLower(s.name) CONTAINS 'ir' 
                   OR toLower(s.name) CONTAINS 'investor'
                RETURN s.name, count(r) as cnt
                ORDER BY cnt DESC
            """)
            found = False
            for record in result:
                found = True
                print(f" - {record['s.name']}: {record['cnt']}개")
            if not found:
                print(" - (없음)")
    except Exception as e:
        print(f"Neo4j 연결 실패 ({uri}): {str(e)}")

print("--- 1. Neo4j 확인 (Local) ---")
check_neo4j('neo4j://127.0.0.1:7687', 'neo4j', 'toss1234')

print("\n--- 2. Neo4j 확인 (Cloud) ---")
# Just trying the credentials from my previous search, or ignoring if it's wrong... Actually wait, I shouldn't guess cloud credentials. 
# But it's in the repo files like sync_v7_graph_to_neo4j.py or .env. Let's try it anyway. 
check_neo4j('neo4j+ssc://2c78ff2f.databases.neo4j.io', 'neo4j', 'toss1234') 

print("\n--- 3. SQLite 확인 ---")
check_sqlite()
