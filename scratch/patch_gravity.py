
import re
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

ONTOLOGY_FILE = 'ontology_graph.py'

if not os.path.exists(ONTOLOGY_FILE):
    print(f"Error: {ONTOLOGY_FILE} not found.")
    sys.exit(1)

with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*([\d.]+)\)', content)
EXISTING = set()
for s, d, r, w in edge_pattern:
    EXISTING.add((s, d))
    EXISTING.add((d, s))

print(f'기존 엣지 수: {len(edge_pattern)}')

new_edges = []
added = set()

def add(src, dst, rel, weight):
    if (src, dst) not in EXISTING and (dst, src) not in EXISTING and (src, dst) not in added:
        new_edges.append((src, dst, rel, weight))
        added.add((src, dst))

# ── 1. 마케팅 형제 노드 척력/인력 ────────────────────────
add("Performance_Marketing",         "Growth_Marketing",              "similar_to", 0.6)
add("Performance_Marketing",         "Conversion_Rate_Optimization",  "related_to", 0.4)
add("Growth_Marketing",              "Conversion_Rate_Optimization",  "related_to", 0.5)
add("Performance_Marketing",         "Content_Marketing_Strategy",    "related_to", 0.2)
add("Performance_Marketing",         "Growth_Hacking_and_Marketing",  "related_to", 0.3)
add("Growth_Marketing",              "Content_Marketing_Strategy",    "related_to", 0.2)

add("Brand_Management",              "IMC_Strategy",                  "similar_to", 0.6)
add("Brand_Management",              "Content_Marketing",             "similar_to", 0.5)
add("Brand_Management",              "B2B_Marketing_Strategy",        "related_to", 0.2)
add("Brand_Management",              "Growth_Hacking_and_Strategy",   "related_to", 0.2)
add("CRM_Strategy",                  "B2B_Marketing_Strategy",        "similar_to", 0.5)
add("B2B_Marketing_Strategy",        "Digital_Campaign_Planning",     "related_to", 0.3)

add("CRM_Marketing",                 "Data_Driven_Marketing",         "similar_to", 0.6)
add("Product_Marketing",             "CRM_Marketing",                 "related_to", 0.3)
add("Product_Marketing",             "IMC",                           "related_to", 0.3)

# ── 2. Finance 형제 노드 척력/인력 ───────────────────────
add("Mergers_and_Acquisitions",      "Valuation",                     "similar_to", 0.7)
add("Mergers_and_Acquisitions",      "IR_Management",                 "similar_to", 0.5)
add("Mergers_and_Acquisitions",      "IPO_Preparation_and_Execution", "similar_to", 0.6)
add("Mergers_and_Acquisitions",      "Treasury_Management",           "related_to", 0.2)
add("Treasury_Management",           "IR_Management",                 "related_to", 0.3)
add("Treasury_Management",           "Valuation",                     "related_to", 0.3)
add("Venture_Capital_Fundraising",   "IR_Management",                 "similar_to", 0.5)
add("Venture_Capital_Fundraising",   "Treasury_Management",           "related_to", 0.2)

add("CFO_Role",                      "Chief_Financial_Officer",       "similar_to", 0.9)
add("CFO_Role",                      "Corporate_Governance",          "similar_to", 0.5)
add("CFO_Role",                      "Chief_Compliance_Officer",      "related_to", 0.3)

# ── 3. Backend 형제 노드 척력/인력 ───────────────────────
add("Backend_Java",                  "Backend_Python",                "similar_to", 0.5)
add("Backend_Java",                  "Backend_Go",                    "similar_to", 0.4)
add("Backend_Java",                  "Backend_Node",                  "similar_to", 0.4)
add("Backend_Python",                "Backend_Go",                    "similar_to", 0.5)
add("Backend_Python",                "Backend_Node",                  "similar_to", 0.4)
add("Backend_Go",                    "Backend_Node",                  "similar_to", 0.5)
add("Fullstack",                     "Backend_Java",                  "related_to", 0.3)
add("Fullstack",                     "Backend_Python",                "related_to", 0.3)

# ── 4. Corporate_Strategy 형제 노드 척력/인력 ─────────────
add("Strategic_Investment",          "CVC_Strategy",                  "similar_to", 0.7)
add("Strategic_Investment",          "Corporate_M_and_A_Strategy",    "similar_to", 0.6)
add("Corporate_M_and_A_Strategy",    "M_and_A_Strategy",              "similar_to", 0.8)
add("Entertainment_M_and_A_Strategy","M_and_A_Strategy",              "similar_to", 0.6)
add("Strategic_Investment",          "Digital_Transformation_Strategy","related_to", 0.2)
add("CVC_Strategy",                  "Joint_Venture_Establishment",   "related_to", 0.3)
add("Investor_Relations",            "IPO_Preparation_and_Execution", "similar_to", 0.6)
add("Investor_Relations",            "Corporate_Restructuring_Strategy","related_to",0.2)
add("Global_Business_Development",   "Global_Business_Management",    "similar_to", 0.6)
add("New_Business_Development",      "Digital_Transformation_Strategy","related_to", 0.3)

# ── 5. Data_Engineering 형제 노드 척력/인력 ──────────────
add("Data_Pipeline_Construction",    "Data_Warehouse_Architecture",   "similar_to", 0.6)
add("Data_Pipeline_Construction",    "Real_Time_Data_Processing",     "similar_to", 0.6)
add("Data_Warehouse_Architecture",   "Query_Optimization_and_Monitoring","similar_to",0.5)
add("Real_Time_Data_Processing",     "Big_Data_Processing",           "similar_to", 0.6)
add("Data_Pipeline_Construction",    "Data_Core",                     "related_to", 0.3)
add("Big_Data_Processing",           "Data_Core",                     "related_to", 0.3)

# ── 6. AI/ML 형제 노드 척력/인력 ─────────────────────────
add("LLM_Inference",                 "LLM_Serving",                   "similar_to", 0.7)
add("LLM_Serving",                   "Model_Serving",                 "similar_to", 0.7)
add("LLM_Serving",                   "Distributed_Training_Inference","related_to", 0.3)
add("Model_Serving",                 "Model_Parallelism",             "related_to", 0.3)
add("AI_Research",                   "AI_Engineering",                "related_to", 0.3)
add("Frontier_AI_Research",          "MLOps",                         "related_to", 0.2)

# ── 7. Security 형제 노드 척력/인력 ──────────────────────
add("Vulnerability_Assessment",      "Incident_Response_and_Compliance","similar_to",0.6)
add("Offensive_Security_and_Vulnerability","Vulnerability_Assessment", "similar_to", 0.7)
add("Cloud_and_Infrastructure_Security","Security_Architecture_and_Compliance","similar_to",0.5)
add("Enterprise_Security_Consulting","Cloud_and_Infrastructure_Security","related_to",0.3)
add("Game_Infrastructure_Security",  "Cloud_and_Infrastructure_Security","similar_to",0.4)

# ════════════════════════════════════════════════════════
# 블랙홀 노드 완화
# ════════════════════════════════════════════════════════
add("Backend_Platform_Engineering",  "Backend_Java",                  "related_to", 0.8)
add("Backend_Platform_Engineering",  "Backend_Python",                "related_to", 0.8)
add("Commerce_Backend_Architecture", "Backend_Java",                  "related_to", 0.8)
add("Enterprise_Web_System_Integration","Backend_Java",               "related_to", 0.8)

add("SRE_Core",                      "Kubernetes",                    "depends_on", 1.5)
add("SRE_Core",                      "CI_CD",                         "depends_on", 1.5)
add("SRE_Core",                      "Monitoring",                    "depends_on", 1.5)
add("Cloud_Infrastructure",          "Kubernetes",                    "depends_on", 1.5)
add("Cloud_Infrastructure",          "CI_CD",                         "related_to", 1.2)

add("M_and_A_Cluster",               "Mergers_and_Acquisitions",      "part_of",    1.8)
add("M_and_A_Cluster",               "Corporate_M_and_A_Strategy",    "part_of",    1.8)
add("M_and_A_Cluster",               "M_and_A_Strategy",              "part_of",    1.8)
add("M_and_A_Cluster",               "Entertainment_M_and_A_Strategy","part_of",    1.5)
add("M_and_A_Cluster",               "Corporate_Strategy",            "part_of",    1.5)

add("Investment_Strategy_Cluster",   "Strategic_Investment",          "part_of",    1.8)
add("Investment_Strategy_Cluster",   "CVC_Strategy",                  "part_of",    1.8)
add("Investment_Strategy_Cluster",   "Venture_Capital_Fundraising",   "part_of",    1.5)
add("Investment_Strategy_Cluster",   "Corporate_Strategy",            "part_of",    1.5)

# ════════════════════════════════════════════════════════
# 파일 패치
# ════════════════════════════════════════════════════════
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # 척력/인력 설정 + 블랙홀 완화 (2026-05-07)',
    '    # similar_to: 매우 유사 형제 (0.5~0.9)',
    '    # related_to: 다른 성격 형제 (0.2~0.4) — 척력에 가까운 중립',
    '    # ══════════════════════════════════════════════',
]
for s, d, r, w in new_edges:
    w_str = str(int(w)) if w == int(w) else str(w)
    edge_lines.append(f'    ("{s}", "{d}", "{r}", {w_str}),')

edge_patch = '\n'.join(edge_lines)
last_edge_matches = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge_matches:
    pos = last_edge_matches[-1].end()
    content = content[:pos] + '\n' + edge_patch + content[pos:]

with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
