import re
import sys
import os

# Set encoding for output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

target_file = 'ontology_graph.py'

if not os.path.exists(target_file):
    print(f"Error: {target_file} not found.")
    sys.exit(1)

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\(\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*([\d.]+)\)', content)
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

# ── Legal_Core 허브 → 하위 노드 연결 ─────────────────────
add("Legal_Core",            "Legal_Practice",              "part_of",    2.0)
add("Legal_Core",            "Legal_Compliance",            "part_of",    2.0)
add("Legal_Core",            "Corporate_Legal_Counsel",     "part_of",    2.0)
add("Legal_Core",            "Patent_Management",           "part_of",    1.8)
add("Legal_Core",            "Regulatory_Affairs",          "part_of",    1.5)
add("Legal_Core",            "Compliance_Management",       "part_of",    1.8)
add("Legal_Core",            "Labor_Law_Compliance",        "part_of",    1.5)
add("Legal_Core",            "Financial_Compliance",        "related_to", 1.3)

# ── Legal_Practice 보강 (핵심 — 변호사 검색 직격) ─────────
add("Legal_Practice",        "Legal_Compliance",            "similar_to", 0.7)
add("Legal_Practice",        "Corporate_Legal_Counsel",     "similar_to", 0.8)
add("Legal_Practice",        "Contract_Review",             "depends_on", 2.0)
add("Legal_Practice",        "Litigation",                  "depends_on", 2.0)
add("Legal_Practice",        "Patent_Management",           "related_to", 0.5)
add("Legal_Practice",        "Labor_Law_Compliance",        "related_to", 0.4)
add("Legal_Practice",        "Regulatory_Affairs",          "related_to", 0.4)
add("Legal_Practice",        "Financial_Compliance",        "related_to", 0.3)

# ── Legal_Compliance 고립 해제 ──────────────────────────
add("Legal_Compliance",      "Compliance_Management",       "similar_to", 0.8)
add("Legal_Compliance",      "Corporate_Legal_Counsel",     "similar_to", 0.6)
add("Legal_Compliance",      "Financial_Compliance",        "related_to", 0.5)
add("Legal_Compliance",      "Labor_Law_Compliance",        "related_to", 0.5)
add("Legal_Compliance",      "Data_Privacy_and_Compliance", "related_to", 0.4)
add("Legal_Compliance",      "Regulatory_Affairs",          "related_to", 0.5)

# ── Corporate_Legal_Counsel 보강 ────────────────────────
add("Corporate_Legal_Counsel","Legal_Practice",             "similar_to", 0.8)
add("Corporate_Legal_Counsel","Contract_Review",            "depends_on", 2.0)
add("Corporate_Legal_Counsel","Compliance_Management",      "depends_on", 1.5)
add("Corporate_Legal_Counsel","Mergers_and_Acquisitions",   "related_to", 0.5)
add("Corporate_Legal_Counsel","IPO_Preparation_and_Execution","related_to",0.4)

# ── 신규 노드: Litigation, Contract_Review ──────────────
add("Litigation",            "Legal_Practice",              "part_of",    2.0)
add("Litigation",            "Legal_Core",                  "part_of",    1.8)
add("Contract_Review",       "Legal_Practice",              "part_of",    2.0)
add("Contract_Review",       "Corporate_Legal_Counsel",     "part_of",    1.8)
add("Contract_Review",       "Legal_Core",                  "part_of",    1.5)
add("Contract_Review",       "Mergers_and_Acquisitions",    "used_in",    1.3)

# ── Patent_Management 보강 ──────────────────────────────
add("Patent_Management",     "Legal_Practice",              "related_to", 0.5)
add("Patent_Management",     "Legal_Core",                  "part_of",    1.8)
add("Patent_Management",     "Regulatory_Affairs",          "related_to", 0.4)

# ── Regulatory_Affairs 보강 ─────────────────────────────
add("Regulatory_Affairs",    "Legal_Core",                  "part_of",    1.5)
add("Regulatory_Affairs",    "Legal_Compliance",            "related_to", 0.5)
add("Regulatory_Affairs",    "Financial_Compliance",        "related_to", 0.4)

NEW_ALIASES = {
    "Legal_Core": [
        "법무", "법률", "법무팀", "법무부서",
        "legal", "법조", "법률 전문가",
    ],
    "Legal_Practice": [
        "변호사", "법무법인", "사내변호사",
        "계약 검토", "소송", "법률 자문",
        "attorney", "lawyer", "counsel",
        "변호사 자격", "법학", "사법시험",
        "변호사 출신", "로펌",
    ],
    "Legal_Compliance": [
        "법무", "준법", "컴플라이언스",
        "Compliance", "규제대응", "법적 리스크",
        "법무 컴플라이언스", "준법감시",
        "규정 준수", "법규 준수",
    ],
    "Corporate_Legal_Counsel": [
        "사내 법무", "사내 변호사", "법무팀장",
        "기업 법무", "법률 검토",
        "투자 계약 자문", "사내 법무 및 규제 대응",
        "Corporate Legal", "In-house Counsel",
        "GC", "General Counsel",
    ],
    "Litigation": [
        "소송", "소송 업무", "민사소송", "형사소송",
        "분쟁 해결", "중재", "litigation",
        "소송 대리", "법정 업무",
    ],
    "Contract_Review": [
        "계약 검토", "계약서 검토", "계약 관리",
        "계약 협상", "NDA 검토", "MOU 검토",
        "contract review", "계약법",
    ],
}

# Injected edges
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # 법무/변호사 온톨로지 보강 (2026-05-07)',
    '    # Legal_Core 허브 신설 + Legal_Practice 연결 강화',
    '    # ══════════════════════════════════════════════',
]
for s, d, r, w in new_edges:
    w_str = str(int(w)) if w == int(w) else str(w)
    edge_lines.append(f'    ("{s}", "{d}", "{r}", {w_str}),')

edge_patch = '\n'.join(edge_lines)
last_edge = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge:
    pos = last_edge[-1].end()
    content = content[:pos] + '\n' + edge_patch + content[pos:]

# Injected aliases
alias_lines = [
    '',
    '    # ══ 법무/변호사 aliases (2026-05-07) ══',
]
for node, aliases in NEW_ALIASES.items():
    alias_lines.append(f'    "{node}": [')
    for i, alias in enumerate(aliases):
        comma = ',' if i < len(aliases) - 1 else ''
        escaped = alias.replace('"', '\\"')
        alias_lines.append(f'        "{escaped}"{comma}')
    alias_lines.append('    ],')

if 'NODE_ALIASES' in content:
    na_start = content.find('NODE_ALIASES')
    na_end = content.find('\n}', na_start)
    content = content[:na_end] + '\n' + '\n'.join(alias_lines) + content[na_end:]
else:
    map_end = content.find('\n}', content.find('CANONICAL_MAP')) + 2
    content = content[:map_end] + '\n' + '\n'.join(alias_lines) + content[map_end:]

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
print(f'   신규 노드: Legal_Core, Litigation, Contract_Review')
