import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 김영민 후보자 데이터 업데이트
# ID: 8a8f2be2-8a1a-4acc-8a59-e006f3907697
candidate_id = '8a8f2be2-8a1a-4acc-8a59-e006f3907697'
summary = '코인원(Coinone)의 CTO로서 클라우드 아키텍처 설계와 운영, 쿠버네티스(EKS) 최적화 및 배포 자동화를 총괄하는 전문가입니다. DevOps 엔지니어로 시작해 플랫폼 테크 리더를 거쳐 CTO로 선임되었으며, 인프라, 데이터, DBA, QA, 제품 전략 등 기술 조직 전반을 리드하고 있습니다. CI/CD, DevSecOps 구축 및 AWS 환경의 대규모 트래픽 처리에 깊은 전문성을 보유하고 있습니다.'
company = '코인원'
position = 'CTO'
sector = 'DevOps/Infrastructure'
total_years = 9.0

cur.execute('''
    UPDATE candidates 
    SET current_company = ?, 
        program_position = ?,
        sector = ?,
        profile_summary = ?,
        total_years = ?,
        is_neo4j_synced = 0,
        is_pinecone_synced = 0
    WHERE id = ?
''', (company, position, sector, summary, total_years, candidate_id))

conn.commit()
conn.close()
print(f'Candidate {candidate_id} (Kim Young-min) updated successfully.')
