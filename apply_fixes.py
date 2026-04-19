import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

from ontology_graph import CANONICAL_MAP, EDGES

CRITICAL_FIXES = {
    # Fix 1: NPU Runtime
    "NPU Runtime": "NPU",
    "NPU 소프트웨어": "NPU",
    "NPU software stack": "NPU",

    # Fix 2: 퍼포먼스마케팅
    "퍼포먼스": "퍼포먼스마케팅",
    "퍼포먼스 마케팅": "퍼포먼스마케팅",
    "performance marketing": "퍼포먼스마케팅",
    "ROAS 달성": "퍼포먼스마케팅",
    "ROAS 최적화": "퍼포먼스마케팅",
    "ROAS 개선": "퍼포먼스마케팅",
    "전환 캠페인": "퍼포먼스마케팅",
    "CPA 감소": "퍼포먼스마케팅",
    "CPA 최적화": "퍼포먼스마케팅",
    "미디어 믹스": "퍼포먼스마케팅",
    "Performance Marketing": "퍼포먼스마케팅",
    "퍼포먼스마케팅": "퍼포먼스마케팅",
    "디지털마케팅": "퍼포먼스마케팅",

    # Fix 3: AI_Core
    "AI": "AI_Core",
    "AI (Artificial Intelligence)": "AI_Core",
    "인공지능": "AI_Core",
    "Artificial Intelligence": "AI_Core",
    "ML": "MachineLearning",
    "머신러닝": "MachineLearning",
    "기계학습": "MachineLearning",
    "MachineLearning": "MachineLearning",
    "딥러닝": "DeepLearning",
    "DeepLearning": "DeepLearning",

    # Fix 4: PM
    "PM": "ProjectManager",
    "프로젝트매니저": "ProjectManager",
    "Project Manager": "ProjectManager",
    "Project Manager(PM)": "ProjectManager",
    "EPC PM": "EPC_Project_Management",
    "EPC 사업관리": "EPC_Project_Management",
    "EPC 사업 관리": "EPC_Project_Management",
    "EPC Project Management": "EPC_Project_Management",
    "PO": "ProductOwner",
    "Product Owner": "ProductOwner",
    "Product Owner(PO)": "ProductOwner",
    "프로덕트오너": "ProductOwner",
    "Platform_Product_Owner": "ProductOwner",
    "플랫폼 PO": "ProductOwner",
    "서비스 기획 총괄": "ProductOwner",
}

HIGH_FIXES = {
    # Fix 5: Backend
    "백엔드 아키텍처": "Backend",
    "Backend Architecture": "Backend",
    "백엔드 플랫폼 엔지니어링": "Backend",
    "Backend Platform Engineering": "Backend",
    "커머스 백엔드 아키텍처": "Backend",
    "Commerce Backend Architecture": "Backend",
    "백엔드 소프트웨어 엔지니어링": "Backend",
    "Backend Software Engineering": "Backend",
    "백엔드": "Backend",
    "서버개발": "Backend",
    "BE": "Backend",
    "BE(서버)": "Backend",

    # Fix 6: 마케팅기획
    "마케팅기획": "마케팅기획",
    "마케팅 기획": "마케팅기획",
    "marketing planning": "마케팅기획",
    "Marketing Planning": "마케팅기획",
    "IMC 기획": "마케팅기획",

    # Fix 7: Data_Core
    "DATA (데이터)": "Data_Core",
    "데이터": "Data_Core",
    "Data": "Data_Core",
    "데이터엔지니어": "DataEngineering",
    "데이터 엔지니어": "DataEngineering",
    "Data Engineering": "DataEngineering",
    "DE": "DataEngineering",
    "데이터파이프라인": "DataEngineering",
    "데이터 파이프라인": "DataEngineering",
    "데이터분석가": "DataAnalysis",
    "데이터 분석가": "DataAnalysis",
    "데이터분석": "DataAnalysis",
    "DA": "DataAnalysis",
    "데이터사이언티스트": "DataScience",
    "데이터 사이언티스트": "DataScience",
    "DS": "DataScience",

    # Fix 8: Sales_Core
    "영업": "Sales_Core",
    "영업 (Sales)": "Sales_Core",
    "Sales": "Sales_Core",
    "B2B영업": "B2B영업",
    "B2B": "B2B영업",
    "B2B 영업": "B2B영업",
    "해외영업": "해외영업",
    "Global Sales": "해외영업",
    "해외 영업": "해외영업",
    "기술영업": "기술영업_PreSales",
    "기술영업(Pre-sales)": "기술영업_PreSales",
    "Technical Sales": "기술영업_PreSales",
    "Pre-Sales": "기술영업_PreSales",
    "반도체 영업": "기술영업_PreSales",
    "Semiconductor Sales": "기술영업_PreSales",
}

ADDITIONAL_EDGES = [
    ("AI_Core", "MachineLearning",      "part_of", 1.5),
    ("AI_Core", "DeepLearning",         "part_of", 1.5),
    ("AI_Core", "AI_Research",          "part_of", 1.5),
    ("AI_Core", "AI_Engineering",       "part_of", 1.5),
    ("Backend", "Backend_Architecture",           "part_of", 1.5),
    ("Backend", "Backend_Platform_Engineering",   "part_of", 1.5),
    ("Backend", "Commerce_Backend_Architecture",  "part_of", 1.5),
    ("ProductOwner", "Platform_Product_Owner",    "similar_to", 1.0),
    ("Sales_Core", "B2B영업",           "part_of", 1.5),
    ("Sales_Core", "해외영업",           "part_of", 1.5),
    ("Sales_Core", "기술영업_PreSales",  "part_of", 1.5),
    ("Sales_Core", "B2C영업",           "part_of", 1.5),
]

DEPRECATED_NODES_MERGE_TARGET = {
    "Performance_Marketing": "퍼포먼스마케팅",
    "Platform_Product_Owner": "ProductOwner",
    "Semiconductor_Sales": "기술영업_PreSales",
}

# 1. Update CANONICAL_MAP
new_map = dict(CANONICAL_MAP)
for k, v in CRITICAL_FIXES.items():
    new_map[k] = v
for k, v in HIGH_FIXES.items():
    new_map[k] = v

# Remove deprecated nodes from CANONICAL_MAP values
# If any key mapped to a deprecated node, map it to the NEW node
for k, v in list(new_map.items()):
    if v in DEPRECATED_NODES_MERGE_TARGET:
        new_map[k] = DEPRECATED_NODES_MERGE_TARGET[v]

# 2. Update EDGES
new_edges = list(EDGES)
new_edges.extend(ADDITIONAL_EDGES)

# Replace deprecated nodes in edges
merged_edges = []
for src, tgt, rel, w in new_edges:
    new_src = DEPRECATED_NODES_MERGE_TARGET.get(src, src)
    new_tgt = DEPRECATED_NODES_MERGE_TARGET.get(tgt, tgt)
    # prevent self-loops
    if new_src == new_tgt:
        continue
    merged_edges.append((new_src, new_tgt, rel, w))

# Save the modifications
# Since earlier we used refactor_ontology.py to group by categories, we'll re-run refactor_ontology with updated EDGES/MAP
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
        # allow directional multi-edges with different rels if necessary, but we can deduplicate exact relationships
        # wait, let's just deduplicate exact same (src, tgt) to avoid double weighting
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
        
        # Sort cannons
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
    return skill  # 미등록 스킬은 원본 유지


if __name__ == "__main__":
    G = build_graph()
    print(f"✅ 그래프 빌드 완료: {G.number_of_nodes()} 노드 / {G.number_of_edges()} 엣지")
""")

print("Patch applied successfully.")
