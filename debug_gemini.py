import os
import json
import pdfplumber
import google.generativeai as genai

GEMINI_API_KEY = "INSERT_YOUR_NEW_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

filepath = r"C:\Users\cazam\Downloads\02_resume 전처리\[우아한형제들] 김정수(Data Scientist)부문_프로젝트.pdf"

with pdfplumber.open(filepath) as pdf:
    text = "\n".join(p.extract_text() or "" for p in pdf.pages)

print(f"Extracted Text Length: {len(text)}")

prompt = f'''
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출해줘.
반드시 아래 JSON 형식으로만 응답해. 다른 텍스트 없이.

형식:
[
  {{"action": "BUILT", "skill": "Payment_and_Settlement_System"}},
  {{"action": "DESIGNED", "skill": "Data_Pipeline_Construction"}}
]

action은 다음 중 하나만 사용:
- BUILT: 직접 구축/개발/만든 경우
- DESIGNED: 설계/기획한 경우  
- MANAGED: 관리/운영한 경우
- ANALYZED: 분석한 경우
- SUPPORTED: 보조/지원한 경우

skill은 아래 목록 중에서만 선택:
Payment_and_Settlement_System, Service_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
재무회계, 전략_경영기획, 사업개발_BD, 퍼포먼스마케팅,
채용_리크루팅, 조직개발_OD, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, 인프라_Cloud, 보안_Security, FinTech,
자연어처리_NLP, 컴퓨터비전_CV, 추천시스템, Deep_Learning

이력서:
{text[:3000]}
'''

response = model.generate_content(prompt)
print("GEMINI Response:")
print(response.text)
