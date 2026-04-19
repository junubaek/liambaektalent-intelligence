import json
import os
import concurrent.futures
from neo4j import GraphDatabase
from google import genai

with open('secrets.json', 'r') as f:
    secrets = json.load(f)
    GENAI_KEY = secrets.get("GEMINI_API_KEY", "")

if not GENAI_KEY:
    print("Warning: GEMINI_API_KEY not found in secrets.json.")
client = genai.Client(api_key=GENAI_KEY)

# Default Model: Gemini Flash Lite version (user requested)
MODEL_ID = 'gemini-2.5-flash-lite'

PROMPT = """아래 이력서를 보고 이 사람이 누구인지 한 문장으로 요약해줘.
형식: N년 경력의 [핵심역량] 전문가로 [주요 회사/경험]을 보유하고 있습니다.
반드시 한국어 1문장만 출력

이력서 내용:
{summary}"""

def process_candidate(candidate_id, summary):
    try:
        if not summary or len(summary) < 10:
            return candidate_id, "프로필 정보가 부족하여 요약할 수 없습니다."
            
        full_prompt = PROMPT.format(summary=summary)
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=full_prompt,
        )
        profile_text = response.text.replace('\n', ' ').strip()
        return candidate_id, profile_text
    except Exception as e:
        print(f"Error for {candidate_id}: {e}")
        return candidate_id, "요약 생성 중 오류가 발생했습니다."

def main():
    print("Loading cache...")
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cands = json.load(f)
        
    print(f"Loaded {len(cands)} candidates. Starting ThreadPoolExecutor...")
    
    # Optional: only process those missing profile_summary or a subset
    # But user requested "전체 2,962명 대상".
    # For now, to allow UI testing to succeed fast, let's process 곽창신 and 이범기 first
    first_batch = [c for c in cands if '곽창신' in c.get('name', '') or '이범기' in c.get('name', '') or '정영훈' in c.get('name', '')]
    rest = [c for c in cands if c not in first_batch]
    target_cands = first_batch + rest
    
    updated_profiles = {}
    
    # Process the first few synchronously for immediate UI use
    for c in first_batch:
        cid, text = process_candidate(c.get('id'), c.get('summary', ''))
        c['profile_summary'] = text
        updated_profiles[cid] = text
        print(f"Immediate Gen: {c.get('name')} -> {text}")
        
    # Overwrite cache with the immediate changes so UI sees them now
    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)
        
    # Then background the rest
    def bg_task():
        print("Starting massive background NLP summarization...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_c = {executor.submit(process_candidate, c.get('id'), c.get('summary', '')): c for c in rest}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_c)):
                c = future_to_c[future]
                cid, text = future.result()
                c['profile_summary'] = text
                updated_profiles[cid] = text
                
                if (i + 1) % 100 == 0:
                    print(f"Processed {i+1} candidates...")
                    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
                        json.dump(cands, f, ensure_ascii=False, indent=2)
                        
        print("Final JSON save...")
        with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
            json.dump(cands, f, ensure_ascii=False, indent=2)
            
        print("Writing to Neo4j...")
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
        with driver.session() as session:
            updates = [{'id': k, 'prof': v} for k, v in updated_profiles.items()]
            query = """
            UNWIND $batch AS row
            MATCH (c:Candidate {id: row.id})
            SET c.profile_summary = row.prof
            """
            session.run(query, batch=updates)
        print("Fully Complete!")
        
    # I'll just run bg_task synchronously in this script because I'll send it to the background using run_command
    bg_task()

if __name__ == "__main__":
    main()
