import requests
import json

url = "http://localhost:8000/api/search-v5"

payload = {
  "prompt": "데이터 분석가 백엔드 개발자 프론트엔드 리뷰",
  "sectors": [],
  "seniority": "All",
  "required": [
    "데이터 분석가", "DA", "백엔드", "BE", "서버", "프론트엔드", "FE", "풀스택", 
    "모바일", "iOS", "Android", "데브옵스", "인프라", "SRE", "데이터 엔지니어", 
    "데이터 사이언티스트", "마케터", "홍보", "기획", "PM", "PO", "프로덕트",
    "사업개발", "전략", "B2B", "영업", "세일즈", "TA", "리크루팅", "인사"
  ],
  "preferred": [],
  "strict_required": False
}

try:
    print("Testing backend search endpoint...")
    r = requests.post(url, json=payload, timeout=60)
    print("Status code:", r.status_code)
    data = r.json()
    if r.status_code == 200:
        total = data.get("total", 0)
        print("Success! Total results:", total)
        print("Alternatives (if any):", data.get("alternative"))
    else:
        print("Error content:", r.text)
except Exception as e:
    print("Error connecting to backend:", e)
