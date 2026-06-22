content = open('incremental_ingest_v11.py', encoding='utf-8', errors='replace').read()
# neo4j 관련 함수 찾기
idx = content.find('def sync_neo4j')
if idx < 0:
    idx = content.find('neo4j')
print(content[max(0,idx-100):idx+800])
