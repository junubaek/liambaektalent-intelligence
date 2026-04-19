import json
import time
import google.generativeai as genai

with open('secrets.json', 'r', encoding='utf-8') as f: secrets = json.load(f)
genai.configure(api_key=secrets.get('GEMINI_API_KEY', ''))

path = r'C:\Users\cazam\Downloads\02_resume 전처리\SK하이닉스_계측분석_한진희.pdf'
sample_file = genai.upload_file(path=path)

model = genai.GenerativeModel('gemini-1.5-flash', generation_config={'response_mime_type': 'application/json'})

prompt = '''아래 PDF 문서 내용에서 직무 경력을 상세히 추출하세요. 
신입이거나 지원서만 있고 실무 경력이 없다면 careers는 빈 배열입니다.
출력은 JSON 포맷으로 합니다.
{
  "careers": [
    { "company": "회사명(미상)", "title": "직급/직무", "start_date": "YYYY-MM", "end_date": "YYYY-MM" }
  ]
}'''

try:
    response = model.generate_content([prompt, sample_file])
    print(response.text)
finally:
    genai.delete_file(sample_file.name)
