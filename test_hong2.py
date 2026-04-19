from jd_compiler import api_search_v8

def test():
    res = api_search_v8('vllm pytorch llm serving machine learning')
    for i, r in enumerate(res['matched'][:15]):
        print(f"{i+1}. {r.get('name') or '미상'} (Score: {r['score']})")

if __name__ == '__main__':
    test()
