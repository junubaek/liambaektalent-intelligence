import json
import re

def check_cache_names():
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    bad = []
    seen = set()
    for c in data:
        name = c.get('name_kr') or ''
        # Assume my stripping script takes place:
        pure = re.sub(r'\[.*?\]', '', name)
        pure = re.sub(r'\(.*?\)', '', pure)
        pure = pure.replace('이력서', '').replace('사본', '').replace('복사본', '').strip()
        pure_ko = re.sub(r'[^가-힣]', '', pure)
        
        if not pure_ko:
            if pure not in seen:
                bad.append(pure)
                seen.add(pure)
            continue
            
        if len(pure_ko) < 2 or len(pure_ko) > 4:
            if pure not in seen:
                bad.append(pure)
                seen.add(pure)
        elif any(x in pure_ko for x in ['경력기술', '프로젝트', '직무수행', '자기소개', '개발자', '기획자', '대표이사']):
            if pure not in seen:
                bad.append(pure)
                seen.add(pure)

    bad.sort()
    with open('bad_names_cache.json', 'w', encoding='utf-8') as f:
        json.dump(bad, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    check_cache_names()
