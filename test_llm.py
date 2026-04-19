import sqlite3
import json
import google.generativeai as genai

with open('secrets.json', 'r') as f: secrets = json.load(f)
genai.configure(api_key=secrets.get('GEMINI_API_KEY', ''))
model = genai.GenerativeModel('gemini-2.5-flash-lite', generation_config={'response_mime_type': 'application/json'})

prompt = '''당신은 전문 헤드헌터 파서입니다. 이력서를 분석해 명확한 팩트를 JSON으로 추출하되, 가장 중요한 규칙이 있습니다:
1. 연도(Date)나 기간이 명시되어 있지 않아도 직무(Role), 한 일(Responsibilities), 소속(Company)이 유추되면 최대한 careers 배열에 포함시키세요.
2. 영문 이력서일 경우 영문 그대로 또는 한글로 번역하여 careers 에 담으세요.
3. 지원자의 대표 포지션(직함 또는 직무 단위, 예: 프론트엔드 개발자, 언론홍보 담당자)을 명확하게 한 구절로 추출하여 'representative_position' 에 담아주세요. 포지션을 전혀 유추할 수 없는 신입의 경우 '신입'이라고 적어주세요.
4. 신입이거나 실무 경력(인턴 포함)이 완전히 없다면 careers는 빈 배열로 두세요.

[JSON 출력 포맷]
{
  "representative_position": "문자열",
  "careers": [
    { "company": "회사명(없으면 미상)", "title": "직급/직무", "start_date": "YYYY-MM 또는 미상", "end_date": "미상/현재" }
  ]
}

[이력서 원문]
1. 언론/미디어 관계 구축 및 기업 이슈를 관리했습니다.
2. 보도자료 및 기획기사 컨텐츠를 개발하고 작성했습니다.
3. 브랜드PR 및 CSR 활동을 기획하고 실행했습니다.
현 직 장: 린나이코리아㈜
직    급: 책임(대리급)
'''

print(model.generate_content(prompt).text)
