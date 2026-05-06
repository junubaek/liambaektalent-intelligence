
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

# ── 1. Product_Owner ↔ Product_Manager 가중치 강화
add("Product_Owner",  "Service_Planning",          "related_to", 2.0)
add("Product_Owner",  "Project_Manager",            "related_to", 1.5)
add("Product_Owner",  "Platform_Product_Owner",     "similar_to", 1.8)
add("Product_Owner",  "Product_Management",         "similar_to", 1.8)

# ── 2. Project_Manager 연결 보강
add("Project_Manager", "Service_Planning",          "related_to", 1.8)
add("Project_Manager", "Product_Service_Planning",  "related_to", 1.5)
add("Project_Manager", "Product_Owner",             "related_to", 1.5)
add("Project_Manager", "Stakeholder_Management",    "depends_on", 2.0)
add("Project_Manager", "Requirement_Definition",    "depends_on", 1.8)
add("Project_Manager", "Data_Driven_Decision",      "related_to", 1.3)

# ── 3. Service_Planning 연결 보강
add("Service_Planning", "Product_Service_Planning", "similar_to", 1.8)
add("Service_Planning", "User_Research",            "depends_on", 1.8)
add("Service_Planning", "Data_Driven_Decision",     "related_to", 1.5)
add("Service_Planning", "UIUX_Design",              "related_to", 1.3)
add("Service_Planning", "Platform_Service_Planning","similar_to", 1.5)

# ── 4. Product_Core 보강
add("Product_Core", "Product_Service_Planning",     "depends_on", 1.8)
add("Product_Core", "User_Research",                "depends_on", 1.5)
add("Product_Core", "Data_Driven_Decision",         "related_to", 1.5)
add("Product_Core", "Service_Planning",             "depends_on", 1.8)
add("Product_Core", "Product_Owner",                "part_of",    1.5)

# ── 5. Platform_Service_Planning 보강
add("Platform_Service_Planning", "Product_Owner",   "related_to", 1.5)
add("Platform_Service_Planning", "Service_Planning","similar_to", 1.5)

# ── 6. Product_Management 보강
add("Product_Management", "Product_Owner",          "similar_to", 1.8)
add("Product_Management", "Service_Planning",       "related_to", 1.8)
add("Product_Management", "Project_Manager",        "related_to", 1.5)

print(f'추가 엣지 수: {len(new_edges)}')

lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # PO / PM / 서비스기획 연결 보강 (2026-05-07)',
    '    # ══════════════════════════════════════════════',
]
for s, d, r, w in new_edges:
    w_str = str(int(w)) if w == int(w) else str(w)
    lines.append(f'    ("{s}", "{d}", "{r}", {w_str}),')

patch = '\n'.join(lines)

# Find the end of the EDGES list
# Look for the last closing paren of a tuple in the list
last_edge_matches = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge_matches:
    pos = last_edge_matches[-1].end()
    new_content = content[:pos] + '\n' + patch + content[pos:]
    with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'\n✅ 패치 완료: {len(edge_pattern)} → {len(edge_pattern) + len(new_edges)}개 엣지')
else:
    print('❌ EDGES 위치를 찾지 못했습니다.')
