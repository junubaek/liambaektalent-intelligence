from jd_compiler import api_search_v8

res_dict = api_search_v8('Kubernetes OpenStack Terraform')
res = res_dict.get('matched', [])
for i, r in enumerate(res):
    if r['name_kr'] == '최호진':
        print(f"Choi Ho-jin found at rank: {i+1}")
        print(f"Score: {r['score']}, Edges: {r['total_edges']}")
        break
else:
    print("Choi Ho-jin not found in extracted results.")
