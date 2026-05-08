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

# ── Healthcare_Core 허브 ─────────────────────────────────
add("Healthcare_Core",       "Pharma_Core",                 "part_of",    2.0)
add("Healthcare_Core",       "Medical_Device_Core",         "part_of",    2.0)
add("Healthcare_Core",       "Digital_Health_Core",         "part_of",    2.0)
add("Healthcare_Core",       "Clinical_Research",           "part_of",    2.0)
add("Healthcare_Core",       "Medical_Device",              "part_of",    1.8)
add("Healthcare_Core",       "Regulatory_Affairs",          "part_of",    1.8)
add("Healthcare_Core",       "Healthcare_PM",               "part_of",    1.5)

# ── Pharma_Core (제약/신약) ──────────────────────────────
add("Pharma_Core",           "Clinical_Research",           "part_of",    2.0)
add("Pharma_Core",           "Drug_Development",            "part_of",    2.0)
add("Pharma_Core",           "Regulatory_Affairs",          "part_of",    2.0)
add("Pharma_Core",           "GMP_Quality",                 "part_of",    2.0)
add("Pharma_Core",           "Drug_Master_File_Registration","part_of",   1.8)
add("Pharma_Core",           "Global_GMP_Certification",    "part_of",    1.8)
add("Pharma_Core",           "Laboratory_Compliance_and_Validation","part_of",1.5)
add("Pharma_Core",           "Healthcare_Core",             "part_of",    1.5)

# ── Drug_Development (신규 노드) ────────────────────────
add("Drug_Development",      "Clinical_Research",           "depends_on", 2.0)
add("Drug_Development",      "Regulatory_Affairs",          "depends_on", 2.0)
add("Drug_Development",      "GMP_Quality",                 "depends_on", 1.8)
add("Drug_Development",      "Pharma_Core",                 "part_of",    1.8)
add("Drug_Development",      "Drug_Master_File_Registration","depends_on",1.8)

# ── Clinical_Research 고립 해제 ──────────────────────────
add("Clinical_Research",     "Drug_Development",            "depends_on", 2.0)
add("Clinical_Research",     "Regulatory_Affairs",          "depends_on", 1.8)
add("Clinical_Research",     "GMP_Quality",                 "related_to", 1.3)
add("Clinical_Research",     "Medical_Image_Computing",     "related_to", 1.2)
add("Clinical_Research",     "Pharma_Core",                 "part_of",    1.8)
add("Clinical_Research",     "Deep_Learning_for_Healthcare","related_to", 1.3)
add("Clinical_Research",     "Laboratory_Compliance_and_Validation","related_to",1.3)

# ── GMP_Quality (신규 노드) ─────────────────────────────
add("GMP_Quality",           "Global_GMP_Certification",    "depends_on", 2.0)
add("GMP_Quality",           "Laboratory_Compliance_and_Validation","depends_on",1.8)
add("GMP_Quality",           "Drug_Master_File_Registration","depends_on",1.5)
add("GMP_Quality",           "Pharma_Core",                 "part_of",    1.8)
add("GMP_Quality",           "Regulatory_Affairs",          "related_to", 1.5)

# ── Regulatory_Affairs 보강 ─────────────────────────────
add("Regulatory_Affairs",    "Drug_Master_File_Registration","depends_on",2.0)
add("Regulatory_Affairs",    "Global_GMP_Certification",    "related_to", 1.5)
add("Regulatory_Affairs",    "Clinical_Research",           "depends_on", 1.8)
add("Regulatory_Affairs",    "Medical_Device_RA",           "similar_to", 0.7)
add("Regulatory_Affairs",    "Healthcare_Core",             "part_of",    1.5)

# ── Medical_Device_Core (의료기기) ──────────────────────
add("Medical_Device_Core",   "Medical_Device",              "part_of",    2.0)
add("Medical_Device_Core",   "Medical_Device_RA",           "part_of",    2.0)
add("Medical_Device_Core",   "Clinical_Evidence",           "part_of",    1.8)
add("Medical_Device_Core",   "Medical_Image_Computing",     "related_to", 1.5)
add("Medical_Device_Core",   "Healthcare_Core",             "part_of",    1.5)

# ── Medical_Device 고립 해제 ────────────────────────────
add("Medical_Device",        "Medical_Device_RA",           "depends_on", 2.0)
add("Medical_Device",        "Clinical_Evidence",           "depends_on", 1.8)
add("Medical_Device",        "Regulatory_Affairs",          "depends_on", 1.8)
add("Medical_Device",        "GMP_Quality",                 "related_to", 1.3)
add("Medical_Device",        "Medical_Device_Core",         "part_of",    1.8)
add("Medical_Device",        "Medical_Image_Computing",     "related_to", 1.2)

# ── Medical_Device_RA (신규 노드) ──────────────────────
add("Medical_Device_RA",     "Regulatory_Affairs",          "similar_to", 0.7)
add("Medical_Device_RA",     "Medical_Device",              "depends_on", 2.0)
add("Medical_Device_RA",     "Medical_Device_Core",         "part_of",    1.8)
add("Medical_Device_RA",     "Clinical_Evidence",           "related_to", 1.5)

# ── Clinical_Evidence (신규 노드) ───────────────────────
add("Clinical_Evidence",     "Clinical_Research",           "similar_to", 0.7)
add("Clinical_Evidence",     "Medical_Device",              "depends_on", 1.8)
add("Clinical_Evidence",     "Medical_Device_Core",         "part_of",    1.5)

# ── Digital_Health_Core (헬스케어 IT/AI) ────────────────
add("Digital_Health_Core",   "Medical_Image_Computing",     "part_of",    2.0)
add("Digital_Health_Core",   "Deep_Learning_for_Healthcare","part_of",    2.0)
add("Digital_Health_Core",   "Healthcare_PM",               "part_of",    1.8)
add("Digital_Health_Core",   "Digital_Health_Platform",     "part_of",    2.0)
add("Digital_Health_Core",   "Clinical_Decision_Support_System","part_of",1.8)
add("Digital_Health_Core",   "Healthcare_Core",             "part_of",    1.5)

# ── Digital_Health_Platform (신규 노드) ─────────────────
add("Digital_Health_Platform","Healthcare_PM",              "related_to", 1.5)
add("Digital_Health_Platform","Medical_Image_Computing",    "related_to", 1.3)
add("Digital_Health_Platform","Deep_Learning_for_Healthcare","related_to",1.5)
add("Digital_Health_Platform","EMR_EHR",                   "depends_on", 1.8)
add("Digital_Health_Platform","Digital_Health_Core",       "part_of",    1.8)

# ── EMR_EHR (신규 노드) ─────────────────────────────────
add("EMR_EHR",               "Digital_Health_Platform",     "part_of",    1.8)
add("EMR_EHR",               "Healthcare_PM",               "related_to", 1.5)
add("EMR_EHR",               "Digital_Health_Core",         "part_of",    1.5)
add("EMR_EHR",               "Clinical_Decision_Support_System","related_to",1.5)

# ── Medical_Image_Computing 보강 ────────────────────────
add("Medical_Image_Computing","Deep_Learning_for_Healthcare","depends_on",1.8)
add("Medical_Image_Computing","Clinical_Decision_Support_System","related_to",1.5)
add("Medical_Image_Computing","Digital_Health_Core",        "part_of",    1.8)

# ── Deep_Learning_for_Healthcare 보강 ───────────────────
add("Deep_Learning_for_Healthcare","Medical_Image_Computing","depends_on",1.8)
add("Deep_Learning_for_Healthcare","Clinical_Decision_Support_System","depends_on",1.8)
add("Deep_Learning_for_Healthcare","Digital_Health_Core",   "part_of",    1.8)
add("Deep_Learning_for_Healthcare","LLM_Engineering",       "related_to", 1.3)
add("Deep_Learning_for_Healthcare","Deep_Learning",         "depends_on", 1.8)

# ── Clinical_Decision_Support_System 보강 ───────────────
add("Clinical_Decision_Support_System","Digital_Health_Core","part_of",  1.8)
add("Clinical_Decision_Support_System","Medical_Image_Computing","related_to",1.5)

# ── Healthcare_PM 고립 해제 ─────────────────────────────
add("Healthcare_PM",         "Digital_Health_Core",         "part_of",    1.8)
add("Healthcare_PM",         "Product_Manager",             "similar_to", 0.6)
add("Healthcare_PM",         "Medical_Device",              "related_to", 1.3)
add("Healthcare_PM",         "Digital_Health_Platform",     "related_to", 1.5)
add("Healthcare_PM",         "Clinical_Research",           "related_to", 1.2)

# ── 제약/의료기기 ↔ AI 연결 (크로스 도메인) ──────────────
add("Drug_Development",      "LLM_Engineering",             "related_to", 1.0)
add("Clinical_Research",     "AI_Research",                 "related_to", 1.0)
add("Medical_Image_Computing","Computer_Vision",            "depends_on", 1.8)
add("Medical_Image_Computing","Multimodal",                 "related_to", 1.3)

NEW_ALIASES = {
    "Healthcare_Core": [
        "헬스케어", "의료", "의료/제약", "바이오",
        "헬스케어 산업", "의료 산업", "생명과학",
        "life science", "healthcare", "biopharma",
    ],
    "Pharma_Core": [
        "제약", "신약개발", "제약 산업", "바이오제약",
        "pharma", "pharmaceutical", "제약회사",
        "신약", "의약품 개발",
    ],
    "Drug_Development": [
        "신약 개발", "drug development", "의약품 개발",
        "후보물질 발굴", "전임상", "preclinical",
        "신약 연구", "약물 개발", "CMC",
        "제형 개발", "제제 연구",
    ],
    "Clinical_Research": [
        "임상연구", "임상시험", "CRA", "CRC", "CRO",
        "임상 CRA", "임상 코디네이터", "CRO 담당자",
        "clinical trial", "임상 1상", "임상 2상", "임상 3상",
        "IRB", "GCP", "임상개발", "clinical research",
        "임상운영", "모니터링 CRA",
    ],
    "GMP_Quality": [
        "GMP", "품질관리", "QA", "QC",
        "cGMP", "GMP 관리", "의약품 품질",
        "제약 QA", "제약 품질", "품질 보증",
        "validation", "밸리데이션", "제조 품질",
    ],
    "Global_GMP_Certification": [
        "KCGMP", "EU GMP", "FDA GMP",
        "FDA 실사", "GMP 인증", "GMP 심사",
        "FDA 공장 심사", "글로벌 GMP",
    ],
    "Regulatory_Affairs": [
        "인허가", "RA", "규제 대응", "허가",
        "식약처", "MFDS", "FDA", "EMA",
        "의약품 허가", "품목허가", "허가 전략",
        "regulatory affairs", "regulatory", "규제과학",
    ],
    "Medical_Device": [
        "의료기기", "medical device", "의료 장비",
        "체외진단", "IVD", "의료기기 개발",
        "진단기기", "치료기기", "영상의료기기",
        "수술 로봇", "웨어러블 의료기기",
    ],
    "Medical_Device_RA": [
        "의료기기 인허가", "의료기기 허가",
        "의료기기 RA", "KFDA 의료기기",
        "510k", "CE 마킹", "의료기기 등록",
        "medical device regulatory",
    ],
    "Clinical_Evidence": [
        "임상적 증거", "clinical evidence",
        "임상 데이터", "임상 결과", "효능 입증",
        "RWE", "Real World Evidence", "임상 근거",
    ],
    "Digital_Health_Platform": [
        "디지털 헬스", "digital health",
        "헬스케어 플랫폼", "의료 플랫폼",
        "원격의료", "telemedicine", "비대면 진료",
        "건강관리 앱", "헬스앱", "모바일 헬스",
        "mHealth", "DTx", "디지털 치료제",
    ],
    "EMR_EHR": [
        "EMR", "EHR", "전자의무기록",
        "전자건강기록", "의료정보시스템",
        "HIS", "병원정보시스템", "OCS",
        "PACS", "의료 IT 시스템",
    ],
    "Healthcare_PM": [
        "헬스케어 PM", "의료 서비스 기획",
        "헬스케어 기획", "의료 플랫폼 PM",
        "디지털 헬스 PM", "헬스케어 프로덕트",
        "healthcare product manager",
    ],
    "Medical_Image_Computing": [
        "의료영상", "의료 영상 AI", "CT 분석",
        "MRI 분석", "의료 이미징", "방사선",
        "DICOM", "의료영상 처리", "영상 진단 AI",
        "medical imaging", "medical image analysis",
    ],
    "Deep_Learning_for_Healthcare": [
        "헬스케어 AI", "의료 AI", "AI 진단",
        "AI 신약", "의료 딥러닝", "바이오 AI",
        "healthcare deep learning", "AI 의료",
        "질병 예측 AI", "임상 AI",
    ],
    "Drug_Master_File_Registration": [
        "DMF", "DMF 등록", "JDMF", "KDMF",
        "원료의약품 등록", "Drug Master File",
        "원료 허가", "API DMF",
    ],
    "Clinical_Decision_Support_System": [
        "CDSS", "임상 의사결정 지원",
        "clinical decision support",
        "진단 보조 AI", "의료 보조 시스템",
    ],
}

# Injected edges
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # 헬스케어/제약/의료기기/헬스IT 온톨로지 보강 (2026-05-07)',
    '    # Healthcare_Core 허브 신설 + 전 영역 연결',
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
    '    # ══ 헬스케어/제약/의료기기 aliases (2026-05-07) ══',
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
