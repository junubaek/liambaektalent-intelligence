import jd_compiler
import time

jd_text = "주요 업무: FP&A, 경영분석 및 재무기획 담당 6년차"

print("--- Test Call 1 (Might evaluate or hit existing cache from above script) ---")
start = time.time()
r1 = jd_compiler.parse_jd_to_json(jd_text)
print(f"Call 1 Elapsed: {time.time() - start:.3f}s")
print(f"Result: {r1}\\n")

print("--- Test Call 2 (Must be a cache hit) ---")
start = time.time()
r2 = jd_compiler.parse_jd_to_json(jd_text)
print(f"Call 2 Elapsed: {time.time() - start:.3f}s")
print(f"Result: {r2}")
