import re
import sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# ── 파일 로드 ────────────────────────────────────────
with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\(\"([^\"]+)\",\s*\"([^\"]+)\",\s*\"([^\"]+)\",\s*([\d.]+)\)', content)
EXISTING = set((s, d) for s, d, r, w in edge_pattern)
print(f'기존 엣지 수: {len(edge_pattern)}')

# ── 형제 노드 그룹 파악 ─────────────────────────────
parent_children = defaultdict(list)
for src, dst, rel, weight in edge_pattern:
    if rel == 'part_of':
        if src not in parent_children[dst]:
            parent_children[dst].append(src)

# ── 새 엣지 생성 ────────────────────────────────────
new_edges = []
added_pairs = set()

def add_edge(src, dst, rel, weight, comment=''):
    key = (src, dst)
    rev = (dst, src)
    if key not in EXISTING and rev not in EXISTING and key not in added_pairs and rev not in added_pairs:
        new_edges.append((src, dst, rel, weight, comment))
        added_pairs.add(key)

# ════════════════════════════════════════════════════
# 1. 형제 노드 similar_to 연결 (같은 부모 공유)
#    가중치: 형제 관계 0.8
# ════════════════════════════════════════════════════
SIBLING_WEIGHT = {
    # 기술 스택 형제는 좀더 강하게
    'Backend': 0.9,
    'Frontend': 0.85,
    'System_Software': 0.85,
    'Semiconductor_Engineering': 0.85,
    # 직무 형제는 보통
    'Corporate_Finance': 0.8,
    'Corporate_Strategy': 0.75,
    'Finance_Leadership': 0.85,
    'Executive_Leadership': 0.75,
    'Information_Security': 0.8,
    'Cyber_Security': 0.8,
    'Data_Engineering': 0.8,
    'Data_Analysis': 0.8,
    'Marketing_Strategy': 0.75,
    'Digital_Marketing': 0.75,
    'Corporate_Operations': 0.75,
    'B2B_Sales': 0.8,
    'SCM': 0.8,
    'FinTech': 0.85,
    'HW_Hardware': 0.85,
}

sibling_count = 0
for parent, children in parent_children.items():
    weight = SIBLING_WEIGHT.get(parent, 0.75)
    # 형제 수가 너무 많으면 핵심만 (최대 8개)
    group = children[:8]
    for i in range(len(group)):
        for j in range(i+1, len(group)):
            add_edge(group[i], group[j], 'similar_to', weight, f'sibling:{parent}')
            sibling_count += 1

print(f'형제 연결 후보: {sibling_count}개')

# ════════════════════════════════════════════════════
# 2. 기술 스택 크로스 연결
# ════════════════════════════════════════════════════

# DevOps / 인프라 클러스터
tech_cross = [
    # DevOps 체인
    ('Docker',          'CI_CD',                'related_to', 1.5),
    ('CI_CD',           'Kubernetes',           'depends_on', 1.5),
    ('Docker',          'Kubernetes',           'related_to', 1.5),
    ('Monitoring',      'CI_CD',                'related_to', 1.2),
    ('Monitoring',      'Kubernetes',           'related_to', 1.2),
    ('CI_CD',           'Infra_Engineer',       'related_to', 1.0),

    # ML/AI 체인
    ('ML_Pipeline',     'Model_Serving',        'depends_on', 1.5),
    ('ML_Pipeline',     'Data_Engineering',     'depends_on', 1.5),
    ('Model_Serving',   'MLOps',                'part_of',    1.5),
    ('ML_Pipeline',     'MLOps',                'part_of',    1.5),
    ('LLM_Architecture','Model_Serving',        'related_to', 1.5),
    ('LLM_Models',      'LLM_Architecture',     'related_to', 1.5),
    ('Recommendation_System', 'ML_Pipeline',    'depends_on', 1.2),
    ('Recommendation_System', 'Data_Engineering','related_to',1.2),
    ('Hardware_Acceleration', 'MLOps',          'related_to', 1.2),
    ('Hardware_Acceleration', 'AI_Accelerator', 'related_to', 1.5),

    # 분산 시스템 체인
    ('Distributed_Storage', 'Distributed_Training_Inference', 'related_to', 1.2),
    ('DPDK',            'Kernel_Bypass',        'related_to', 1.5),
    ('SPDK',            'Kernel_Bypass',        'related_to', 1.5),
    ('DPDK',            'SPDK',                 'similar_to', 1.2),
    ('SDS',             'Distributed_Storage',  'related_to', 1.5),

    # 백엔드 기술 스택
    ('Backend_Java',    'Database_Engine',      'related_to', 1.0),
    ('Backend_Python',  'Database_Engine',      'related_to', 1.0),
    ('Backend_Node',    'Database_Engine',      'related_to', 1.0),
    ('Backend_Java',    'Docker',               'related_to', 1.0),
    ('Backend_Python',  'Docker',               'related_to', 1.0),
    ('Backend_Java',    'CI_CD',                'related_to', 1.0),
    ('Backend_Go',      'Docker',               'related_to', 1.2),
    ('Backend_Go',      'Kubernetes',           'related_to', 1.2),
    ('Fullstack',       'Docker',               'related_to', 0.9),
    ('Fullstack',       'Frontend_React',       'related_to', 1.2),
    ('Fullstack',       'Backend_Node',         'related_to', 1.2),

    # 모바일
    ('Mobile_iOS',      'Mobile_CrossPlatform', 'related_to', 1.0),
    ('Frontend_React',  'Mobile_CrossPlatform', 'related_to', 0.9),

    # 반도체/HW 체인
    ('AI_Accelerator',  'NPU',                  'related_to', 1.5),
    ('Hardware_Acceleration', 'NPU',            'related_to', 1.5),
    ('Hardware_Offloading',   'Network_Hardware','related_to', 1.2),
    ('Test_Architecture', 'Hardware_Design',    'related_to', 1.2),

    # 네트워크 하드웨어
    ('Network_Hardware', 'Kernel_Bypass',       'related_to', 1.2),
    ('Network_Hardware', 'DPDK',                'related_to', 1.2),

    # 데이터베이스
    ('Database_Engine', 'Data_Structures',      'depends_on', 1.5),
    ('Database_Engine', 'Data_Pipeline_Construction', 'related_to', 1.0),
]

for edge in tech_cross:
    add_edge(*edge, 'tech_cross')

# ════════════════════════════════════════════════════
# 3. 직무-역량 크로스 연결
# ════════════════════════════════════════════════════
role_cross = [
    # Finance / CFO
    ('CFO_Role',                'Treasury_Management',          'depends_on', 2.0),
    ('CFO_Role',                'IR_Management',                'depends_on', 1.8),
    ('CFO_Role',                'Mergers_and_Acquisitions',     'related_to', 1.8),
    ('CFO_Role',                'IPO_Preparation_and_Execution','related_to', 2.0),
    ('CFO_Role',                'Consolidated_Financial_Statements','depends_on',1.8),
    ('CFO_Role',                'Internal_Control',             'depends_on', 1.5),
    ('Chief_Financial_Officer', 'CFO_Role',                     'similar_to', 2.0),
    ('Corporate_Governance',    'Chief_Financial_Officer',      'related_to', 1.5),
    ('Valuation',               'Mergers_and_Acquisitions',     'depends_on', 1.8),
    ('Valuation',               'IPO_Preparation_and_Execution','depends_on', 1.8),
    ('Venture_Capital_Fundraising','IR_Management',             'related_to', 1.5),
    ('IPO_PR',                  'IPO_Preparation_and_Execution','depends_on', 2.0),
    ('IPO_PR',                  'IR_Management',                'related_to', 1.5),

    # Strategy / BD
    ('Strategic_Investment',    'CVC_Strategy',                 'related_to', 1.5),
    ('Strategic_Investment',    'Venture_Capital_Fundraising',  'related_to', 1.5),
    ('New_Business_Development','Joint_Venture_Establishment',  'related_to', 1.5),
    ('New_Business_Development','Strategic_Partnership',        'depends_on', 1.5),
    ('Digital_Transformation_Strategy','New_Business_Development','related_to',1.2),
    ('New_Biz_Incubation',      'New_Business_Development',     'similar_to', 1.5),
    ('Global_Business_Development','Strategic_Partnership',     'depends_on', 1.5),
    ('Global_Business_Development','Global_Sales_and_Marketing','related_to', 1.5),

    # Product Owner / PM
    ('Product_Core',            'Product_Service_Planning',     'depends_on', 1.8),
    ('Product_Core',            'Data_Driven_Decision',         'related_to', 1.5),
    ('Product_Core',            'User_Research',                'depends_on', 1.5),
    ('Product_Core',            'Product_Manager',              'part_of',    1.5),
    ('ML_Pipeline',             'Product_Manager',              'related_to', 0.8),

    # Marketing
    ('Growth_Marketing',        'Conversion_Rate_Optimization', 'depends_on', 1.5),
    ('Growth_Marketing',        'Performance_Marketing',        'related_to', 1.5),
    ('Growth_Hacking_and_Marketing','Growth_Marketing',         'similar_to', 1.5),
    ('Content_Marketing_Strategy','Content_Marketing',         'similar_to', 1.2),
    ('CRM_Marketing',           'CRM_Strategy',                 'similar_to', 1.5),
    ('Digital_Campaign_Planning','Digital_Campaign_Management', 'similar_to', 1.5),
    ('Data_Driven_Marketing',   'Performance_Marketing',        'depends_on', 1.5),
    ('IMC',                     'Brand_Management',             'related_to', 1.2),

    # HR / 조직
    ('HR_and_Admin_Management', 'Human_Resources_Management',   'similar_to', 1.5),
    ('HR_Strategy_and_Operations','Human_Resources_Management', 'similar_to', 1.5),
    ('ATS',                     'Human_Resources_Management',   'used_in',    1.5),
    ('ATS',                     'Talent_Acquisition',           'used_in',    1.5),

    # 보안
    ('Vulnerability_Assessment','Incident_Response_and_Compliance','related_to',1.5),
    ('Offensive_Security_and_Vulnerability','Vulnerability_Assessment','similar_to',1.5),
    ('Cloud_and_Infrastructure_Security','Kubernetes',          'related_to', 1.2),
    ('Cloud_and_Infrastructure_Security','Enterprise_Security_Consulting','related_to',1.2),
    ('Security_Architecture_and_Compliance','Information_Security','depends_on',1.5),
    ('Data_Privacy_Protection', 'Data_Privacy_and_Compliance',  'similar_to', 1.5),

    # SCM / 물류
    ('Logistics_and_Supply_Chain','Logistics_and_Inventory_Optimization','similar_to',1.5),
    ('Procurement_and_Sourcing', 'Supply_Chain_Management',     'depends_on', 1.5),

    # FinTech
    ('Core_Banking',            'Channel_System',               'related_to', 1.5),
    ('Mobile_Payment_Service',  'Channel_System',               'related_to', 1.5),
    ('Mobile_Payment_Service',  'FinTech',                      'part_of',    1.5),

    # 데이터
    ('A_B_Testing',             'Data_Driven_Decision',         'depends_on', 1.5),
    ('A_B_Testing',             'Causal_Inference',             'related_to', 1.5),
    ('Demand_Forecasting',      'Data_Pipeline_Construction',   'depends_on', 1.2),
    ('Real_Time_Data_Processing','Data_Pipeline_Construction',  'similar_to', 1.5),
    ('Data_Warehouse_Architecture','Data_Pipeline_Construction','depends_on', 1.5),
    ('Big_Data_Processing',     'Data_Warehouse_Architecture',  'related_to', 1.5),
    ('Machine_Learning_for_Business','Data_Driven_Decision',    'depends_on', 1.5),
    ('E_Commerce_Data_Analysis','A_B_Testing',                  'related_to', 1.2),

    # Mobility
    ('MaaS',                    'Smart_City_and_MaaS_Architecture','part_of', 1.5),
    ('Autonomous_Mobility_Service','MaaS',                      'related_to', 1.5),

    # Quality
    ('Food_Safety_and_Quality_Control','Laboratory_Compliance_and_Validation','related_to',1.2),
    ('Validation_and_Qualification','Laboratory_Compliance_and_Validation','similar_to',1.2),
    ('Equipment_Inspection_and_Diagnosis','Validation_and_Qualification','related_to',1.2),
]

for edge in role_cross:
    add_edge(*edge, 'role_cross')

# ════════════════════════════════════════════════════
# 4. 중복 노드 통합 (similar_to)
# ════════════════════════════════════════════════════
duplicates = [
    ('Internal_Accounting_Control', 'Internal_Control',         'similar_to', 1.5),
    ('Infra_Engineer',              'System_Engineer',           'similar_to', 1.0),
    ('자금_Treasury',               'Treasury_Management',       'similar_to', 2.0),
    ('시스템소프트웨어',             'Sys_Software',              'similar_to', 1.5),
    ('Performance_Marketing',       'Digital_Campaign_Management','related_to',1.0),
]
for edge in duplicates:
    add_edge(*edge, 'dedup')

# ════════════════════════════════════════════════════
# 결과 출력 및 파일 생성
# ════════════════════════════════════════════════════
print(f'\n총 추가 엣지 수: {len(new_edges)}')
print()

# 카테고리별 집계
from collections import Counter
cat_count = Counter(e[4] for e in new_edges)
for cat, cnt in cat_count.items():
    print(f'  {cat}: {cnt}개')

# 추가할 엣지 코드 생성
lines = []
lines.append('\n    # ══════════════════════════════════════════════')
lines.append('    # EDGE ENRICHMENT — 자동 보강 (2026-05-07)')
lines.append('    # ══════════════════════════════════════════════')

current_cat = None
for src, dst, rel, weight, cat in new_edges:
    if cat != current_cat:
        cat_labels = {
            'sibling:Backend': '## 형제: Backend',
            'tech_cross': '## 기술 스택 크로스 연결',
            'role_cross': '## 직무-역량 크로스 연결',
            'dedup': '## 중복 노드 통합',
        }
        # 형제 그룹 구분
        label = cat_labels.get(cat, f'## {cat}')
        if cat.startswith('sibling:'):
            parent = cat.split(':')[1]
            label = f'## 형제: {parent}'
        lines.append(f'    # {label}')
        current_cat = cat
    w_str = str(int(weight)) if weight == int(weight) else str(weight)
    lines.append(f'    ("{src}", "{dst}", "{rel}", {w_str}),')

patch_code = '\n'.join(lines)

# ontology_graph.py에서 EDGES 리스트 끝 찾아서 삽입
# 마지막 엣지 튜플 뒤에 추가
insert_marker = '# ══════════════════════════════════════════════'

# EDGES 변수 선언 찾기
# 마지막 엣지 라인 찾아서 그 뒤에 삽입
last_edge_match = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge_match:
    last_pos = last_edge_match[-1].end()
    new_content = content[:last_pos] + '\n' + patch_code + content[last_pos:]

    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'\n✅ ontology_graph.py 패치 완료')
    print(f'   기존 엣지: {len(edge_pattern)}개')
    print(f'   추가 엣지: {len(new_edges)}개')
    print(f'   총 엣지: {len(edge_pattern) + len(new_edges)}개')
else:
    print('❌ EDGES 위치를 찾지 못했습니다.')

# 검증용 패치 내용 저장
with open('edge_patch_preview.txt', 'w', encoding='utf-8') as f:
    f.write(f'추가 엣지 총 {len(new_edges)}개\n\n')
    for src, dst, rel, weight, cat in new_edges:
        f.write(f'{cat:20s} | {src:45s} → {dst} ({rel}, {weight})\n')
print(f'\n📄 edge_patch_preview.txt 저장 완료 (검토용)')
