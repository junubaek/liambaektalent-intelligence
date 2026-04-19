import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jd_compiler

from jd_compiler import parse_jd_to_json
import sqlite3
import math

query = "6년차 이상 자금 담당자"
print(f"=== [쿼리] {query} ===")

jd_json = parse_jd_to_json(query)

from neo4j import GraphDatabase

uri = "bolt://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))

def check_kim_edges():
    with driver.session() as session:
        # Check all edges for 김대중
        res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) WHERE c.name_kr = '김대중' RETURN type(r) as rel, s.name as skill")
        edges = []
        for rec in res:
            edges.append(f"{rec['rel']}:{rec['skill']}")
        print("김대중님의 전체 엣지:")
        print(edges)

check_kim_edges()
                  
driver.close()
