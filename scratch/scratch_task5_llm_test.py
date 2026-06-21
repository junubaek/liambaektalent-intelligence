import sys
import os
import json
from openai import OpenAI

sys.path.append(os.path.abspath("C:/Users/cazam/Downloads/이력서자동분석검색시스템"))
from jd_compiler import parse_jd_with_llm, api_search_v9

# Load OpenAI Client
SECRETS_PATH = "C:/Users/cazam/Downloads/이력서자동분석검색시스템/secrets.json"
with open(SECRETS_PATH, "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))

# 1. Test 7 queries
queries = [
    "카카오 출신 백엔드 시니어 개발자",
    "삼성전자 경력 SoC 아키텍트",
    "스타트업 CFO 경험자",
    "10년차 이상 재무 담당자",
    "네카라쿠배 출신 ML 엔지니어",
    "McKinsey 출신 전략 컨설턴트",
    "LLM 서빙 추론 최적화 엔지니어",
]

print("="*60)
print("LLM QUERY PARSER TEST ON 7 QUERIES:")
print("="*60)

for idx, q in enumerate(queries, 1):
    res = parse_jd_with_llm(q, client)
    print(f"\n[{idx}] Query: {q}")
    print(json.dumps(res, ensure_ascii=False, indent=2))

# 2. Search Top 5 for "카카오 출신 백엔드 시니어 개발자"
print("\n" + "="*60)
print("SEARCH TOP 5 FOR '카카오 출신 백엔드 시니어 개발자':")
print("="*60)

search_q = "카카오 출신 백엔드 시니어 개발자"
results = api_search_v9(search_q)
for i, cand in enumerate(results.get("matched", [])[:5], 1):
    print(f"{i}. [{cand['name_kr']}] Score: {cand['final_score']} | Company: {cand['current_company']} | Years: {cand['total_years']} | Seniority: {cand['seniority']}")
