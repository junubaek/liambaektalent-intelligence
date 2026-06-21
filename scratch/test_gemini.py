import json
import google.generativeai as genai

secrets = json.load(open('secrets.json', encoding='utf-8'))
genai.configure(api_key=secrets['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.5-flash')

# 테스트 1: Meta
resp = model.generate_content("""
회사명: Meta Inc
포지션: Technical Program Manager
재직기간: 2020년 ~ 2024년

JSON만 반환:
{
  "tier": "S/A/B/C",
  "timing_score": 0.0~1.0,
  "domain_relevance": 0.0~1.0,
  "company_summary": "20자 이내",
  "confidence": 0.0~1.0
}
""")
print('Meta 응답:', resp.text)

# 테스트 2: 리벨리온 (2021년)
resp2 = model.generate_content("""
회사명: 리벨리온
포지션: NPU 커널 엔지니어
재직기간: 2021년 ~ 2023년

JSON만 반환:
{
  "tier": "S/A/B/C",
  "timing_score": 0.0~1.0,
  "domain_relevance": 0.0~1.0,
  "company_summary": "20자 이내",
  "confidence": 0.0~1.0
}
""")
print('리벨리온 응답:', resp2.text)
