import sys
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

queries = [
    'NPU 드라이버 커널 엔지니어',
    'LLM 서빙 추론 최적화',
    'SoC 아키텍트',
    '재무 FP&A 담당자',
    'DevOps 엔지니어',
    '백엔드 Node.js 개발자',
    'B2B 영업 세일즈',
    'Treasury Manager',
    'Data Scientist ML Engineer',
    'General Affairs Manager',
    'UIUX 디자이너',
]

targets = {
    'NPU 드라이버 커널 엔지니어': ['전형준', '이석현'],
    'LLM 서빙 추론 최적화': ['이석현', '송우석'],
    'SoC 아키텍트': ['강종훈'],
    '재무 FP&A 담당자': ['김상원'],
    'DevOps 엔지니어': ['윤석훈'],
    '백엔드 Node.js 개발자': ['김태욱'],
    'B2B 영업 세일즈': ['최경석'],
    'Treasury Manager': ['김대중'],
    'Data Scientist ML Engineer': ['김정수'],
    'General Affairs Manager': ['이상헌'],
    'UIUX 디자이너': ['이영도']
}

# The actual IDs in the restored DB / Aura caches
target_ids = {
    '전형준': '31f22567-1b6f-81ea-a60e-d03c4a266d15',
    '이석현': '2ef78c51-5423-4377-856e-9b76c336b335',
    '송우석': '076745e4-4709-4f29-88da-7a158f9855e1',
    '강종훈': '31f22567-1b6f-8121-a08f-d8610b5e1294',
    '김상원': '31f22567-1b6f-8108-9739-fe07884e2967',
    '윤석훈': '566db883-983f-4ba4-8f48-1c549784827d',
    '김태욱': '32e22567-1b6f-8157-92b6-fdcd99692173',
    '최경석': '33522567-1b6f-817e-a77b-ffc7e1b8d5d4',
    '김대중': '32e22567-1b6f-81c3-a567-fa97777d7f53',
    '김정수': '33522567-1b6f-81bb-83a2-ef99ae586714',
    '이상헌': 'db752f0f-0f1a-437c-a09d-43c20442ab7b',
    '이영도': '32e22567-1b6f-81a3-8891-c822c76ea374'
}

print("=== [작업 1] 11개 쿼리 실행 및 Top 5 분석 (Aura/Restored DB 기준) ===")
for q in queries:
    print(f"\n🔍 쿼리: '{q}'")
    try:
        res = jd_compiler.api_search_v9(prompt=q)
        matched = res.get("matched", [])
        
        # Print Top 5
        print("  [상위 5명 결과]")
        for rank, item in enumerate(matched[:5], 1):
            name = item.get("name") or item.get("name_kr")
            company = item.get("current_company") or item.get("company") or "미상"
            score = item.get("score") or item.get("final_score") or 0.0
            id_str = item.get("id") or item.get("uuid")
            print(f"    {rank}위: {name} ({company}) | Score: {score:.4f} | ID: {id_str}")
            
        # Target ranks check using actual active IDs
        q_targets = targets.get(q, [])
        for t_name in q_targets:
            t_id = target_ids.get(t_name)
            found = False
            for rank, item in enumerate(matched, 1):
                item_id = item.get("id") or item.get("uuid")
                name = item.get("name") or item.get("name_kr")
                if item_id == t_id or name == t_name:
                    company = item.get("current_company") or item.get("company") or "미상"
                    score = item.get("score") or item.get("final_score") or 0.0
                    id_str = item.get("id") or item.get("uuid")
                    print(f"  🎯 타겟 발견: {t_name} | {rank}위 | Score: {score:.4f} | ID: {id_str}")
                    found = True
                    break
            if not found:
                print(f"  ❌ 타겟 발견 실패: {t_name}")
    except Exception as e:
        print(f"  🚨 에러 발생: {e}")
