import urllib.request
import json

url = "http://127.0.0.1:8000/api/search-v8"
data = json.dumps({"jd_text": "6년차 이상 자금 담당자", "search_type": "deep"}).encode("utf-8")
headers = {"Content-Type": "application/json"}

print("Calling API...")
try:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode('utf-8')
        d = json.loads(body)
        
    top5 = d.get('matched', d.get('candidates', []))[:5]
    print("\nTop 5:")
    for i, c in enumerate(top5):
        print(f"{i+1}. {c.get('이름')} | Score: {c.get('_score')} | Vector: {c.get('pinecone_score',0)} | Max: {c.get('_max_score')}")
        
    all_cands = d.get('matched', d.get('candidates', []))
    kim = next((c for c in all_cands if '김대중' in c.get('이름', '')), None)
    print('\nKim Dae-Jung:')
    if kim:
        print(f"Rank: {all_cands.index(kim)+1}")
        print(f"Score: {kim.get('_score')} | Vector: {kim.get('pinecone_score',0)} | Max: {kim.get('_max_score')}")
    else:
        print('Not found')
        
except Exception as e:
    print(f"API Error: {e}")
