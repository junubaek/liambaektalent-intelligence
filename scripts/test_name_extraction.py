import json
import re

def extract_name(raw):
    # Base normalization
    s = raw.replace('~$', '').replace('부문', '').replace('원본', '').replace('지원서', '')
    s = s.replace('.doc', '').replace('_영문', '').replace('_프로젝트', '')
    s = re.sub(r'\[.*?\]', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[_\-\s]+', '_', s) # Normalize separators to _
    
    parts = s.split('_')
    
    # Try to find a valid Korean name of 2-4 characters among the parts
    possible_names = []
    for p in parts:
        pure_ko = re.sub(r'[^가-힣]', '', p)
        if len(pure_ko) in [2, 3, 4] and pure_ko == p.replace(' ', ''): 
            # It's highly likely a name if it's purely korean and right length
            # Let's filter out non-name words
            if not any(w in pure_ko for w in ['개발', '기획', '영업', '디자인', '담당자', '무명', '마케터', '신사업']):
                possible_names.append(pure_ko)
                
    if len(possible_names) == 1:
        return possible_names[-1]
    elif len(possible_names) > 1:
        # Just pick the last valid korean block, usually names are at the end
        return possible_names[-1]
        
    return ""

def test_extract():
    with open('bad_names_cache.json', 'r', encoding='utf-8') as f:
        bad = json.load(f)
        
    results = {}
    for b in bad:
        results[b] = extract_name(b)
        
    for i, (k, v) in enumerate(list(results.items())[:20]):
        print(f"{k} => {v}")

if __name__ == "__main__":
    test_extract()
