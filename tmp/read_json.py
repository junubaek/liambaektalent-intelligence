import json

try:
    with open('tmp/search_res.json', encoding='utf-8') as f:
        d = json.load(f)
        
    top5 = d.get('matched', d.get('candidates', []))[:5]
    print('Top 5:')
    for i, c in enumerate(top5):
        print(f"{i+1}. {c.get('이름')} | Score: {c.get('_score')} | Vector: {c.get('pinecone_score',0)} | Final: {c.get('total_score', c.get('_score'))} | Max: {c.get('_max_score')}")
        
    all_cands = d.get('matched', d.get('candidates', []))
    kim = next((c for c in all_cands if '김대중' in c.get('이름', '')), None)
    print('\nKim Dae-Jung:')
    if kim:
        print(f"Rank: {all_cands.index(kim)+1}")
        print(f"Score: {kim.get('_score')} | Vector: {kim.get('pinecone_score',0)} | Final: {kim.get('total_score', kim.get('_score'))} | Max: {kim.get('_max_score')}")
    else:
        print('Not found')
        
except Exception as e:
    print(f"Error: {e}")
