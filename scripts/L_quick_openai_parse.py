import sqlite3
import json
import time
from openai import OpenAI

def main():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
        
    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
    
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    c.execute("SELECT id, raw_text FROM candidates WHERE is_parsed=0 AND is_duplicate=0")
    targets = c.fetchall()
    
    print(f"Parsing {len(targets)} candidates natively with OpenAI...")
    success = 0
    
    for row in targets:
        cid, text = row
        cid_str = str(cid).replace('-', '')
        cinfo = cache_map.get(cid_str)
        if not cinfo: continue
        
        prompt = f"""
        당신은 이력서 요약 에이전트입니다.
        아래 이력서를 읽고, 구체적인 핵심 경험과 성과 중심으로 3~5문장으로 요약하세요.
        반드시 전화번호(010-), 이메일, 주소, 생년월일 등의 개인정보는 완전히 제외해야 합니다.
        
        이력서 내용: {text[:4000]}
        """
        
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            summary = res.choices[0].message.content
            
            cinfo['summary'] = summary
            c.execute("UPDATE candidates SET is_parsed=1, is_neo4j_synced=0, is_pinecone_synced=0 WHERE id=?", (cid,))
            success += 1
            print(f"Parsed {cid_str}")
        except Exception as e:
            print(f"Failed {cid_str}: {e}")
            
    conn.commit()
    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    conn.close()
    
if __name__ == "__main__":
    main()
