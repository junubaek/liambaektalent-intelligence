import json
from connectors.pinecone_api import PineconeClient

s = json.load(open('secrets.json'))
pc_host = s['PINECONE_HOST']
if not pc_host.startswith('https://'):
    pc_host = 'https://' + pc_host
pc = PineconeClient(s['PINECONE_API_KEY'], pc_host)

try:
    pc.delete_all(namespace='resume_vectors')
    print('Pinecone 초기화 완료')
except Exception as e:
    print('Pinecone 오류:', e)
