from jd_compiler import api_search_v8
import json

res = api_search_v8('vLLM PyTorch llm serving')
with open('res.json', 'w', encoding='utf-8') as f:
    json.dump(res['matched'][:15], f, ensure_ascii=False, indent=2)
