import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# We will construct a clean list of queries and match them to the exact candidate IDs and names in candidates.db
ids_mapping = [
    {
        "query": "카카오 출신 백엔드 시니어 개발자",
        "ids": ["ba99c86f-562d-4193-8380-0e414bd19093"],
        "seniority": "Senior"
    },
    {
        "query": "삼성전자 경력 SoC 설계자",
        "ids": ["ae1ac997-651e-4c0d-9809-7d5d0b2f521b"],
        "seniority": "Middle"
    },
    {
        "query": "토스 출신 ML 엔지니어",
        "ids": ["ca4146b1-7c15-4854-8d90-80036bf284a9"],
        "seniority": "Senior"
    },
    {
        "query": "네이버 출신 검색 엔지니어",
        "ids": ["cf822061-7f61-4aad-bdde-345ed0d334c0"],
        "seniority": "Senior"
    },
    {
        "query": "리벨리온 또는 퓨리오사 NPU 경험자",
        "ids": ["18b0c77b-9d05-4f44-b210-4f08f0af74ef"],
        "seniority": "All"
    },
    {
        "query": "스타트업 CTO 경험 있는 개발자",
        "ids": ["8dfee6d3-a4df-4940-b523-92f9ff3f0f37"],
        "seniority": "Senior"
    },
    {
        "query": "IPO 준비 경험 있는 CFO",
        "ids": ["51844988-9683-41e5-8fb7-fadb9a3ad40c"],
        "seniority": "Senior"
    },
    {
        "query": "대규모 트래픽 경험 있는 DevOps",
        "ids": ["ca4146b1-7c15-4854-8d90-80036bf284a9"],
        "seniority": "Senior"
    },
    {
        "query": "글로벌 세일즈 경험 있는 엔터프라이즈 영업",
        "ids": ["8bfeaf26-b163-415f-89de-f0a3b763515d"],
        "seniority": "Senior"
    },
    {
        "query": "AI 스타트업 초기 멤버 ML 엔지니어",
        "ids": ["18b0c77b-9d05-4f44-b210-4f08f0af74ef"],
        "seniority": "All"
    }
]

golden_dataset_v9 = []

for q_item in ids_mapping:
    relevant_ids = []
    relevance_scores = {}
    actual_names = []
    
    for cid in q_item["ids"]:
        cur.execute("SELECT name_kr FROM candidates WHERE id = ?", (cid,))
        row = cur.fetchone()
        if row:
            name_kr = row[0]
            relevant_ids.append(cid)
            relevance_scores[cid] = 1.0
            actual_names.append(name_kr)
            
    golden_dataset_v9.append({
        "query": q_item["query"],
        "relevant_ids": relevant_ids,
        "relevance_scores": relevance_scores,
        "relevant_names": actual_names,
        "seniority": q_item["seniority"]
    })

with open('golden_dataset_v9.json', 'w', encoding='utf-8') as f:
    json.dump(golden_dataset_v9, f, ensure_ascii=False, indent=2)

print("golden_dataset_v9.json created successfully:")
for q in golden_dataset_v9:
    print(f"  Query: {q['query']} -> Relevant: {q['relevant_names']} ({q['relevant_ids']})")

conn.close()
