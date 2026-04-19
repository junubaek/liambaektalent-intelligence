import re

with open('dynamic_parser_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_system_instruction = '''SYSTEM_INSTRUCTION = """
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출합니다.
각 후보자별로 결과를 추출할 때, `candidate_name` 필드는 파싱용으로 제공된 [후보자명: OOO] 형태의 헤더에서 OOO 부분을 절대 변경하지 말고 100% 동일한 글자로 복사해야 합니다. (이름이 불일치하면 시스템 에러가 발생하여 저장되지 않습니다.)

- action: 반드시 한정된 9개 동사 Enum 내에서만 선택하세요.
  * BUILT: 직접 코드 작성 또는 시스템/인프라 구축
  * DESIGNED: 아키텍처, 정책, UX, BM 등 기획/설계
  * MANAGED: 기존 시스템, 조직, 프로세스 운영/관리
  * ANALYZED: 데이터 추출/분석하여 인사이트 도출
  * LAUNCHED: 프로덕트/서비스를 책임지고 시장에 출시
  * NEGOTIATED: 외부와 협상/영업하거나 계약 체결
  * GREW: 매출, 트래픽, 유저 수 등 지표를 수치적으로 성장
  * SUPPORTED: 주도적 역할 아님, 협업/일부 지원
  * USED: 특정 도구나 인프라를 기반(기반 환경)으로 사용함

[1우선순위: 고유명사 원형 보존 원칙 (최우선 최우선!)]
프레임워크, 라이브러리, 툴, 플랫폼 이름(OpenStack, Terraform, Kubernetes, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념으로 요약하지 말고, 이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 
목록(2순위)에 없는 단어라도 영문 고유명사면 아래 수식어 패턴을 포함해 무조건 원형 그대로 추출할 것.
- built on X → (후보자) USED X
- using X → (후보자) USED X  
- based on X → (후보자) USED X
- powered by X → (후보자) USED X
- leveraged X → (후보자) BUILT X
예시:
'MySQL service built on in-house OpenStack'
→ (후보자) -[:USED]-> (OpenStack)

[2순위: 그 외 일반 스킬은 아래 목록 기준으로 정규화]
(단, 위 1순위에 해당하는 영문 고유명사는 이 2순위 목록 제한을 무시하고 추출할 것)
Payment_and_Settlement_System, Product_Service_Planning, Business_Model_Planning, Platform_Operations_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning,
Corporate_Legal_Counsel, Intellectual_Property, Legal_Compliance, Contract_Management, Litigation

한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라.
스킬 노드는 검색 가능한 기술 명사여야 한다.
다음은 스킬 노드로 추출하면 안 됨:
- 숫자+단위 조합 (예: 32bit/64bit Architecture)
- 특수문자 포함 수치 표현 (예: L2/L3 Network)
- 회사명, 프로젝트명, 서비스명
- 단순 형용사/부사 (예: High Performance)

올바른 예시:
RTOS, FPGA, Linux_Kernel, NPU, 
vLLM, Kubernetes, Terraform, RDMA,
Memory_Profiling, Board_Bringup, 
On_Device_Compile

[문장 분석 Few-Shot 예시]
1. "신규 결제 서비스를 시장에 출시했습니다" -> action: "LAUNCHED", skill: "Payment_and_Settlement_System"
2. "주요 파트너사와 물류 제휴 계약을 협상했습니다" -> action: "NEGOTIATED", skill: "물류_Logistics"
3. "추천시스템 모델을 고도화하여 MAU를 6개월 만에 3배 성장시켰습니다" -> action: "GREW", skill: "추천시스템"
4. "앱 화면 UX와 어드민 시스템을 전담하여 설계했습니다" -> action: "DESIGNED", skill: "Product_Service_Planning"
"""'''

pattern = r'SYSTEM_INSTRUCTION = """(.*?)"""'
replaced_text = re.sub(pattern, new_system_instruction[21:-3], text, flags=re.DOTALL)

with open('dynamic_parser_v2.py', 'w', encoding='utf-8') as f:
    f.write(replaced_text)

print("SYSTEM_INSTRUCTION replaced successfully.")
