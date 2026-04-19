import os
import json
import sqlite3
import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
DB_FILE = os.path.join(ROOT_DIR, "candidates.db")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)
neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')

# Connect Neo4j
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

print("━━━━━━━━━━━━━━━━━━━━\n1. 고스트 노드 8,449개 (Neo4j)\n━━━━━━━━━━━━━━━━━━━━")
with driver.session() as session:
    res1 = session.run("MATCH (s:Skill) WHERE NOT (s)--() RETURN count(s) as isolated_skills")
    for r in res1:
        print(f"Isolated skills (NOT (s)--()): {r['isolated_skills']}")
        
    res2 = session.run("MATCH (s:Skill) WHERE NOT ()-[]->(s) AND NOT (s)-[]->() RETURN count(s) as zero_connection_skills")
    for r in res2:
        print(f"Zero connection skills: {r['zero_connection_skills']}")
        
driver.close()

# Connect SQLite
conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n━━━━━━━━━━━━━━━━━━━━\n2. Limbo 507명 (SQLite)\n━━━━━━━━━━━━━━━━━━━━")
query_limbo = """
SELECT id, name_kr, is_neo4j_synced, is_pinecone_synced, is_parsed
FROM candidates
WHERE is_duplicate=0
AND (is_neo4j_synced=0 OR is_pinecone_synced=0)
LIMIT 10
"""
cur.execute(query_limbo)
limbo_rows = cur.fetchall()
for row in limbo_rows:
    print(f"ID: {row['id']} | Name: {row['name_kr']} | Parsed: {row['is_parsed']} | Neo4j: {row['is_neo4j_synced']} | Pinecone: {row['is_pinecone_synced']}")

print("\n━━━━━━━━━━━━━━━━━━━━\n3. name_kr 오염 5건 (SQLite)\n━━━━━━━━━━━━━━━━━━━━")
query_name = """
SELECT id, name_kr
FROM candidates
WHERE is_duplicate=0
AND (
  name_kr LIKE '%기획%'
  OR name_kr LIKE '%개발%'
  OR name_kr LIKE '%운영%'
  OR name_kr LIKE '%마케팅%'
  OR name_kr LIKE '%영업%'
  OR name_kr 고기LIKE '%총무%'
  OR name_kr LIKE '%재무%'
  OR name_kr LIKE '%인사%'
)
"""
# Fix the typo '고기LIKE' before running. Use a dynamic query or just standard SQL.
query_name = """
SELECT id, name_kr
FROM candidates
WHERE is_duplicate=0
AND (
  name_kr LIKE '%기획%'
  OR name_kr LIKE '%개발%'
  OR name_kr LIKE '%운영%'
  OR name_kr LIKE '%마케팅%'
  OR name_kr LIKE '%영업%'
  OR name_kr LIKE '%총무%'
  OR name_kr LIKE '%재무%'
  OR name_kr LIKE '%인사%'
)
"""

cur.execute(query_name)
name_rows = cur.fetchall()
for row in name_rows:
    print(f"ID: {row['id']} | Name: {row['name_kr']}")
    
conn.close()
