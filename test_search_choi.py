from jd_compiler import api_search_v8

res_dict = api_search_v8('Kubernetes OpenStack Terraform')
res = res_dict.get('matched', [])
print("Top 10:")
for i, r in enumerate(res[:10]):
    print(f"{i+1}. {r['name_kr']} - Score: {r['score']}")
