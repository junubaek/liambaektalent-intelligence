import re

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\dynamic_parser_v2.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_rule = """[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
한 스킬에 여러 행동이 보이면 복수 동사 Multi-Edge 모두 생성해라."""

new_rule = """[고유명사 원형 보존 원칙]
프레임워크, 라이브러리, 툴, 플랫폼 이름(Kubernetes, Terraform, vLLM, PyTorch, LangGraph, CUDA, RDMA 등)은 절대 상위 개념(IaC, LLM_Engineering 등)으로 요약하거나 치환하지 마라.
이력서에 적힌 영문 원형 그대로 독립된 노드로 추출해라. 맵에 없는 단어라도 영문 고유명사면 원형 그대로.
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
On_Device_Compile"""

content = content.replace(old_rule, new_rule)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dynamic_parser_v2.py with new rules.")
