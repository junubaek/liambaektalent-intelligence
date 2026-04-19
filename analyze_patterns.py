import json
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

Q_ACTIONS = """
MATCH (c:Candidate)-[r]->(s:Skill)
RETURN type(r) AS action, count(r) AS freq
ORDER BY freq DESC
"""

Q_TOP_SKILLS = """
MATCH (c:Candidate)-[r]->(s:Skill)
RETURN s.name AS skill, count(r) AS freq
ORDER BY freq DESC
LIMIT 50
"""

Q_BOTTOM_SKILLS = """
MATCH (s:Skill)
OPTIONAL MATCH (c:Candidate)-[r]->(s)
RETURN s.name AS skill, count(r) AS freq
ORDER BY freq ASC
LIMIT 50
"""

Q_ZERO_EDGES = """
MATCH (c:Candidate)
WHERE NOT (c)-->(:Skill)
RETURN c.name AS name
"""

Q_AVG_EDGES = """
MATCH (c:Candidate)
OPTIONAL MATCH (c)-[r]->(s:Skill)
WITH c, count(r) AS edge_count
RETURN avg(edge_count) AS avg_edges, count(c) as total_candidates, sum(edge_count) as total_edges
"""

def main():
    report = {}
    
    with driver.session() as session:
        # 1. Action Frequency
        res_actions = session.run(Q_ACTIONS)
        report["actions"] = {record["action"]: record["freq"] for record in res_actions}
        
        # 2. Top 50 Skills
        res_top = session.run(Q_TOP_SKILLS)
        report["top_50_skills"] = [{"skill": r["skill"], "count": r["freq"]} for r in res_top]
        
        # 3. Bottom 50 Skills
        res_bottom = session.run(Q_BOTTOM_SKILLS)
        report["bottom_50_skills"] = [{"skill": r["skill"], "count": r["freq"]} for r in res_bottom]
        
        # 4. Candidates with 0 skill nodes
        res_zero = session.run(Q_ZERO_EDGES)
        report["zero_edge_candidates"] = [r["name"] for r in res_zero]
        
        # 5. Averge edges per candidate
        res_avg = session.run(Q_AVG_EDGES).single()
        report["metrics"] = {
            "avg_edges_per_candidate": res_avg["avg_edges"] if res_avg["avg_edges"] else 0.0,
            "total_candidates": res_avg["total_candidates"],
            "total_edges": res_avg["total_edges"]
        }

    with open("pattern_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Print summary
    print("====== Neo4j 패턴 분석 요약 ======")
    print(f"전체 후보자 수: {report['metrics']['total_candidates']}명")
    print(f"전체 엣지 수: {report['metrics']['total_edges']}개")
    print(f"후보자 1인당 평균 엣지 수: {report['metrics']['avg_edges_per_candidate']:.2f}개")
    print(f"스킬 노드가 0개인 후보자 수: {len(report['zero_edge_candidates'])}명")
    
    print("\n[액션별 빈도]")
    for act, cnt in report["actions"].items():
        print(f" - {act}: {cnt}개")

    print(f"\n[가장 많이 연결된 스킬 노드 Top 5] (총 50개는 json 참고)")
    for s in report["top_50_skills"][:5]:
        print(f" - {s['skill']} ({s['count']}번)")

    print(f"\n[가장 적게 연결된 스킬 노드 Bottom 5] (총 50개는 json 참고)")
    for s in report["bottom_50_skills"][:5]:
        print(f" - {s['skill']} ({s['count']}번)")

    print("\n분석이 완료되었습니다. 자세한 결과는 'pattern_report.json'에 저장되었습니다.")

if __name__ == "__main__":
    main()
