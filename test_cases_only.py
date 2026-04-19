import json
import os
import glob
import re
import pdfplumber

def extract_real_name(text):
    c = re.sub(r'\[.*?\]|\(.*?\)|\..*', '', text)
    c = c.replace('부문', '').replace('원본', '').strip()
    return c.split('_')[0].strip()

def regex_clean_text(text, name):
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

def main():
    pdf_dir = os.path.abspath(os.path.join("..", "02_resume 전처리"))
    all_pdfs = glob.glob(os.path.join(pdf_dir, "**", "*.pdf"), recursive=True)
    pdf_map = {}
    for p in all_pdfs:
        clean = extract_real_name(os.path.basename(p))
        pdf_map[clean] = p
        
    for name in ["이범기", "정영훈"]:
        if name in pdf_map:
            pdf_path = pdf_map[name]
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    text = ''.join(page.extract_text() or '' for page in pdf.pages[:3])
                    clean_text = regex_clean_text(text, name)
                    print(f"\n=================\n[{name}] Summary Preview:")
                    print(clean_text)
            except Exception as e:
                print(f"Failed for {name}: {e}")

if __name__ == "__main__":
    main()
