import sqlite3
import sys
import json
import time
import os
from google import genai
from google.genai import types

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
os.chdir(PROJECT_ROOT)

def run_repair():
    secrets_path = 'secrets.json'
    if not os.path.exists(secrets_path):
        print(f"Error: {secrets_path} does not exist.")
        return
        
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = json.load(f)
        
    client = genai.Client(api_key=secrets['GEMINI_API_KEY'])
    
    db_path = 'candidates.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Identify target candidates: active, raw_text > 500, lacking sector or summary
    cur.execute('''
        SELECT id, name_kr, raw_text, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND length(raw_text) > 500
        AND (
            (sector IS NULL OR sector='' OR sector='미분류')
            OR (profile_summary IS NULL OR profile_summary='' OR profile_summary='정보 없음')
        )
    ''')
    rows = cur.fetchall()
    print(f'1. [대상 분석] 보완이 필요한 지원자: {len(rows)}명')
    
    fixed = 0
    for cid, name, raw, sector, summary in rows:
        need_sector = not sector or sector in ('', '미분류')
        need_summary = not summary or summary in ('', '정보 없음')
        
        # Clean candidate name for prints
        clean_name = name.replace('[원본]', '').strip()
        
        prompt = f'''이력서를 분석해서 JSON으로만 답해줘. 다른 말 없이 JSON만.
{{
  "sector": "직무분야 (SW/Finance/Marketing/HR/Operations/Legal/Healthcare/AI반도체/BD/Data 중 가장 적합한 것)",
  "summary": "핵심 경력 2문장 요약 (한국어)"
}}

이력서:
{raw[:2000]}'''
        
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt]
            )
            # Remove potential markdown json fences
            text = resp.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            data = json.loads(text)
            
            new_sector = data.get('sector', sector) if need_sector else sector
            new_summary = data.get('summary', summary) if need_summary else summary
            
            # Map sectors logically to corporate sectors if needed, or keep as suggested
            # We'll keep the suggested one as Gemini produces it.
            
            # Set both is_neo4j_synced and is_pinecone_synced to 0
            # since they are updated and need re-indexing
            cur.execute('''UPDATE candidates SET 
                sector=?, profile_summary=?, is_neo4j_synced=0, is_pinecone_synced=0
                WHERE id=?''', (new_sector, new_summary, cid))
                
            fixed += 1
            print(f"   [{fixed}/{len(rows)}] {clean_name} -> Sector: {new_sector}")
            
            if fixed % 10 == 0:
                conn.commit()
                print(f'   -- {fixed}명 중간 저장 완료 --')
            time.sleep(0.5)
        except Exception as e:
            print(f'   ❌ 오류 {clean_name}: {e}')
            
    conn.commit()
    conn.close()
    print(f'\n🎉 2. [완료] 총 {fixed}명에 대한 데이터 보완 업데이트 성공!')

if __name__ == "__main__":
    run_repair()
