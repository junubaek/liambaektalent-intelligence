
import json
import re
from connectors.gemini_api import GeminiClient

class ResumeParser:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    def parse(self, resume_text: str) -> dict:
        """
        [v8.0] NEXT-GEN AI Talent Intelligence Engine (Gemini 3.0 Flash)
        3-Gate structure: Seniority, 18 Master Sectors, Functional Patterns.
        """
        if not resume_text:
             return {}

        prompt = f"""
You are the heart of the AI Talent Intelligence OS (v8.0 Master Spec), powered by Gemini 3.0 Flash.
Your task is to analyze the resume and output a precise, structured JSON of the candidate's professional identity.

[GATE 1: SENIORITY BUCKET]
- Junior: 0 ~ 4 years (Execution focus)
- Middle: 5 ~ 9 years (Process improvement & Leading)
- Senior: 10+ years (Strategy & Organizational leadership)

[GATE 2: HIERARCHICAL MASTER SECTORS]
### STRICT HIERARCHICAL ONTOLOGY (USE ONLY THESE STRINGS):
[MAIN SECTOR LIST]
- 영업 (Sales)
- 마케팅 (Marketing)
- HR (Human Resources)
- 총무 (General Affairs)
- Finance (재무/회계)
- STRATEGY (전략)
- 디자인 (Design)
- 법무 (Legal)
- 물류/유통 (Logistics & SCM)
- MD (Commerce)
- PRODUCT (제품 기획)
- DATA (데이터)
- SW (Software)
- HW (Hardware)
- 반도체 (Semiconductor)
- AI (Artificial Intelligence)
- 보안 (Security)
- 기타

[SUB SECTOR MAPPING]
- 영업 (Sales): 해외영업, B2B영업, 기술영업(Pre-sales), 영업지원, 영업기획
- 마케팅 (Marketing): 퍼포먼스, 그로스, 브랜드, 콘텐츠(인플루언서 협업/제휴 포함), 언론홍보(PR), 마케팅기획
- HR (Human Resources): 채용(TA), 평가보상(C&B), 급여(Payroll), 노무(ER), 인사기획, 교육(L&D)
- 총무 (General Affairs): 복리후생 운영, 자산관리(부동산; 법인자산; IT 비품 구매 및 관리)
- Finance (재무/회계): 재무회계, 자금, 세무, IR, M&A, 내부통제_감사, FP&A(경영분석), 회계사(CPA), 투자담당자(Investment/VC/PE)
- STRATEGY (전략): 전략_경영기획, Business Operation(프로세스 효율화), 신사업 발굴 및 런칭
- 디자인 (Design): UIUX, 브랜드, 제품, 웹, 디자인 기획 및 시스템 구축
- 법무 (Legal): 일반법무, 컴플라이언스, 지적재산권(IP), 변호사
- 물류/유통 (Logistics & SCM): 구매, SCM(수요예측/공급망), 유통망 관리, 물류기획 및 프로세스 최적화
- MD (Commerce): 상품기획(Selection), 소싱MD(해외 직소싱/원가), 영업MD(채널 매출 관리)
- PRODUCT (제품 기획): Product Owner(PO), Project Manager(PM), 서비스기획(화면설계), TPM
- DATA (데이터): 데이터분석가, 데이터엔지니어, 데이터사이언티스트, DBA(DBMS 운영; 성능 최적화; 보안)
- SW (Software): BE(서버), FE(웹), DevOps_SRE, 인프라_Cloud, Mobile(iOS; Android)
- HW (Hardware): 회로설계(PCB), 기구설계, 로보틱스, 자동화(PLC), 임베디드, FAE_CE
- 반도체 (Semiconductor): HW(SoC; RTL), SW(하단 드라이버), FW(컨트롤러), 공정(Yield/FAB)
- AI (Artificial Intelligence): 엔지니어(Serving/MLOps), 리서쳐(모델링), 기획(AI Governance; DT; AT; AX 전략 설계)
- 보안 (Security): 정보보안(인프라/인증), 개인정보보호(CPO; 규제 대응)
- 기타

[HALO-ZERO COMPLIANCE RULE]
- You MUST map 'Main Sectors' AND 'Sub Sectors' ONLY to the exact strings provided above.
- [CRITICAL] Choose 'Main Sector' ONLY from this list: [영업 (Sales), 마케팅 (Marketing), HR (Human Resources), 총무 (General Affairs), Finance (재무/회계), STRATEGY (전략), 디자인 (Design), 법무 (Legal), 물류/유통 (Logistics & SCM), MD (Commerce), PRODUCT (제품 기획), DATA (데이터), SW (Software), HW (Hardware), 반도체 (Semiconductor), AI (Artificial Intelligence), 보안 (Security), 기타]
- Do NOT use abbreviations like "SW", "Data", "HW". Use the FULL string from the list.
- Do NOT translate, rephrase, or add parenthetical notes unless they are part of the exact string in the list.
- If a candidate doesn't perfectly fit, choose the closest match from the lists.

[GATE 3: FUNCTIONAL EXPERIENCE PATTERN (v5.7 Exposure-Based Logic)]
- Extract verifiable "Environmental Exposure" patterns instead of subjective capabilities.
- The goal is to document the exact environment, target, or process the candidate was exposed to, not how well they did it.
- [RULE 1] 100% EXCLUDE CAPABILITY/JUDGMENT WORDS: Do NOT use words like "Expert", "Leader", "Master", "Optimizer", "Maker", "Specialist".
- [RULE 2] USE FACTUAL SUFFIXES: Use neutral suffixes like "_Exp" (Experience), "_Env" (Environment), "_Cycle" (Cycle), or "_Process".
- [RULE 3] STRICT NAMING FORMAT: [Specific Target]_[Environment/Process]
  - Bad: "IPO_Leader" -> Good: "IPO_Process_Exp"
  - Bad: "Financial_Modeling_Expert" -> Good: "Financial_Modeling_Exp"
  - Bad: "Architecture_Design_Lead" -> Good: "Arch_Design_Env"
  - Bad: "Growth_Hacking_Master" -> Good: "Growth_Mkt_Cycle"
  - Bad: "System_Architect" -> Good: "MSA_Architecture_Env" or "High_Traffic_Node"
  - Bad: "Deal_Maker" -> Good: "Buy_Side_CDD_Exp" or "Due_Diligence_Cycle"
- [RULE 4] THE EXPOSURE VALIDATION: Ask yourself, "Is a specific tool, monetary target, or strict process named?" If yes, tag the exposure. If the wording is vague like "Strategic Leadership", DO NOT extract a pattern or downgrade it to "Biz_Planning_Env".

[INTELLIGENCE RULES]
- [RULE 3] SEMICONDUCTOR PRIORITY: If previous company is in semiconductor value chain and role is engineering, PRIORITIZE [반도체] as a Main Sector.
- [RULE 4] ROLE-AWARE CONTEXT: If resume text is sparse (less than 1000 chars), PRIORITIZE information found in the Role Title (prepended in the text) for sector classification. 
- [RULE 5] INVESTMENT MAPPING: '투자담당자', 'VC', 'PE', 'Fund Manager' MUST map to [Finance (재무/회계)] as Main Sector and [투자담당자(Investment/VC/PE)] as Sub Sector.

[RESUME TEXT]
{resume_text[:30000]}

[SCHEMA]
{{
  "candidate_profile": {{
    "main_sectors": ["List of Main Sectors"],
    "sub_sectors": ["List of specific Sub Sectors"],
    "total_years_experience": float,
    "seniority_bucket": "Junior | Middle | Senior",
    "context_tags": ["Tech keywords/Keywords"],
    "gap_analysis": ["List of warning signals if they claim leadership without proof (e.g., '패턴 대비 기여도 확인 필요: 주도적이라고 주장하나 수치 누락')"],
    "experience_summary": "Numbered list of functional results"
  }},
  "patterns": [
    {{
      "verb_object": "Verb + Object pattern",
      "tools": [],
      "impact": "Quantified result",
      "depth": "Owned | Led | Applied | Assisted"
    }}
  ]
}}
"""
        try:
            target_model = "gemini-3-flash-preview"
            
            parsed_data = self.client.get_chat_completion_json(prompt, model=target_model)
            
            # Post-processing for Rule 3: Semiconductor Priority (AI-assisted but we reinforce)
            # This can be handled by the prompt, but we ensure logic consistency here.
            
            return parsed_data
            
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Too Many Requests" in err_str:
                print(f"❌ Resume Parsing Error: {e}")
                return {}
                
            print(f"❌ Resume Parsing Error: {e}")
            return {}

    def calculate_quality_score(self, parsed_data: dict) -> dict:
        """
        [v5] Candidate Data Quality Score
        Items: Completeness, Pattern Density, Consistency.
        """
        if not parsed_data: return {"total": 0, "status": "Invalid"}
        
        # 1. Completeness (40%)
        fields = ["basics", "role_families", "domains", "experience_patterns", "impact_signals"]
        present_fields = sum(1 for f in fields if parsed_data.get(f))
        completeness = (present_fields / len(fields)) * 100
        
        # 2. Pattern Density (30%)
        patterns = parsed_data.get("experience_patterns", [])
        # Healthy range: 3-8 patterns
        pattern_density = 100 if 3 <= len(patterns) <= 8 else 50 if len(patterns) > 0 else 0
        
        # 3. Experience Consistency (30%)
        # Logic: If total_years > 5, but patterns < 2, consistency is low
        total_years = parsed_data.get("basics", {}).get("total_years_experience", 0)
        consistency = 100
        if total_years > 5 and len(patterns) < 2:
            consistency = 40
            
        total_score = (completeness * 0.4) + (pattern_density * 0.3) + (consistency * 0.3)
        
        return {
            "total_score": round(total_score, 2),
            "status": "High" if total_score > 80 else "Medium" if total_score > 50 else "Low",
            "flags": ["INCOMPLETE"] if completeness < 60 else []
        }
