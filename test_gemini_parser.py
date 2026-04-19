import json
from resume_parser import ResumeParser
from connectors.gemini_api import GeminiClient

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

client = GeminiClient(secrets["GEMINI_API_KEY"])
parser = ResumeParser(client)

mock_resume = """
저는 그로스 마케팅 마스터입니다. 
IPO 과정 전체를 총괄하고 리드하는 압도적 리더십을 발휘했습니다. 
또한 MSA 아키텍처 설계를 주도하며 최고 수준의 성과를 냈습니다.
그러나 이에 대한 구체적인 매출 수치나 시스템 스케일, 팀 규모에 대한 언급은 이력서에 없습니다.
오직 저의 열정과 아키텍처 전문가로서의 주도성만을 강조합니다.
"""

print("Running v5.7 Expression-Based Parser...\n")
res = parser.parse(mock_resume)

print(json.dumps(res, indent=2, ensure_ascii=False))
