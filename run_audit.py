import sqlite3
import json

db_path = 'C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

query = """
SELECT 
  COUNT(*) as total_count,
  SUM(CASE WHEN name_kr IS NULL OR name_kr = '' THEN 1 ELSE 0 END) as no_name,
  SUM(CASE WHEN length(name_kr) > 5 THEN 1 ELSE 0 END) as polluted_name,
  SUM(CASE WHEN name_kr LIKE '%확인%' THEN 1 ELSE 0 END) as needs_check_name,
  SUM(CASE WHEN phone IS NULL OR phone = '' THEN 1 ELSE 0 END) as no_phone,
  SUM(CASE WHEN email IS NULL OR email = '' THEN 1 ELSE 0 END) as no_email,
  SUM(CASE WHEN raw_text IS NULL OR raw_text = '' THEN 1 ELSE 0 END) as no_raw,
  SUM(CASE WHEN length(raw_text) < 200 THEN 1 ELSE 0 END) as poor_raw,
  SUM(CASE WHEN p.parsed_json IS NULL OR json_extract(p.parsed_json, '$.profile_summary') IS NULL OR json_extract(p.parsed_json, '$.profile_summary') = '' THEN 1 ELSE 0 END) as no_summary
FROM candidates c
LEFT JOIN parsing_cache p ON c.id = p.candidate_id
"""
cursor.execute(query)
res = cursor.fetchone()

print(f'=== 기본 품질 감사 결과 ===')
print(f'전체: {res["total_count"]}')
print(f'이름없음: {res["no_name"]}')
print(f'이름오염의심 (>5자): {res["polluted_name"]}')
print(f'확인요됨 이름: {res["needs_check_name"]}')
print(f'전화없음: {res["no_phone"]}')
print(f'이메일없음: {res["no_email"]}')
print(f'본문없음: {res["no_raw"]}')
print(f'본문빈약 (<200자): {res["poor_raw"]}')
print(f'요약없음: {res["no_summary"]}')
