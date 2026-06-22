import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
from jd_compiler import api_search_v9
result = api_search_v9('DevOps Engineer Kubernetes', 'debug_name')
for r in result.get('matched', [])[:10]:
    print(r.get('id','')[:8], '|', r.get('name_kr','[없음]'), '|', r.get('current_company',''), '|', round(r.get('final_score',0),3))
