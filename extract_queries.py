import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load the golden dataset
try:
    with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

queries = set()
for entry in golden_data:
    if isinstance(entry, dict):
        q = entry.get('jd_query', '')
        if q:
            queries.add(q.strip())

queries = list(queries)

print(f"Total Unique Queries: {len(queries)}\n")
print("=== 전체 쿼리 목록 ===")
for q in queries:
    print(f"- {q}")

# 휴리스틱 분류
# 순수 스킬: 대문자로 시작하는 영문명사 혹은 기술명사들만 있을 때 (알파벳, 공백, +/#/.)
# 자연어형: 한글 문장, 조사(은,는,이,가,경험,자,우대) 등이 포함되었을 때
# 혼합형: 둘 다 있거나 기타
pure_skill = []
natural_lang = []
mixed = []

for q in queries:
    # 한글 조사나 특징적 형태소 포함 (경험, 개발자, 우대, 년차 등)
    if any(k in q for k in ["경험", "개발자", "우대", "년차", "사람", "인재", "구함", "자격"]):
        natural_lang.append(q)
    # 한글 단어(일반 명사)가 섞여 있으면 혼합으로 간주
    elif any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in q):
        mixed.append(q)
    else:
        # 영어/기호 중심 스킬 쿼리
        pure_skill.append(q)

print(f"\n=== 휴리스틱 분류 통계 (단순 패턴 기반) ===")
print(f"1. 순수 스킬 키워드형 (영문 기술명 등): {len(pure_skill)}건")
print(f"2. 혼합형 (영문 기술 + 한글 직무/키워드): {len(mixed)}건")
print(f"3. 자연어형 (경험자, 우대 등 문장/단서 포함): {len(natural_lang)}건")

if mixed:
    print("\n[혼합형 샘플]")
    for x in mixed[:5]: print(" -", x)
if natural_lang:
    print("\n[자연어형 샘플]")
    for x in natural_lang[:5]: print(" -", x)

