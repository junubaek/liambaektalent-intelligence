import json
import os
import glob
import re
import pdfplumber
import concurrent.futures

def extract_real_name(text):
    # e.g. "[리벨리온] 이범기(Treasury Manager)부문"
    # e.g. "이효성_자금_원본"
    c = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', text)
    c = c.replace('부문', '').replace('원본', '').strip()
    return c.split('_')[0].strip()

def regex_clean_text(text, name):
    # 1. find start position
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
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
        text = re.sub(r'\d{2,3}[-\.\s]\d{3,4}[-\.\s]\d{4}', '', text)
        
    lines = text.split('\n')
    clean_lines = []
    
    # regex matches to cover spaces
    remove_regexps = [
        r"이\s*름\s*:", r"성\s*명\s*:", r"생\s*년\s*월\s*일\s*:", 
        r"학\s*력\s*:", r"인\s*적\s*사\s*항", r"이\s*력\s*서", 
        r"^I\.", r"^II\.", r"^III\."
    ]
    name_regex = re.compile(rf"{name}\s*[\d\.\-]+", re.IGNORECASE) if name else None
    
    for line in lines:
        l = line.strip()
        if not l: continue
        
        skip = False
        for p in remove_regexps:
            if re.search(p, l):
                skip = True
                break
        if skip: continue
        
        if name_regex and name_regex.search(l):
            if len(l) < 30: continue
            
        clean_lines.append(l)

    return ' '.join(clean_lines)[:500].strip()

def extract_summary(pdf_path, name):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages[:3])
            return regex_clean_text(text, name)
    except Exception as e:
        return ""

def main():
    pdf_dir = os.path.abspath(os.path.join("..", "02_resume 전처리"))
    all_pdfs = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
    pdf_map = {}
    for p in all_pdfs:
        filename = os.path.basename(p)
        clean = extract_real_name(filename)
        pdf_map[clean] = p
        
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cands = json.load(f)

    def process(c):
        rn = c.get("name", "")
        # Force set fixed name if missing
        real_n = extract_real_name(rn)
        c["name_kr"] = real_n
        
        # Always re-extract from matched pdf to be safe for all candidates
        matched_pdf = None
        for key, path in pdf_map.items():
            if real_n and (real_n == key or real_n in key):
                matched_pdf = path
                break
                
        if matched_pdf:
            new_sum = extract_summary(matched_pdf, real_n)
            if new_sum:
                c["summary"] = new_sum
                
        return c

    print("Reparsing all candidates PDFs...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        cands = list(ex.map(process, cands))

    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
