import json
import re
from neo4j import GraphDatabase

def extract_company_from_summary(summary):
    if not summary:
        return ""
    
    # 1st priority: "현재", "Present", "재직중", "재직 중"
    chunks = re.split(r'\n|▪||-|\*', summary)
    for chunk in chunks:
        # Check if the chunk has active keywords
        if re.search(r'(현재|재직\s*중|Present|~\s*2025|~\s*2026)', chunk, re.IGNORECASE):
            # We want to extract the company name adjacent to these keywords
            # Examples:
            # 2020.03 ~ 현재 : OOO컴퍼니
            # OOO컴퍼니 (2020~현재)
            # OOO컴퍼니 재직 중 
            
            # Use regex to find potential company names.
            # Match formats like:
            # 1. "... : [Company]"
            # 2. "[Company] (..."
            # 3. "[Company] 재직..."
            # We'll just grab the most prominent capitalized or Korean string that isn't dates/keywords.
            cleaned_chunk = re.sub(r'(현재|재직\s*중|Present|~\s*\d{4}|\d{4}\.\d{2}|\d{4}년|\d{2}월|~|-)', ' ', chunk, flags=re.IGNORECASE).strip()
            
            # After removing dates and keywords, let's extract the first valid sequence of characters
            match = re.search(r'([가-힣A-Za-z0-9&]+(?:\s[가-힣A-Za-z0-9&]+){0,2})', cleaned_chunk)
            if match:
                candidate = match.group(1).strip()
                # Exclude generic words
                invalid_words = ["기간", "주요", "담당", "업무", "경력", "이력", "소속", "직함", "직무", "팀장", "매니저", "팀원", "프로젝"]
                if len(candidate) > 1 and not any(w in candidate for w in invalid_words):
                    return candidate
                    
    # Strict fallback: DO NOT guess if there's no explicit current keyword
    return ""

def get_current_company(raw_name, summary):
    # 전면 수정: 파일명 의존 금지. summary에서만 추출
    c = extract_company_from_summary(summary)
    return c if c else ""

def main():
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
    
    print("Loading cache...")
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cands = json.load(f)
        
    updates = []
    
    for c in cands:
        name_raw = c.get('name', '')
        summary = c.get('summary', '')
        
        comp = get_current_company(name_raw, summary)
        
        # update dict
        c['current_company'] = comp
        
        cid = c.get('id')
        if cid:
            updates.append({'id': cid, 'comp': comp})
            
    print(f"Updating JSON cache for {len(cands)} candidates...")
    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)
        
    print(f"Batch updating Neo4j {len(updates)} nodes...")
    with driver.session() as session:
        # Use UNWIND for fast batch update
        query = """
        UNWIND $batch AS row
        MATCH (c:Candidate {id: row.id})
        SET c.current_company = row.comp
        """
        session.run(query, batch=updates)
        
    print("Completed current_company extraction!")

if __name__ == "__main__":
    main()
