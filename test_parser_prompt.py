import sys
import os

# append the current directory to sys.path
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")

from dynamic_parser import parse_resume

dummy_text = "이력서 테스트 " * 20

text_clear = dummy_text + "카카오페이에서 정산 시스템 아키텍처를 직접 설계했습니다."
text_ambiguous = dummy_text + "이전 직장에서 정산 관련 업무에 일부 참여했습니다."

print("=== 명확한 문장 테스트 ===")
res_clear = parse_resume(text_clear)
print(res_clear)

print("\n=== 애매한 문장 테스트 ===")
res_ambiguous = parse_resume(text_ambiguous)
print(res_ambiguous)
