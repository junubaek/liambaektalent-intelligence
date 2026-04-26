import os, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')
from google import genai

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

api_key = os.environ.get('GEMINI_API_KEY') or secrets.get('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD

# 고아 노드 목록
all_nodes = set(CANONICAL_MAP.values())
orphans = sorted([n for n in all_nodes if n not in UNIFIED_GRAVITY_FIELD])
print(f'고아 노드: {len(orphans)}개', flush=True)

if len(orphans) == 0:
    print('생성할 고아 노드가 없습니다.')
    sys.exit(0)

# 기존 노드 목록 (참조용)
existing_nodes = list(UNIFIED_GRAVITY_FIELD.keys())[:80]

new_fields = {}
BATCH = 20

for i in range(0, len(orphans), BATCH):
    batch = orphans[i:i+BATCH]
    
    prompt = f'''
당신은 HR/채용 온톨로지 전문가입니다.
아래 직무/기술 노드들에 대해 중력장을 설계해주세요.

기존 노드 목록 (참조용):
{json.dumps(existing_nodes, ensure_ascii=False)}

설계 대상 노드들:
{json.dumps(batch, ensure_ascii=False)}

각 노드에 대해:
- core_attracts: 이 노드와 가장 핵심적으로 연관된 노드 2~4개 (가중치 0.6~0.9)
- repels: 이 노드와 명확히 다른 직군 노드 1~2개 (가중치 -0.2~-0.4)

규칙:
1. core_attracts/repels의 노드명은 반드시 기존 노드 목록에서 선택하세요. 기존 노드 목록에 없는 노드는 절대로 사용하지 마세요.
2. 노드명은 영문만 사용하세요.
3. repels는 완전히 다른 직군일 때만 설정하세요.

오직 올바른 JSON 형식으로만 반환하세요. 앞뒤 설명이나 마크다운 백틱은 넣지 마세요:
{{
  "NodeName1": {{
    "core_attracts": {{"NodeA": 0.8, "NodeB": 0.7}},
    "repels": {{"NodeC": -0.3}}
  }}
}}
'''

    try:
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = resp.text.strip()
        if '```' in text:
            parts = text.split('```')
            if len(parts) > 1:
                text = parts[1]
            if text.startswith('json'):
                text = text[4:]
        
        parsed = json.loads(text.strip())
        new_fields.update(parsed)
        print(f'  {i+len(batch)}/{len(orphans)} 처리 완료', flush=True)
    except Exception as e:
        print(f'  배치 {i} 실패: {e}', flush=True)
        print(f'  Raw text: {resp.text if "resp" in locals() else "N/A"}', flush=True)
    
    time.sleep(1)

print(f'\n총 생성된 중력장: {len(new_fields)}개', flush=True)

if new_fields:
    addition = '\n# --- Auto-generated Gravity Fields (229 orphan nodes) ---\n'
    addition += 'UNIFIED_GRAVITY_FIELD.update(' + json.dumps(new_fields, ensure_ascii=False, indent=2) + ')\n'

    with open('ontology_graph.py', 'a', encoding='utf-8', errors='surrogateescape') as f:
        f.write(addition)
    print('ontology_graph.py 업데이트 완료', flush=True)
