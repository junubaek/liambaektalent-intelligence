import sys
sys.stdout.reconfigure(encoding='utf-8')
from scratch_process_exactly_13 import force_process_file

print("Processing 최성우...")
res1 = force_process_file("[리벨리온] 최성우(NPU Runtime Software Engineer)부문.pdf")
print("Result 최성우:", res1)

print("\nProcessing 전형준...")
res2 = force_process_file("[리벨리온] 전형준(Moreh Software Engineer)부문.pdf")
print("Result 전형준:", res2)
