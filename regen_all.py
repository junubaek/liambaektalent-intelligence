import json
import os
import glob
import re
import pdfplumber
import concurrent.futures
from neo4j import GraphDatabase

def fix_name(raw_name):
    # '이효성_자금_원본', '유희선_자금_원본.pdf', '[BEP] 임준형_...'
    # -> strip [], (), .pdf -> split('_') -> first part
    clean = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', raw_name).strip()
    parts = clean.split('_')
    if parts:
        return parts[0]
    return clean

def extract_summary(pdf_path, name):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages[:3]) # First 3 pages
            
            # Clean useless strings first or later?
            # Start position matching
            keywords = ["간단프로필", "경력기술서", "주요경력"]
            
            start_pos = -1
            for kw in keywords:
                idx = text.find(kw)
                if idx != -1:
                    start_pos = idx + len(kw)
                    break
                    
            if start_pos != -1:
                text = text[start_pos:]
            else:
                # remove emails and phone numbers from the start
                text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
                text = re.sub(r'\d{2,3}[-\.\s]\d{3,4}[-\.\s]\d{4}', '', text)
            
            lines = text.split('\n')
            clean_lines = []
            
            # Remove specific patterns
            remove_patterns = ["이름 :", "성명 :", "생년월일 :", "학력 :", "인적사항", "이 력 서", "I.", "II.", "III."]
            
            for line in lines:
                l = line.strip()
                if not l: continue
                
                # Check for remove patterns
                skip = False
                for p in remove_patterns:
                    if p in l:
                        skip = True
                        break
                if skip: continue
                
                # Check for "Name + Birthdate" (e.g., 홍길동 1990)
                if name and name in l and re.search(r'\d{2,4}', l):
                    if len(l) < 30: # It's probably just a header line
                        continue
                        
                clean_lines.append(l)

            clean_text = ' '.join(clean_lines)
            return clean_text[:500].strip()
    except Exception as e:
        return ""


def main():
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
    
    # 1. Update Neo4j names
    with driver.session() as session:
        nodes = session.run("MATCH (c:Candidate) RETURN c.id AS id, c.name AS name, c.name_kr AS name_kr")
        updates = []
        for n in nodes:
            name = n['name'] or ''
            name_kr = n['name_kr'] or ''
            if '원본' in name or '자금' in name or '원본' in name_kr or '자금' in name_kr:
                # If name_kr is just "자금" or "재무" or contains them, try to fix it from name
                fixed_name = fix_name(name)
                updates.append((n['id'], fixed_name))
        
        print(f"Fixing {len(updates)} bad names in Neo4j...")
        for cid, fn in updates:
            session.run("MATCH (c:Candidate {id: $id}) SET c.name_kr = $fn, c.name = $fn", id=cid, fn=fn)

    # 2. Get PDFs
    pdf_dir = os.path.abspath(os.path.join("..", "02_resume 전처리"))
    all_pdfs = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
    pdf_map = {}
    for p in all_pdfs:
        filename = os.path.basename(p)
        clean = fix_name(filename)
        pdf_map[clean] = p
        
    print(f"Found {len(pdf_map)} PDFs.")

    # 3. Read cache
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cands = json.load(f)

    # 4. Process cands
    def process(c):
        raw_name = c.get("name", "")
        fixed_name = fix_name(raw_name) if '원본' in raw_name or '자금' in raw_name else raw_name
        
        # fix the dict
        c["name"] = fixed_name
        c["name_kr"] = fixed_name
        
        # Extract summary
        matched_pdf = None
        for key, path in pdf_map.items():
            if fixed_name and fixed_name in key:
                matched_pdf = path
                break
                
        if matched_pdf:
            new_sum = extract_summary(matched_pdf, fixed_name)
            if new_sum and len(new_sum) > 10:
                c["summary"] = new_sum
                
        return c

    print("Extracting summaries...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        cands = list(ex.map(process, cands))

    # sector calc
    sector_keywords = {
        "Finance": ["자금", "treasury", "재무", "회계", "fx", "결산", "cash flow", "ir", "ipo", "펀딩", "투자"],
        "PRODUCT": ["pm", "기획", "서비스", "ux", "로드맵", "스프린트", "product", "어드민", "앱", "플랫폼"],
        "SW": ["개발", "backend", "frontend", "서버", "api", "python", "java", "아키텍처", "인프라"],
        "DATA": ["데이터", "분석", "sql", "파이프라인", "etl", "대시보드", "bi", "모델링"],
        "AI": ["머신러닝", "딥러닝", "llm", "ai", "nlp", "추천", "알고리즘", "모델"],
        "STRATEGY": ["전략", "경영기획", "컨설팅", "m&a", "사업기획", "신사업", "pmi", "전략기획"],
        "HR": ["인사", "채용", "조직", "hr", "인재", "보상", "평가", "리크루팅"]
    }
    
    for c in cands:
        s = c.get("summary", "").lower()
        if not s:
            c["sector"] = "미상"
            continue
        scores = {sec: 0 for sec in sector_keywords}
        for sec, keywords in sector_keywords.items():
            for kw in keywords:
                scores[sec] += s.count(kw.lower())
        m = max(scores, key=scores.get)
        c["sector"] = m if scores[m] > 0 else "미상"

    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)

    # Output verification
    for c in cands:
        if '이범기' in c.get('name', '') or '정영훈' in c.get('name', ''):
            print(f"\n[{c['name']}] Summary:\n{c.get('summary')}")
            
    # Output bad name fix test
    for c in cands:
        if '이효성' in c.get('name','') or '유희선' in c.get('name',''):
            print(f"\nFixed Name Check -> {c.get('name')}")

if __name__ == "__main__":
    main()
