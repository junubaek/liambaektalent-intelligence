import re
import os

def generate_ontology_summary(map_path):
    if not os.path.exists(map_path):
        return "Error: canonical_map.md not found."

    with open(map_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 카테고리별 섹션 추출
    sections = re.split(r'##\s+', content)
    summary = []
    
    summary.append("# 🌐 Talent Intelligence Ontology: Node-Action Matrix\n")
    summary.append("| Category | Core Nodes (Examples) | Typical Actions (Verbs) | Hierarchy Structure |")
    summary.append("| :--- | :--- | :--- | :--- |")

    for section in sections[1:]:
        lines = section.strip().split('\n')
        category = lines[0]
        
        # 노드 예시 추출
        nodes = []
        for line in lines:
            match = re.search(r'-\s+`([^`]+)`', line)
            if match:
                nodes.append(match.group(1))
            if len(nodes) >= 5: break
            
        # 액션 및 구조 추론 (파일 내용 기반)
        actions = "USED_AS_MAIN, DEVELOPED, MANAGED" # 기본 액션
        if "Finance" in category or "Strategic" in category:
            actions = "MANAGED, EXECUTED, REPORTED"
        elif "Design" in category:
            actions = "DESIGNED, PROTOTYPED"
            
        summary.append(f"| {category} | {', '.join(nodes[:3])}... | {actions} | Parent-Child / Peer |")

    return '\n'.join(summary)

if __name__ == "__main__":
    map_path = 'canonical_map.md'
    report = generate_ontology_summary(map_path)
    
    with open('ontology_action_summary.md', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Ontology Action Summary generated as ontology_action_summary.md")
