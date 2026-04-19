with open('C:/Users/cazam/.gemini/antigravity/brain/bf9cf191-3e7a-4628-8914-c6b8c894b562/walkthrough.md', 'r', encoding='utf-8') as f:
    text = f.read()
text += '''
### 43. 웹서버 안정성 대규모 개선 (Phase 43)
사용자가 웹 화면이 자주 먹통(Shutdown)되는 현상을 보고하여 긴급 점검을 수행했습니다.

1. **FastAPI Event Loop Starvation 해결**:
   - 기존 코드에서 API 함수들이 `async def`로 정의되어 있었으나, 내부에서는 동기적 I/O(Notion API 요청 등)를 10초 이상 수행했습니다.
   - 이로 인해 **단 하나의 요청만 들어와도 서버의 이벤트 루프 전체가 블로킹**되어, 다른 사용자는 물론 웹 UI 렌더링까지 모두 멈춰버리는 "서버 마비" 증상이 있었습니다.
   - 라우터 정의에서 `async`를 모두 제거하여, FastAPI가 백그라운드 스레드풀에서 안전하게 병렬 처리하도록 전체 아키텍처를 교정했습니다.
2. **Notion Schema 필터 검증 에러 패치**:
   - V6 엔진이 호출될 때 `Functional Patterns` 속성이 Notion DB 내에서 `rich_text` 임에도 서버 코드에서는 `multi_select`로 요를 보내 HTTP 400 치명적 에러를 발생시켰습니다.
   - 데이터 타입을 맞추어 해당 필터 검증 에러를 소거하고, 결과 데이터를 정상적으로 불러오도록 패치했습니다.
'''
with open('C:/Users/cazam/.gemini/antigravity/brain/bf9cf191-3e7a-4628-8914-c6b8c894b562/walkthrough.md', 'w', encoding='utf-8') as f:
    f.write(text)
