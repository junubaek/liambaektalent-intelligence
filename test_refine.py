import jd_compiler
import time

jd_text = "정산 PM"

print("\\n" + "="*80)
print("1. 최초 전체 검색 실행")
print("="*80)
start = time.time()
session_id = jd_compiler.run_jd_compiler(jd_text)
print(f">> [초기 검색 완료] 소요 시간: {time.time()-start:.2f}초 | 할당된 세션 UID: {session_id}\\n")

print("="*80)
print("2. Mode A (자연어 수정 - '백엔드 추가해줘')")
print("="*80)
start = time.time()
jd_compiler.run_jd_compiler(jd_text, session_id=session_id, refine_text="백엔드 경험 추가해줘")
print(f">> [Mode A 완료] 소요 시간: {time.time()-start:.2f}초\\n")

print("="*80)
print("3. Mode B (구조화 데이터 수정 - 'min_years=8, skills_to_add=Machine_Learning')")
print("="*80)
start = time.time()
jd_compiler.run_jd_compiler(jd_text, session_id=session_id, skills_to_add=["Machine_Learning"], refined_min_years=8)
print(f">> [Mode B 완료] 소요 시간: {time.time()-start:.2f}초\\n")
