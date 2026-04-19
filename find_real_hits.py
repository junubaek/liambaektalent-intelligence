import json
from jd_compiler import api_search_v8

def find_5_real_hits():
    golden = json.load(open('golden_dataset.json', encoding='utf-8'))
    positives = [i for i in golden if i['label'] == 'positive']
    
    hits = []
    
    for item in positives:
        q = item['jd_query']
        t = item['candidate_name']
        
        try:
            res = api_search_v8(prompt=q)
        except:
            continue
            
        matched = res.get('matched', [])
        names = [c.get('name', c.get('이름', '')) for c in matched]
        
        if t in names:
            hits.append((q, t))
            print(f"FOUND VALID HIT IN FUNNEL: {t} for query {q}")
            if len(hits) == 5:
                break
                
    print("FINISHED:", hits)

if __name__ == '__main__':
    find_5_real_hits()
