import json
import re
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def export():
    canonical_keys_lower = {k.lower(): (k, v) for k, v in CANONICAL_MAP.items()}
    with driver.session() as session:
        query = """
        MATCH (s:Skill)<-[r]-(:Candidate)
        RETURN s.name as name, count(r) as degree
        ORDER BY degree DESC
        """
        all_skills = session.run(query)
        
        to_migrate = []
        for record in all_skills:
            name = record['name']
            degree = record['degree']
            
            lower_name = name.lower()
            if lower_name in canonical_keys_lower:
                original_key, mapped_val = canonical_keys_lower[lower_name]
                if name != mapped_val:
                    to_migrate.append((name, mapped_val, degree))

    lines = []
    lines.append("# 대상 노드 전수 확인 목록")
    lines.append("현재 V8 방식(직접 연결 엣지)을 새로운 캐노니컬 노드로 치환할 전체 목록입니다.")
    lines.append("\n| 기존 추출물(DB) | 맵핑될 새 노드명(Canonical) | 점검 필요 사항 | 연결된 후보자 수 |")
    lines.append("|---|---|---|---|")
    
    for name, mapped_val, degree in to_migrate:
        issue = []
        
        # Rule 1: Korean in canonical name
        if re.search(r'[가-힣]', mapped_val):
            issue.append("한글 노드명")
            
        # Rule 2: Languages mapped to domain constraints
        language_keywords = ['C#', 'Java', 'Python', 'Kotlin', 'C++', 'Go', 'Ruby', 'Swift', 'Javascript']
        if any(lang.lower() == name.lower() for lang in language_keywords):
            if "Game" in mapped_val or "Robot" in mapped_val or "Automotive" in mapped_val:
                issue.append("언어가 특정 도메인으로 매핑됨")
                
        # Rule 3: Framework mapped to general domain
        if "React" in name and "Frontend" in mapped_val:
            issue.append("범용 프레임워크")
            
        issue_str = ", ".join(issue) if issue else ""
        lines.append(f"| `{name}` | `{mapped_val}` | {issue_str} | {degree} |")
        
    with open("full_mappings_review.md", "w", encoding='utf-8') as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    export()
