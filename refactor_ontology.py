import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

try:
    from ontology_graph import CANONICAL_MAP, EDGES
except Exception as e:
    print(e)
    sys.exit(1)

from collections import defaultdict
import networkx as nx

# Build a graph to find root domains
G = nx.DiGraph()
for src, tgt, rel, w in EDGES:
    G.add_edge(src, tgt)

# We want to group nodes into broad categories.
# Let's define some anchor nodes for categories.
ANCHORS = {
    "Technology & Software": ["Backend", "Frontend", "DataEngineering", "DataAnalysis", "DataScience", "Sys_Software", "SW_Software", "인프라_Cloud", "DevOps"],
    "DeepTech & Hardware": ["HW_Hardware", "반도체_Semiconductor", "Robotics", "AI_Core", "MachineLearning", "DeepLearning", "NPU", "SoC"],
    "Business & Strategy": ["전략_경영기획", "사업개발_BD", "Product_Core", "ProductManager"],
    "Finance & Investment": ["재무회계", "투자_M&A", "Corporate_Finance", "Corporate_Accounting"],
    "Design": ["Design", "UIUX_Design", "BX_Design"],
    "HR & Corporate PR": ["조직개발_OD", "채용_리크루팅", "언론홍보_PR", "Corporate_HR"],
    "Security": ["보안_Security", "정보보안", "Cyber_Security", "Information_Security"],
    "Commerce & Logistics": ["유통", "물류_Logistics", "SCM", "Commerce_Business"],
    "Sales & Marketing": ["Sales_Core", "퍼포먼스마케팅", "브랜드마케팅", "CRM마케팅", "Marketing_Core", "Digital_Marketing"],
    "Operations & Legal": ["CX_CS", "Business_Operation", "법무_Legal", "컴플라이언스"],
    "Game & Entertainment": ["Game"],
    "Automotive & Mobility": ["AutonomousDriving", "Mobility_Platform", "Automotive_Software"],
}

node_to_category = {}

def get_category(node):
    if node in node_to_category:
        return node_to_category[node]
    
    # Simple BFS to find the closest anchor
    visited = set([node])
    queue = [(node, 0)]
    best_cat = "Other / Uncategorized"
    min_dist = 9999
    
    while queue:
        curr, dist = queue.pop(0)
        if dist > 3: continue
        
        for cat, anchors in ANCHORS.items():
            if curr in anchors:
                if dist < min_dist:
                    min_dist = dist
                    best_cat = cat
        
        for succ in G.successors(curr):
            if succ not in visited:
                visited.add(succ)
                queue.append((succ, dist+1))
                
        # Also check predecessors (what it is part_of)
        for pred in G.predecessors(curr):
            if pred not in visited:
                visited.add(pred)
                queue.append((pred, dist+1))
                
    node_to_category[node] = best_cat
    return best_cat

# Group EDGES
grouped_edges = defaultdict(list)
for edge in EDGES:
    src, tgt, rel, w = edge
    cat = get_category(src)
    grouped_edges[cat].append(edge)

# Remove duplicate edges
clean_grouped_edges = defaultdict(list)
for cat, edges in grouped_edges.items():
    seen = set()
    for e in edges:
        pair = tuple(sorted([e[0], e[1]]))
        if pair not in seen:
            seen.add(pair)
            clean_grouped_edges[cat].append(e)

# Group CANONICAL MAP
grouped_canonical = defaultdict(list)
# remove duplicates by taking the latest
clean_map = {}
for k, v in CANONICAL_MAP.items():
    clean_map[k] = v

for k, v in clean_map.items():
    cat = get_category(v)
    grouped_canonical[cat].append((k, v))

# Write the new ontology_graph.py
with open("c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py", "w", encoding="utf-8") as f:
    f.write("import math\n")
    f.write("import networkx as nx\n\n")
    f.write("# ── 1. Canonical Map (Structured) ────────────────────────────────────────────────────────\n\n")
    f.write("CANONICAL_MAP: dict[str, str] = {\n")
    
    for cat in sorted(grouped_canonical.keys()):
        f.write(f"    # {cat}\n")
        # Format 1 per line or grouped? Grouped by canonical id is better
        cat_items = grouped_canonical[cat]
        by_canon = defaultdict(list)
        for k, v in cat_items:
            by_canon[v].append(k)
        
        for canon_id, keys in by_canon.items():
            line = []
            for k in keys:
                line.append(f'"{k}": "{canon_id}"')
            f.write("    " + ", ".join(line) + ",\n")
        f.write("\n")
        
    f.write("}\n\n")
    f.write("# ── 2. Edge 정의 (Structured) ─────────────────────────────────────────────────────────────\n")
    f.write("EDGES: list[tuple[str, str, str, float]] = [\n")
    
    for cat in sorted(clean_grouped_edges.keys()):
        f.write(f"    # {cat}\n")
        edges = clean_grouped_edges[cat]
        # Sort edges by source node
        edges.sort(key=lambda x: (x[0], x[1]))
        for e in edges:
            f.write(f'    ("{e[0]}", "{e[1]}", "{e[2]}", {e[3]}),\n')
        f.write("\n")
        
    f.write("]\n\n")
    
    # Write the remaining functions...
    f.write(
"""# ── 3. 그래프 빌드 함수 ──────────────────────────────────────────────────────

def build_graph() -> nx.DiGraph:
    \"\"\"엔진이 시작할 때 한 번 호출. DiGraph 반환.\"\"\"
    G = nx.DiGraph()

    # 노드 등록 (canonical ID 기준)
    all_nodes = set(CANONICAL_MAP.values())
    for s, t, _, _ in EDGES:
        all_nodes.add(s)
        all_nodes.add(t)
    G.add_nodes_from(all_nodes)

    # 엣지 등록 (weight = 관계 강도, distance = 1/weight)
    for src, tgt, rel, w in EDGES:
        G.add_edge(src, tgt, relation=rel, weight=w, distance=round(1.0/w, 4))

    # 노드 질량 계산 (Log-scaled degree centrality)
    dc = nx.degree_centrality(G)
    for node in G.nodes:
        raw = dc[node] * len(G.nodes)
        G.nodes[node]["mass"] = round(math.log(1 + raw), 4)

    return G


def canonicalize(skill: str) -> str:
    \"\"\"이력서/JD 텍스트에서 추출된 스킬을 canonical ID로 변환.\"\"\"
    # Greedy: 긴 표현 우선 매핑
    for key in sorted(CANONICAL_MAP.keys(), key=len, reverse=True):
        if key.lower() in skill.lower():
            return CANONICAL_MAP[key]
    return skill  # 미등록 스킬은 원본 유지


if __name__ == "__main__":
    G = build_graph()
    print(f"✅ 그래프 빌드 완료: {G.number_of_nodes()} 노드 / {G.number_of_edges()} 엣지")
    print("\\n📊 노드 질량 Top 10:")
    masses = sorted(G.nodes(data="mass"), key=lambda x: x[1] or 0, reverse=True)
    for name, mass in masses[:10]:
        print(f"  {name:<25} mass={mass}")
    print("\\n🔗 NPU 인접 노드:")
    for nb in G.successors("NPU"):
        e = G["NPU"][nb]
        print(f"  NPU → {nb:<20} [{e['relation']}] weight={e['weight']}")
""")
    
    print("Refactoring complete.")
