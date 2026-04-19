import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def check_garbage():
    with driver.session() as s:
        q = """
        MATCH (s:Skill)
        WHERE s.name CONTAINS '/'
           OR s.name CONTAINS 'bit'
        RETURN s.name as name, count{(s)<-[]-()} as edge_cnt
        ORDER BY edge_cnt DESC
        LIMIT 20
        """
        results = s.run(q).data()
        for res in results:
            print(f"- {res['name']} ({res['edge_cnt']} edges)")

if __name__ == "__main__":
    check_garbage()
    driver.close()
