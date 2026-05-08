import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

correct_summary = '22년간 삼성SDS·베스핀글로벌·ByteDance에서 엔터프라이즈 클라우드·AI 인프라 영업을 총괄하며 7,900억원 누적 매출을 달성한 Enterprise Sales 전문가. 삼성전자 HPC 데이터센터 5,250억 메가딜 수주, AI-based GPU 인프라 GTM, LLM 솔루션 한국 시장 개척 등 대형 딜 전 주기 오너십 보유.'

cur.execute('UPDATE candidates SET profile_summary = ?, is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE name_kr = "최우성" AND is_duplicate = 0', (correct_summary,))
conn.commit()
conn.close()
print('Choi Woo-sung summary updated and flags reset.')
