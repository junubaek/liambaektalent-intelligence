import sys
import io

# Set stdout to utf-8 explicitly to avoid console codepage issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from jd_compiler import api_search_v8

res = api_search_v8("IPO/펀딩 대비 자금 담당자 6년차")
print(f"Total returned: {len(res['matched'])}")

found = []
for i, c in enumerate(res['matched']):
    name = c['이름']
    print(f"{i+1}. {name} | Score: {c['_score']} | Hist: {c.get('_mechanics', '').split('<br><b>')[-1] if '<br><b>' in c.get('_mechanics', '') else 'None'}")
    if "김대중" in name or "이범기" in name:
        found.append((i+1, name, c['_score']))

print("\n--- TARGET CANDIDATES ---")
for f in found:
    print(f"Rank {f[0]}: {f[1]} - Score: {f[2]}")
    
if not found:
    print("김대중, 이범기 were NOT found in the Top 20.")
