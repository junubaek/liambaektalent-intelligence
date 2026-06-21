from neo4j import GraphDatabase
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    secrets = json.load(open('secrets.json', encoding='utf-8'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    with driver.session() as s:
        print('=== Neo4j AI/반도체/시스템 엣지 관계 세부 통계 ===')
        
        # 1. Total relationship counts by type
        rel_types = s.run('CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType').value()
        print('1. 관계 타입별 전체 엣지 수:')
        for rt in sorted(rel_types):
            cnt = s.run(f'MATCH ()-[r:{rt}]->() RETURN count(r) as c').single()['c']
            print(f'  - [{rt}]: {cnt}개')
            
        # 2. Source distribution
        print('\n2. 엣지 출처(Source) 분포:')
        sources = s.run('MATCH ()-[r]->() WHERE r.source IS NOT NULL RETURN r.source as src, count(r) as c').data()
        for src in sources:
            print(f"  - {src['src']}: {src['c']}개")

    driver.close()

if __name__ == '__main__':
    main()
