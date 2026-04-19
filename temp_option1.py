import os
import re

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
jd_path = os.path.join(ROOT_DIR, "jd_compiler.py")

with open(jd_path, "r", encoding="utf-8") as f:
    content = f.read()

injection_code = """
    # [Option 1 Patch] 약어 확장 로직
    try:
        from connectors.openai_api import OpenAIClient
        import json
        with open("secrets.json", "r", encoding="utf-8") as sf:
            s_data = json.load(sf)
        _openai = OpenAIClient(s_data.get("OPENAI_API_KEY", ""))
        sys_prompt = '''
        약어가 포함된 쿼리는 반드시 풀어서 해석해.
        예: IPO → 기업공개/상장, IR → 투자자관계, DFT → Design_for_Testability
        약어를 스킬 노드 검색 키워드에 확장 적용할 것.
        
        [확장 사전]
        IPO → 기업공개, 상장, IPO, 공모, 상장준비
        IR → 투자자관계, Investor_Relations, IR, 기업설명회
        DFT → Design_for_Testability, DFT, 테스트설계
        RTL → RTL_Design, Register_Transfer_Level
        SoC → SoC, System_on_Chip, 시스템반도체
        DFE → DFE, Decision_Feedback_Equalizer
        ASRS → ASRS, 자동창고, 자동화물보관
        SAP → SAP, ERP, SAP_ERP
        BI → Business_Intelligence, BI, 데이터시각화
        Tableau → Tableau, Data_Visualization, BI_Dashboard
        DevOps → DevOps, CI_CD, 개발운영
        SaaS → SaaS, 클라우드서비스, Software_as_a_Service
        Kotlin → Kotlin, Android_Development
        
        규칙: 입력된 쿼리에 위 약어가 있다면 풀어서 원본 쿼리에 덧붙인 띄어쓰기 구분 문자열을 반환하라. 약어가 없다면 원본 쿼리를 그대로 반환하라. 설명은 절대 적지 마라.
        '''
        _expanded = _openai.get_chat_completion(sys_prompt, jd_text)
        if _expanded and len(_expanded) > 2:
            import logging
            logging.getLogger(__name__).info(f"[LLM Expansion] {jd_text} -> {_expanded}")
            jd_text = _expanded
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"[LLM Expansion Failed] {e}")
"""

# Find def parse_jd_to_json(jd_text: str) -> Dict:
# and inject after global GLOBAL_GEMINI_CALL_COUNT
# using string replacement

if "def parse_jd_to_json(jd_text: str) -> Dict:" in content:
    target_str = """def parse_jd_to_json(jd_text: str) -> Dict:

    \"\"\"

    자연어 JD를 입력받아, 필수/우대 구조의 화학식 JSON 및 최소 연차 정보를 반환합니다.

    \"\"\"

    global GLOBAL_GEMINI_CALL_COUNT

    import re"""
    # Clean up whitespace issues for regex
    
    # A safer way
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("def parse_jd_to_json(jd_text: str) -> Dict:"):
            # insert after this line, once we see 'import re'
            for j in range(i+1, i+20):
                if "import re" in lines[j]:
                    lines.insert(j+1, injection_code)
                    break
            break
            
    with open(jd_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))
    print("Injection successful.")
else:
    print("Function not found.")
