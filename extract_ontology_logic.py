import re
import os

def extract_ontology_logic(file_path):
    if not os.path.exists(file_path):
        return "Error: ontology_graph.py not found."

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 관계(Action) 타입 추출
    actions = sorted(list(set(re.findall(r"type='([^']+)'", content))))
    # 필터링 (구조적 관계 제외하고 실제 동사 성격만 추출)
    verbs = [a for a in actions if a not in ['SUB_CATEGORY', 'RELATED_TO', 'HAS_ALIAS', 'PART_OF']]

    # 2. 계층 구조(Hierarchy) 추출 - 주요 부모 노드 위주
    hierarchy = re.findall(r"add_edge\('([^']+)',\s*'([^']+)',\s*type='SUB_CATEGORY'\)", content)
    parent_map = {}
    for parent, child in hierarchy:
        if parent not in parent_map: parent_map[parent] = []
        parent_map[parent].append(child)

    # 3. 리포트 생성
    report = []
    report.append("# 🗺️ Talent Intelligence Ontology: Node-Action Integration Map\n")
    
    report.append("## 🎭 1. Available Verbs (Actions)")
    report.append("시스템이 후보자의 경험을 해석할 때 사용하는 핵심 동사들입니다.\n")
    for v in verbs:
        report.append(f"*   **`{v}`**")
    
    report.append("\n## 🌲 2. Major Node Hierarchy (Parent -> Children)")
    report.append("핵심 도메인별 노드 구조입니다.\n")
    
    # 상위 10개 주요 부모 노드만 출력
    top_parents = sorted(parent_map.keys(), key=lambda x: len(parent_map[x]), reverse=True)[:15]
    for p in top_parents:
        children = ", ".join(parent_map[p][:8])
        report.append(f"*   **{p}**: {children}...")

    report.append("\n## 🧪 3. Logic: How Nodes Combine with Verbs")
    report.append("모든 노드는 위에서 정의된 동사들과 자유롭게 결합하여 후보자의 '역량 깊이'를 정의합니다.")
    report.append("> **예시**: (후보자) --- `LEAD_PROJECT` ---> `MLOps` 노드")
    report.append("> **예시**: (후보자) --- `MANAGED` ---> `Treasury_Management` 노드")

    return '\n'.join(report)

if __name__ == "__main__":
    file_path = 'ontology_graph.py'
    report = extract_ontology_logic(file_path)
    
    with open('ontology_logic_map.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Ontology Logic Map generated as ontology_logic_map.md")
