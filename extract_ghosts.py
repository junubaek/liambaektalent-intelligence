import sqlite3
import pandas as pd
conn = sqlite3.connect(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()
c.execute("SELECT name_kr, phone, email, SUBSTR(CAST(raw_text AS TEXT), 1, 60) FROM candidates WHERE careers_json IS NULL OR careers_json = '[]' OR careers_json = ''")
rows = c.fetchall()

md_content = '# 완전 껍데기(Real Ghosts) 최종 명단\n\n'
md_content = '> 완화된 스캔(Phase 1. Deep Extraction V2)으로도 경력을 찾지 못해 포기된 진짜 껍데기 및 완전 순수 신입 포트폴리오 명단(' + str(len(rows)) + '명)입니다.\n\n'
md_content += '| 이름 | 연락처 | 이메일 | 원문 텍스트 (60자 사전보기) |\n'
md_content += '|---|---|---|---|\n'
for r in rows:
    name = r[0] or '미상'
    phone = str(r[1]) if r[1] else ''
    email = str(r[2]) if r[2] else ''
    desc = str(r[3]).strip().replace('\n', ' ').replace('\r', ' ')[:60]
    md_content += f'| {name} | {phone} | {email} | {desc} |\n'

with open(r'C:\Users\cazam\.gemini\antigravity\brain\8612324f-88ef-41c4-8cef-bcaebea80e5d\artifacts\real_ghosts_list.md', 'w', encoding='utf-8') as f:
    f.write(md_content)
