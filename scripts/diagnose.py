import sys
import urllib.request
import json
PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)
from connectors.notion_api import HeadhunterDB

db = HeadhunterDB()

payload = {
    "query": "HW2팀_87조건(원본)",
    "filter": {"value": "page", "property": "object"}
}
res = db.client._request("POST", "search", payload)

if res and res.get('results'):
    target = res['results'][0]
    print(f"URL: {target.get('url')}")
    
    # fetch props
    props = db.client.extract_properties(target)
    print(f"Google Drive Link: {props.get('구글드라이브_링크')}")
    
    text = db.fetch_candidate_details(target['id'])
    print(f"Text from deep fetch: {len(text)} chars")
    
    res = db.client._request('GET', f"blocks/{target['id']}/children")
    if res and "results" in res:
        types = [b['type'] for b in res['results']]
        print(f"Top-level block types: {types}")
        
        for b in res['results']:
            if b['type'] == 'file':
                print(f"File block details: {b['file']}")
            elif b['type'] == 'pdf':
                print(f"PDF block details: {b['pdf']}")
            elif b['type'] == 'child_page':
                print(f"Child page: {b['child_page']}")
