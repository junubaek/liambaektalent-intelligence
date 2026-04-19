import io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from neo4j import GraphDatabase

print("🚀 Neo4j 기존 동적 엣지 일괄 삭제를 시작합니다...")
driver=GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j','toss1234'))
with driver.session() as session:
    try:
        query = "MATCH (c:Candidate)-[r:BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED]->() DELETE r"
        result = session.run(query)
        summary = result.consume()
        print(f"✅ 기존 엣지 삭제 완료: {summary.counters.relationships_deleted}개의 엣지가 삭제되었습니다.")
    except Exception as e:
        print(f"❌ Error: {e}")
driver.close()
