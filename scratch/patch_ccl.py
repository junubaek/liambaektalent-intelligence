
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

# ── 신규 노드: Collective_Communication ──
add("Collective_Communication",  "Distributed_Training_Inference",  "depends_on", 2.0)
add("Collective_Communication",  "Model_Parallelism",               "depends_on", 2.0)
add("Collective_Communication",  "LLM_Engineering",                 "used_in",    1.8)

add("Collective_Communication",  "Sys_Software",                    "part_of",    1.8)
add("Collective_Communication",  "Compiler",                        "related_to", 1.5)
add("Collective_Communication",  "NPU_Software_Stack",              "related_to", 1.8)
add("Collective_Communication",  "GPU_Driver",                      "related_to", 1.5)
add("Collective_Communication",  "MLOps",                           "used_in",    1.3)

add("Collective_Communication",  "NPU",                             "used_in",    1.8)
add("Collective_Communication",  "GPGPU",                           "used_in",    1.8)
add("Collective_Communication",  "High_Performance_Computing",      "depends_on", 1.8)
add("Collective_Communication",  "SmartNIC",                        "related_to", 1.5)
add("Collective_Communication",  "DPDK",                            "related_to", 1.3)

# ── 신규 노드: Network_Systems_Programming ──
add("Network_Systems_Programming", "Sys_Software",                  "part_of",    1.8)
add("Network_Systems_Programming", "DPDK",                          "part_of",    2.0)
add("Network_Systems_Programming", "SmartNIC",                      "related_to", 1.8)
add("Network_Systems_Programming", "Collective_Communication",      "related_to", 1.5)
add("Network_Systems_Programming", "High_Performance_Computing",    "related_to", 1.8)
add("Network_Systems_Programming", "Firmware_Engineering",          "related_to", 1.3)

# ── 기존 노드 보강 ──
add("DPDK",     "Collective_Communication",   "related_to", 1.5)
add("DPDK",     "Network_Systems_Programming","part_of",    2.0)
add("DPDK",     "High_Performance_Computing", "related_to", 1.5)
add("DPDK",     "Sys_Software",               "related_to", 1.5)
add("SPDK",     "Network_Systems_Programming","related_to", 1.5)
add("SPDK",     "Sys_Software",               "related_to", 1.5)

# ── NODE_ALIASES ──
NEW_ALIASES = {
    "Collective_Communication": [
        "CCL", "Collective Communication",
        "집합 통신", "분산 통신 라이브러리",
        "NCCL", "RCCL", "AllReduce", "AllGather",
        "분산 학습 통신", "inter-GPU 통신",
        "collective comm", "통신 라이브러리",
        "통신 최적화", "inter-node communication",
        "노드간 통신", "칩간 통신",
    ],
    "Network_Systems_Programming": [
        "네트워크 시스템 프로그래밍",
        "NIC 드라이버", "network driver",
        "고성능 네트워킹", "kernel bypass networking",
        "DPDK 개발", "패킷 처리", "packet processing",
        "네트워크 스택", "데이터 플레인",
        "data plane", "EFA", "InfiniBand",
        "RoCE", "RDMA 프로그래밍",
    ],
    "DPDK": [
        "DPDK", "Data Plane Development Kit",
        "dpdk", "PMD", "Poll Mode Driver",
        "고성능 패킷 처리", "커널 바이패스",
    ],
}

# ════════════════════════════════════════════════════════
# 파일 패치
# ════════════════════════════════════════════════════════
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # Collective Communication + Network Systems (2026-05-07)',
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

alias_lines = [
    '',
    '    # ══ Collective Communication + Network Systems aliases ══',
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
    if na_end != -1:
        content = content[:na_end] + '\n' + '\n'.join(alias_lines) + content[na_end:]
        print('NODE_ALIASES 블록에 CCL 항목 추가 완료')

with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
print(f'   신규 노드: Collective_Communication, Network_Systems_Programming')
