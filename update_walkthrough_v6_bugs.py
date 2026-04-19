with open('C:/Users/cazam/.gemini/antigravity/brain/bf9cf191-3e7a-4628-8914-c6b8c894b562/walkthrough.md', 'r', encoding='utf-8') as f:
    text = f.read()
text += '''
### 45. "전혀 안맞는 사람" 출력 3대 치명적 버그 수정 (The "Completely Wrong People" Fixes)
사용자께서 두 번째 테스트를 하셨을 때 엉뚱한 결과가 다시 나온 원인을 백엔드 파이프라인(V6) 디버깅 및 가상 환경 시뮬레이션을 통해 완벽하게 추적하고 해결했습니다. **총 3가지의 맞물려 있던 치명적 버그**를 제거했습니다.

1. **Neo4j Negative Gravity 오버라이트(Overwrite) 버그**:
   - `search_engine_v6.py` 내에서 `exclude_nodes` (재무회계)에 `-1.0`의 감점 중력을 부여한 직후, 후속 라인에서 `max(1.0, ...)` 합산 로직이 덮어써져 **음수 패널티가 다시 양수(+1.0)로 초기화**되는 심각한 오류가 있었습니다. 이 때문에 회계사들이 오히려 가산점을 받고 튀어나왔습니다. 해당 오버라이트 라인을 삭제하여 **-1.0의 영구적 감점**이 보장되도록 패치했습니다.

2. **한글 자연어 -> V7 마스터 노드 번역(Alias) 누락**:
   - 그래프 구조에 `Product_Manager`와 `Payment_and_Settlement_System`은 존재했으나, NLU가 파싱해 낸 `"정산 시스템"`이나 `"정산 데이터"`라는 한국어 단어를 그래프에서 매칭해 주지 못해 허공으로 증발해버렸습니다. `CANONICAL_MAP` 사전에 **완벽한 한국어 동의어 매핑 레이어(Alias Layer)**를 추가하여 Neo4j가 해당 단어들을 즉시 인지하게 만들었습니다.

3. **Notion API 400 Validation 에러 (연차 필터 스트링 불일치)**:
   - 프롬프트에 기재된 "6년 차 이상"이 번역 필터 없이 고스란히 Notion DB 쿼리로 넘어가면서, `Senior`, `Middle` 등을 기대하는 DB가 **HTTP 400 에러를 뿜으며 0명의 텍스트 필터 결과를 반환**하는 현상이 있었습니다. (이 때문에 Neo4j 검색 엔진이 허공에 삽질을 하고 있었습니다). UI/NLU의 한글 연차 문자열을 엔진 1차 통과 직전에 영문 `Seniority Bucket` 포맷으로 자동 변환하는 `sen_map`을 적용했습니다.

**🔥 치명적 확인 사항 (서버 재시작 필요)**:
현재 실행 중이신 `run_site.bat` 터미널 프로세스는 소스코드가 실시간으로 반영되는 `--reload` (Hot-reload) 모드가 꺼져 있었습니다. 따라서 앞서 제가 고쳐드린 모든 Python 서버 로직이 하나도 반영되지 않은 예전 껍데기 서버에서 돌고 있었기 때문에 똑같은 오류가 나타났던 것입니다. 해당 터미널을 끄고 다시 켜주시면 완벽하게 적용됩니다!
'''
with open('C:/Users/cazam/.gemini/antigravity/brain/bf9cf191-3e7a-4628-8914-c6b8c894b562/walkthrough.md', 'w', encoding='utf-8') as f:
    f.write(text)
