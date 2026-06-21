"""
OntologyVectorIndex 클래스 + api_search_v9 통합 패치
- jd_compiler.py에 OntologyVectorIndex 클래스 추가 (모듈 로드 시 1회 초기화)
- api_search_v9 Step 1 직후에 LLM skills → 온톨로지 매칭 → conds 추가
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

TARGET_FILE = 'jd_compiler.py'

with open(TARGET_FILE, encoding='utf-8') as f:
    content = f.read()

# ──────────────────────────────────────────────
# Step 1: OntologyVectorIndex 클래스 삽입
# get_company_boost 앞에 삽입 (parse_jd_with_llm 바로 뒤)
# ──────────────────────────────────────────────
ONTOLOGY_CLASS = '''
class OntologyVectorIndex:
    """
    온톨로지 노드 벡터 인덱스 (Ontology Vector Index)
    - 노드명 단독 임베딩 (1515노드 × 1536차원)
    - LLM이 추출한 스킬명을 임베딩 → 코사인 유사도로 온톨로지 노드 탐색
    - exact match 미스 케이스 보완
    """
    def __init__(self, pkl_path='ontology_vectors.pkl'):
        self._nodes = []
        self._matrix = None
        self._skill_cache = {}  # skill_text → embedding 캐시
        try:
            import pickle, numpy as _np
            if not os.path.exists(pkl_path):
                logger.warning(f"[OntologyVectorIndex] {pkl_path} not found. Disabled.")
                return
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
            self._nodes = [item['node'] for item in data]
            matrix = _np.array([item['vector'] for item in data])
            # 행별 정규화 (코사인 유사도 = 내적)
            norms = _np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self._matrix = matrix / norms
            logger.info(f"[OntologyVectorIndex] Loaded {len(self._nodes)} nodes, {self._matrix.shape[1]}dim")
        except Exception as e:
            logger.warning(f"[OntologyVectorIndex] Init failed: {e}")

    def search(self, skill_text: str, openai_client, threshold=0.80, top_k=5) -> list:
        """스킬명을 임베딩해서 유사한 온톨로지 노드 반환"""
        if self._matrix is None or not skill_text:
            return []
        import numpy as _np
        try:
            # 캐시 확인
            if skill_text in self._skill_cache:
                q_vec = self._skill_cache[skill_text]
            else:
                resp = openai_client.embeddings.create(
                    input=[skill_text], model="text-embedding-3-small"
                )
                q_arr = _np.array(resp.data[0].embedding)
                q_vec = q_arr / (_np.linalg.norm(q_arr) or 1.0)
                self._skill_cache[skill_text] = q_vec
            sims = self._matrix @ q_vec
            top_idx = _np.argsort(-sims)
            return [(self._nodes[i], float(sims[i]))
                    for i in top_idx if float(sims[i]) >= threshold][:top_k]
        except Exception as e:
            logger.warning(f"[OntologyVectorIndex] search failed: {e}")
            return []

_ontology_index = OntologyVectorIndex()

'''

INSERT_MARKER = "def get_company_boost(company_name, conditions, conn):"
if INSERT_MARKER not in content:
    print("ERROR: get_company_boost marker not found!")
    sys.exit(1)

if "class OntologyVectorIndex" in content:
    print("OntologyVectorIndex already present, skipping class insert.")
else:
    idx = content.find(INSERT_MARKER)
    content = content[:idx] + ONTOLOGY_CLASS + content[idx:]
    print(f"Inserted OntologyVectorIndex class ({len(ONTOLOGY_CLASS)} chars)")

# ──────────────────────────────────────────────
# Step 2: api_search_v9 에서 LLM parsing 블록 직후에
# 온톨로지 벡터 매칭 로직 추가
# ──────────────────────────────────────────────
OLD_ABBREV_BLOCK = """    conds = map_abbreviations_to_conds(prompt, conds)
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)"""

NEW_ABBREV_BLOCK = """    conds = map_abbreviations_to_conds(prompt, conds)
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)

    # Ontology Vector Index: LLM skills → 유사 온톨로지 노드 탐색
    _llm_skills_for_onto = _jd_llm.get('skills', []) if '_jd_llm' in dir() else []
    if _llm_skills_for_onto:
        existing_skill_names = {c.get('skill') for c in conds}
        _onto_added = []
        for _skill_txt in _llm_skills_for_onto[:6]:  # 최대 6개 skill만
            _matches = _ontology_index.search(_skill_txt, _openai_client,
                                              threshold=0.80, top_k=3)
            for _node, _sim in _matches:
                if _node not in existing_skill_names:
                    conds.append({"action": "MANAGED", "skill": _node,
                                  "is_mandatory": False, "source": "ontology_vector"})
                    existing_skill_names.add(_node)
                    _onto_added.append(f"{_node}({_sim:.2f})")
        if _onto_added:
            logger.info(f"[OntologyVector] Added {len(_onto_added)} nodes: {_onto_added}")"""

if OLD_ABBREV_BLOCK not in content:
    print("ERROR: abbreviation block not found!")
    # 디버그: 유사한 패턴 탐색
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'inject_node_affinity' in line:
            print(f"  Line {i+1}: {line}")
    sys.exit(1)

content = content.replace(OLD_ABBREV_BLOCK, NEW_ABBREV_BLOCK, 1)
print("Patched: ontology vector search added after conds building")

# 파일 저장
with open(TARGET_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n모든 패치 완료! 파일 크기: {len(content)} chars")

# 문법 검사
import ast
try:
    ast.parse(content)
    print("문법 검사: OK ✅")
except SyntaxError as e:
    print(f"문법 오류: {e}")
    sys.exit(1)
