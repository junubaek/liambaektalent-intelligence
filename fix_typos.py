import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

from ontology_graph import CANONICAL_MAP, EDGES

# We want to merge fragmented nodes into a single standard node.
# Format: { "Bad_Node": "Good_Node" }
MERGE_PLAN = {
    # Casing issues
    "Elasticsearch": "ElasticSearch",
    
    # Snake_case vs PascalCase
    "GraphicDesign": "Graphic_Design",
    "PackageDesign": "Package_Design",
    "ProductDesign": "Product_Design",
    "Industrial_Design": "IndustrialDesign",
    "Data_Engineering": "DataEngineering",
    "UI_UX_Design": "UIUX_Design",
    "Message_Queue": "MessageQueue",
}

new_map = dict(CANONICAL_MAP)
new_edges = list(EDGES)

# 1. Remap CANONICAL_MAP Values
for k, v in list(new_map.items()):
    if v in MERGE_PLAN:
        new_map[k] = MERGE_PLAN[v]

# 2. Add bad nodes as synoyms for the good nodes if not present
for bad, good in MERGE_PLAN.items():
    if bad not in new_map:
        new_map[bad] = good

# 3. Rename edges
merged_edges = []
for src, tgt, rel, w in new_edges:
    new_src = MERGE_PLAN.get(src, src)
    new_tgt = MERGE_PLAN.get(tgt, tgt)
    if new_src == new_tgt:
        continue
    merged_edges.append((new_src, new_tgt, rel, w))

# Save the modifications
import networkx as nx
from collections import defaultdict

G = nx.DiGraph()
for src, tgt, rel, w in merged_edges:
    G.add_edge(src, tgt)

ANCHORS = {
    "Technology & Software": ["Backend", "Frontend", "DataEngineering", "DataAnalysis", "DataScience", "Sys_Software", "SW_Software", "인프라_Cloud", "DevOps"],
    "DeepTech & Hardware": ["HW_Hardware", "반도체_Semiconductor", "Robotics", "AI_Core", "MachineLearning", "DeepLearning", "NPU", "SoC"],
    "Business & Strategy": ["전략_경영기획", "사업개발_BD", "Product_Core", "ProductManager", "ProductOwner"],
    "Finance & Investment": ["재무회계", "투자_M&A", "Corporate_Finance", "Corporate_Accounting"],
    "Design": ["Design", "UIUX_Design", "BX_Design", "Graphic_Design", "Package_Design", "Product_Design"],
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
        for pred in G.predecessors(curr):
            if pred not in visited:
                visited.add(pred)
                queue.append((pred, dist+1))
    node_to_category[node] = best_cat
    return best_cat

grouped_edges = defaultdict(list)
for edge in merged_edges:
    src, tgt, rel, w = edge
    cat = get_category(src)
    grouped_edges[cat].append(edge)

clean_grouped_edges = defaultdict(list)
for cat, edges in grouped_edges.items():
    seen = set()
    for e in edges:
        pair = tuple(sorted([e[0], e[1]]))
        if pair not in seen:
            seen.add(pair)
            clean_grouped_edges[cat].append(e)

grouped_canonical = defaultdict(list)
for k, v in new_map.items():
    cat = get_category(v)
    grouped_canonical[cat].append((k, v))

with open("c:/Users/cazam/Downloads/이력서자동분석검색시스템/ontology_graph.py", "w", encoding="utf-8") as f:
    f.write("import math\n")
    f.write("import networkx as nx\n\n")
    f.write("# ── 1. Canonical Map (Structured) ────────────────────────────────────────────────────────\n\n")
    f.write("CANONICAL_MAP: dict[str, str] = {\n")
    
    for cat in sorted(grouped_canonical.keys()):
        f.write(f"    # {cat}\n")
        cat_items = grouped_canonical[cat]
        by_canon = defaultdict(list)
        for k, v in cat_items:
            by_canon[v].append(k)
        
        for canon_id in sorted(by_canon.keys()):
            keys = by_canon[canon_id]
            line = []
            for k in sorted(keys):
                line.append(f'"{k}": "{canon_id}"')
            f.write("    " + ", ".join(line) + ",\n")
        f.write("\n")
        
    f.write("}\n\n")
    f.write("# ── 2. Edge 정의 (Structured) ─────────────────────────────────────────────────────────────\n")
    f.write("EDGES: list[tuple[str, str, str, float]] = [\n")
    
    for cat in sorted(clean_grouped_edges.keys()):
        f.write(f"    # {cat}\n")
        edges = clean_grouped_edges[cat]
        edges.sort(key=lambda x: (x[0], x[1]))
        for e in edges:
            f.write(f'    ("{e[0]}", "{e[1]}", "{e[2]}", {e[3]}),\n')
        f.write("\n")
        
    f.write("]\n\n")
    
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
    return skill


if __name__ == "__main__":
    G = build_graph()
    print(f"✅ 그래프 빌드 완료: {G.number_of_nodes()} 노드 / {G.number_of_edges()} 엣지")
""")

print("Typo resolution complete.")
