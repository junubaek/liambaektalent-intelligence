import json
from connectors.pinecone_api import PineconeClient

s = json.load(open('secrets.json'))
pc = PineconeClient(s['PINECONE_API_KEY'], s['PINECONE_HOST'])

# Upsert a single test vector (1536 dimensions)
vector = [0.1] * 1536
pc.upsert([{'id': 'test_001', 'values': vector, 'metadata': {'test': True}}], namespace='resume_vectors')
print('Pinecone OK')
