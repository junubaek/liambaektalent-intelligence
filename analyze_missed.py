import json
from jd_compiler import api_search_v8, get_candidates_from_cache
from neo4j import GraphDatabase

def check_case(query: str, target_name: str):
    print(f"\n========================================")
    print(f"🔍 쿼리: '{query}' | 타겟: {target_name}")
    results = api_search_v8(query)
    
    # 타겟 등수 찾기
    target_rank = -1
    target_score = 0
    for idx, r in enumerate(results.get('matched', [])):
        # 'name' is like '홍기재(수석연구원)' or just '홍기재'
        if target_name in (r.get('name') or ''):
            target_rank = idx + 1
            target_score = r['score']
            break
            
    if target_rank != -1:
        print(f"👉 타겟({target_name}) 실제 등수: {target_rank}위 (Score: {target_score:.2f})")
    else:
        print(f"👉 타겟({target_name}) 실제 등수: 50위 밖으로 밀려남 (또는 예선 탈락)")
        
    if not results.get('matched'):
        print("검색 결과가 없습니다.")
        return
        
    # 1위 정보
    top1 = results['matched'][0]
    print(f"🏆 현재 1위: {top1['name']} (Score: {top1['score']:.2f})")
    
    # 1위가 어떤 스킬로 1위가 되었는지 Neo4j에서 확인
    top1_name = top1['name']
    
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # Candidate 노드를 찾아서 나가는 엣지 확인
        q = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.name_kr CONTAINS $name
        RETURN type(r) AS rel, s.name AS skill_name
        ORDER BY s.name
        """
        # 정확한 이름 매칭이 안될 수 있으니 괄호 앞 부분만 추출
        search_name = top1_name.split('(')[0].strip()
        res = session.run(q, name=search_name)
        skills = [f"[{r['rel']}]->{r['skill_name']}" for r in res]
        
        print(f"💡 1위({search_name})의 Neo4j 보유 스킬 엣지 (총 {len(skills)}개):")
        # 출력 양이 너무 많을 수 있으니 상위 15개 정도만
        print(", ".join(skills[:15]) + ("..." if len(skills) > 15 else ""))
        
    driver.close()

if __name__ == '__main__':
    cases = [
        ('Framework Software Engineer', '홍기재'),
        ('DevOps Platform Engineer', '오원교'),
        ('NPU Library Software Engineer', '전예찬')
    ]
    for q, t in cases:
        check_case(q, t)
