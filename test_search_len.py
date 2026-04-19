import sys
sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')
import jd_compiler

print('--- Test: Null Byte Filter Integration ---')
candidates = jd_compiler.get_candidates_from_cache()

count_passed = 0
for c in candidates:
    rt = str(c.get('raw_text', '') or '')
    if rt.replace('\\x00', '').strip():
        count_passed += 1

print(f"Total passing candidates without null bytes filter: {count_passed} / {len(candidates)}")
