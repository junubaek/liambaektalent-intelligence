
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

# ════════════════════════════════════════════════════════
# 1. AI_Research / Frontier 계열 — LLM_Engineering과 연결
# ════════════════════════════════════════════════════════
add("AI_Research",              "LLM_Engineering",              "related_to", 1.8)
add("AI_Research",              "NLP_and_LLM_Optimization",     "related_to", 1.8)
add("AI_Research",              "Deep_Learning",                "depends_on", 2.0)
add("AI_Research",              "Computer_Vision",              "related_to", 1.5)
add("AI_Research",              "Multimodal",                   "related_to", 1.5)
add("Frontier_AI_Research",     "LLM_Engineering",              "related_to", 1.8)
add("Frontier_AI_Research",     "AI_Research",                  "similar_to", 1.8)
add("Frontier_AI_Research",     "NLP_and_LLM_Optimization",     "depends_on", 1.8)
add("Frontier_AI_Research",     "Multimodal",                   "related_to", 1.5)

# ════════════════════════════════════════════════════════
# 2. 신규 노드: Multimodal
# ════════════════════════════════════════════════════════
add("Multimodal",               "LLM_Engineering",              "depends_on", 2.0)
add("Multimodal",               "Computer_Vision",              "depends_on", 2.0)
add("Multimodal",               "Natural_Language_Processing",  "depends_on", 2.0)
add("Multimodal",               "Deep_Learning",                "depends_on", 2.0)
add("Multimodal",               "Generative_AI_and_3D_Vision",  "related_to", 1.5)
add("Multimodal",               "Speech_Recognition",           "related_to", 1.3)
add("Multimodal",               "AI_Research",                  "part_of",    1.5)

# ════════════════════════════════════════════════════════
# 3. 신규 노드: Speech_Recognition
# ════════════════════════════════════════════════════════
add("Speech_Recognition",       "Natural_Language_Processing",  "depends_on", 1.8)
add("Speech_Recognition",       "Deep_Learning",                "depends_on", 2.0)
add("Speech_Recognition",       "LLM_Engineering",              "related_to", 1.5)
add("Speech_Recognition",       "Multimodal",                   "related_to", 1.3)
add("Speech_Recognition",       "AI_Research",                  "part_of",    1.5)
add("Speech_Recognition",       "NLP_and_LLM_Optimization",     "related_to", 1.5)
add("Speech_Recognition",       "OnDevice_AI",                  "related_to", 1.3)

# ════════════════════════════════════════════════════════
# 4. 신규 노드: Search_Ranking
# ════════════════════════════════════════════════════════
add("Search_Ranking",           "Natural_Language_Processing",  "depends_on", 2.0)
add("Search_Ranking",           "Recommendation_System",        "related_to", 1.8)
add("Search_Ranking",           "Machine_Learning",             "depends_on", 1.8)
add("Search_Ranking",           "LLM_Engineering",              "related_to", 1.5)
add("Search_Ranking",           "Data_Analysis",                "depends_on", 1.5)
add("Search_Ranking",           "Search_Engine",                "part_of",    1.8)
add("Search_Ranking",           "Personalization",              "related_to", 1.5)
add("Search_Ranking",           "A_B_Testing",                  "depends_on", 1.5)

# ════════════════════════════════════════════════════════
# 5. 신규 노드: Personalization
# ════════════════════════════════════════════════════════
add("Personalization",          "Recommendation_System",        "similar_to", 1.8)
add("Personalization",          "Machine_Learning",             "depends_on", 1.8)
add("Personalization",          "Search_Ranking",               "related_to", 1.5)
add("Personalization",          "Data_Analysis",                "depends_on", 1.5)
add("Personalization",          "Content_Recommendation",       "similar_to", 1.8)
add("Personalization",          "A_B_Testing",                  "depends_on", 1.5)
add("Personalization",          "LLM_Engineering",              "related_to", 1.3)

# ════════════════════════════════════════════════════════
# 6. 신규 노드: Content_Recommendation
# ════════════════════════════════════════════════════════
add("Content_Recommendation",   "Recommendation_System",        "similar_to", 1.8)
add("Content_Recommendation",   "Personalization",              "similar_to", 1.8)
add("Content_Recommendation",   "Machine_Learning",             "depends_on", 1.8)
add("Content_Recommendation",   "Natural_Language_Processing",  "related_to", 1.5)
add("Content_Recommendation",   "Data_Analysis",                "depends_on", 1.5)
add("Content_Recommendation",   "LLM_Engineering",              "related_to", 1.3)

# ════════════════════════════════════════════════════════
# 7. 신규 노드: OnDevice_AI
# ════════════════════════════════════════════════════════
add("OnDevice_AI",              "AI_Accelerator",               "depends_on", 2.0)
add("OnDevice_AI",              "NPU",                          "used_in",    2.0)
add("OnDevice_AI",              "Model_Optimization",           "depends_on", 2.0)
add("OnDevice_AI",              "LLM_Inference",                "related_to", 1.8)
add("OnDevice_AI",              "MLOps",                        "related_to", 1.3)
add("OnDevice_AI",              "Firmware_Engineering",         "related_to", 1.3)
add("OnDevice_AI",              "AI_Engineering",               "related_to", 1.5)
add("OnDevice_AI",              "Speech_Recognition",           "related_to", 1.3)

# ════════════════════════════════════════════════════════
# 8. 신규 노드: Platform_AI
# ════════════════════════════════════════════════════════
add("Platform_AI",              "AI_Engineering",               "similar_to", 1.8)
add("Platform_AI",              "AI_Infra",                     "depends_on", 1.8)
add("Platform_AI",              "MLOps",                        "depends_on", 1.8)
add("Platform_AI",              "LLM_Engineering",              "related_to", 1.5)
add("Platform_AI",              "AI_Cloud_Platform",            "similar_to", 1.5)
add("Platform_AI",              "Recommendation_System",        "related_to", 1.3)
add("Platform_AI",              "Search_Ranking",               "related_to", 1.3)

# ════════════════════════════════════════════════════════
# 9. 기존 약한 노드 보강
# ════════════════════════════════════════════════════════
add("Recommendation_System",    "Natural_Language_Processing",  "related_to", 1.5)
add("Recommendation_System",    "LLM_Engineering",              "related_to", 1.5)
add("Recommendation_System",    "Search_Ranking",               "related_to", 1.8)
add("Recommendation_System",    "Content_Recommendation",       "similar_to", 1.8)
add("Recommendation_System",    "Personalization",              "similar_to", 1.8)
add("Recommendation_System",    "Data_Analysis",                "depends_on", 1.5)

add("AI_Engineering",           "LLM_Engineering",              "related_to", 1.8)
add("AI_Engineering",           "MLOps",                        "depends_on", 1.8)
add("AI_Engineering",           "AI_Infra",                     "related_to", 1.8)
add("AI_Engineering",           "AI_Research",                  "related_to", 1.5)
add("AI_Engineering",           "Platform_AI",                  "similar_to", 1.5)

add("AI_Infra",                 "LLM_Engineering",              "related_to", 1.5)
add("AI_Infra",                 "AI_Engineering",               "similar_to", 1.8)
add("AI_Infra",                 "AI_Cloud_Platform",            "related_to", 1.5)
add("AI_Infra",                 "Platform_AI",                  "similar_to", 1.5)

add("AI_Cloud_Platform",        "LLM_Engineering",              "related_to", 1.5)
add("AI_Cloud_Platform",        "MLOps",                        "depends_on", 1.8)
add("AI_Cloud_Platform",        "Platform_AI",                  "similar_to", 1.5)

add("Search_Engine",            "Search_Ranking",               "depends_on", 2.0)
add("Search_Engine",            "Natural_Language_Processing",  "depends_on", 1.8)
add("Search_Engine",            "LLM_Engineering",              "related_to", 1.5)
add("Search_Engine",            "Recommendation_System",        "related_to", 1.5)

add("NLP_and_LLM_Optimization", "LLM_Engineering",              "depends_on", 2.0)
add("NLP_and_LLM_Optimization", "Search_Ranking",               "related_to", 1.5)
add("NLP_and_LLM_Optimization", "Recommendation_System",        "related_to", 1.3)
add("NLP_and_LLM_Optimization", "Speech_Recognition",           "related_to", 1.3)

add("Computer_Vision",          "Multimodal",                   "related_to", 1.8)
add("Computer_Vision",          "Generative_AI_and_3D_Vision",  "related_to", 1.5)
add("Computer_Vision",          "OnDevice_AI",                  "related_to", 1.3)
add("Computer_Vision",          "LLM_Engineering",              "related_to", 1.3)

add("AI_Model_and_Distributed_Training", "LLM_Engineering",     "depends_on", 2.0)
add("AI_Model_and_Distributed_Training", "Model_Parallelism",   "depends_on", 2.0)
add("AI_Model_and_Distributed_Training", "Distributed_Training_Inference", "similar_to", 1.8)
add("AI_Model_and_Distributed_Training", "MLOps",               "related_to", 1.5)

# ════════════════════════════════════════════════════════
# NODE_ALIASES — 순수 SW AI 연구
# ════════════════════════════════════════════════════════
NEW_ALIASES = {
    "Multimodal": [
        "멀티모달", "multimodal", "멀티모달 AI",
        "이미지-텍스트", "Vision-Language", "VLM",
        "Visual Language Model", "멀티모달 모델",
        "CLIP", "GPT-4V", "이미지 언어 모델",
        "멀티모달 학습", "cross-modal",
    ],
    "Speech_Recognition": [
        "음성인식", "STT", "Speech-to-Text",
        "ASR", "Automatic Speech Recognition",
        "음성 언어 처리", "음성 AI", "TTS",
        "Text-to-Speech", "음성합성", "Whisper",
        "음성 모델", "spoken language processing",
    ],
    "Search_Ranking": [
        "검색 랭킹", "search ranking", "검색 알고리즘",
        "랭킹 모델", "검색 최적화", "검색 품질",
        "learning to rank", "LTR", "검색 관련성",
        "쿼리 이해", "query understanding",
        "검색 엔진 최적화", "검색 개선",
    ],
    "Personalization": [
        "개인화", "personalization", "개인 맞춤",
        "사용자 맞춤", "개인화 추천", "user personalization",
        "개인화 모델", "행동 기반 개인화",
    ],
    "Content_Recommendation": [
        "콘텐츠 추천", "content recommendation",
        "추천 시스템", "콘텐츠 큐레이션",
        "피드 추천", "뉴스 추천", "동영상 추천",
        "협업 필터링", "collaborative filtering",
        "콘텐츠 기반 필터링",
    ],
    "OnDevice_AI": [
        "온디바이스 AI", "on-device AI", "엣지 AI",
        "edge AI", "모바일 AI", "디바이스 AI",
        "경량화 모델", "모델 경량화", "온디바이스 추론",
        "on-device inference", "TinyML", "tiny ML",
    ],
    "Platform_AI": [
        "AI 플랫폼", "플랫폼 AI", "platform AI",
        "AI 서비스 플랫폼", "인터넷 AI 플랫폼",
        "AI 서비스 개발", "AI 제품 개발",
        "HyperCLOVA", "하이퍼클로바",
        "CLOVA", "클로바", "카카오 AI", "라인 AI",
    ],
    "AI_Research": [
        "AI 연구", "인공지능 연구", "AI researcher",
        "AI 리서처", "research scientist",
        "리서치 사이언티스트", "AI 과학자",
        "딥러닝 연구", "머신러닝 연구",
    ],
    "Frontier_AI_Research": [
        "프론티어 AI", "frontier AI", "기초 AI 연구",
        "AI 기초 연구", "fundamental AI research",
        "AGI 연구", "AI alignment", "AI safety",
    ],
    "AI_Engineering": [
        "AI 엔지니어링", "AI engineer", "AI 엔지니어",
        "응용 AI", "applied AI", "AI 개발",
        "AI 시스템 개발", "AI 솔루션 개발",
    ],
    "AI_Infra": [
        "AI 인프라", "AI infra", "AI infrastructure",
        "학습 인프라", "training infrastructure",
        "AI 클러스터", "GPU 클러스터",
        "AI 서버 운영", "딥러닝 인프라",
    ],
    "Recommendation_System": [
        "추천 시스템", "recommendation system",
        "추천 알고리즘", "추천 엔진",
        "RS", "RecSys", "개인화 추천",
        "협업 필터링", "행렬 분해",
    ],
}

# ════════════════════════════════════════════════════════
# 파일 패치
# ════════════════════════════════════════════════════════
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # 순수 SW AI 연구 노드 연결 보강 (2026-05-07)',
    '    # 네이버/카카오/라인 등 인터넷기업 AI 연구자 커버',
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
    '    # ══ 순수 SW AI 연구 aliases (2026-05-07) ══',
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
        alias_patch = '\n'.join(alias_lines)
        content = content[:na_end] + '\n' + alias_patch + content[na_end:]
        print('NODE_ALIASES 블록에 순수 SW AI 연구 항목 추가 완료')

with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
print(f'   보강된 alias 노드: {len(NEW_ALIASES)}개')
