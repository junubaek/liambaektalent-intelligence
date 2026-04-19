import sys
sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')
import jd_compiler

print('--- Test 1 ---')
q1 = '5년차 이상 DevOps 엔지니어'
res1 = jd_compiler.api_search_v8(q1)
m1 = res1.get('matched', [])
if m1:
    print(f'1위: {m1[0].get("이름")} (Score: {m1[0].get("_score")})')

print('\\n--- Test 2 ---')
q2 = '6년차 이상 자금 담당자'
res2 = jd_compiler.api_search_v8(q2)
m2 = res2.get('matched', [])
if m2:
    print(f'1위: {m2[0].get("이름")} (Score: {m2[0].get("_score")})')
