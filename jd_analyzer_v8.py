
import json
import os
from connectors.gemini_api import GeminiClient

class JDAnalyzerV8:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        # Load v8.0 Ontology
        ontology_path = os.path.join(os.path.dirname(__file__), "headhunting_engine/universal_ontology_v8.json")
        try:
            with open(ontology_path, "r", encoding="utf-8") as f:
                self.ontology = json.load(f)
        except:
            self.ontology = {}

    def analyze(self, jd_text: str) -> dict:
        """
        [v8.0] NEXT-GEN JD Intelligence (Gemini 3.0 Flash)
        Extracts 18-Sector mapping, Functional Patterns, and Reciprocal Tags.
        """
        allowed_sectors = [
            "SW", "HW", "반도체", "AI", "보안", "금융/Fintech", "커머스", 
            "게임", "모빌리티", "헬스케어", "에너지", "제조", "HR", 
            "마케팅", "영업", "경영지원", "컨설팅", "투자"
        ]
        
        system_prompt = f"""
You are the AI Talent Intelligence JD Analyzer v8.1.
Your task is to parse a Job Description into a highly structured JSON format for matching.

### [GATE 2: HIERARCHICAL MASTER SECTORS]
Identify ONE or MORE Main Sectors and their corresponding Sub Sectors.
- 영업 (Sales): 해외영업, B2B영업, 기술영업(Pre-sales), 영업지원, 영업기획.
- 마케팅 (Marketing): 퍼포먼스, 그로스, 브랜드, 콘텐츠(인플루언서 협업/제휴 포함), 언론홍보(PR), 마케팅기획.
- HR (Human Resources): 채용(TA), 평가보상(C&B), 급여(Payroll), 노무(ER), 인사기획, 교육(L&D).
- 총무 (General Affairs): 복리후생 운영, 자산관리(부동산, 법인자산, IT 비품 구매 및 관리).
- Finance (재무/회계): 재무회계, 자금, 세무, IR, M&A, 내부통제_감사, FP&A(경영분석), 회계사(CPA).
- STRATEGY (전략): 전략_경영기획, Business Operation(프로세스 효율화), 신사업 발굴 및 런칭.
- 디자인 (Design): UIUX, 브랜드, 제품, 웹, 디자인 기획 및 시스템 구축.
- 법무 (Legal): 일반법무, 컴플라이언스, 지적재산권(IP), 변호사.
- 물류/유통 (Logistics & SCM): 구매, SCM(수요예측/공급망), 유통망 관리, 물류기획 및 프로세스 최적화.
- MD (Commerce): 상품기획(Selection), 소싱MD(해외 직소싱/원가), 영업MD(채널 매출 관리).
- PRODUCT (제품 기획): IT 기업의 Product Owner(PO), Project Manager(PM), 서비스기획(화면설계), TPM.
- DATA (데이터): 데이터분석가, 데이터엔지니어, 데이터사이언티스트, DBA(DBMS 운영, 성능 최적화, 보안).
- SW (Software): BE(서버), FE(웹), DevOps_SRE, 인프라_Cloud, Mobile(iOS, Android).
- HW (Hardware): 회로설계(PCB), 기구설계, 로보틱스, 자동화(PLC), 임베디드, FAE_CE.
- 반도체 (Semiconductor): [도메인 우선] HW(SoC, RTL), SW(하단 드라이버), FW(컨트롤러), 공정(Yield/FAB).
- AI (Artificial Intelligence): 엔지니어(Serving/MLOps), 리서쳐(모델링), 기획(AI Governance, DT, AT, AX 전략 설계).
- 보안 (Security): 정보보안(인프라/인증), 개인정보보호(CPO, 규제 대응).
- 기타: 위 범주에 속하지 않는 특수 전문직.

### [HARD GATES]
1. **Sectors**: Identify Main Sectors and Sub Sectors from the list above.
2. **Seniority**: Identify minimum years and bucket (Junior: 0-4, Middle: 5-9, Senior: 10+).
3. **Functional Patterns**: Extract requirements as "Verb + Object" (Action-oriented). STRICTLY EXCLUDE soft skills.

### [INTELLIGENCE RULES]
- **Rule 2 (Reciprocal Dynamic Tagging)**: Extract niche technical requirements as 'context_tags' (e.g., "HBM3", "CXL").
- **Return JSON ONLY.**

### [INPUT JD]
{jd_text}

### [OUTPUT JSON SCHEMA]
{{
  "main_sectors": ["List of Main Sectors"],
  "sub_sectors": ["List of Sub Sectors"],
  "seniority": {{
    "min_years": 0,
    "bucket": "Junior|Middle|Senior"
  }},
  "functional_patterns": ["Pattern 1", "Pattern 2"],
  "context_tags": ["Tag 1", "Tag 2"],
  "hard_constraints": ["Must have 1", "Must have 2"]
}}
"""
        try:
            # We pass both system and user-merged prompt to get_chat_completion_json
            parsed_data = self.client.get_chat_completion_json(system_prompt)
            return parsed_data
        except Exception as e:
            print(f"❌ JD Analyzer v8 Error: {e}")
            return {}
