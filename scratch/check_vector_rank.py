import json
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

from jd_compiler import _get_secret
from connectors.openai_api import OpenAIClient
from connectors.pinecone_api import PineconeClient

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

o_api = OpenAIClient(_get_secret('OPENAI_API_KEY'))
p_host = _get_secret('PINECONE_HOST')
if not p_host.startswith('https'):
    p_host = f'https://{p_host}'
p_api = PineconeClient(_get_secret('PINECONE_API_KEY'), p_host)

query = 'Enterprise Sales Manager'
target_id = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'

print(f"Direct Vector Search for: '{query}'")
q_vec = o_api.embed_content(query)
res = p_api.query(q_vec, top_k=1000)

found = False
if res and 'matches' in res:
    for i, match in enumerate(res['matches']):
        if match['id'] == target_id:
            print(f"Target found at Vector Rank {i+1} with score {match['score']}")
            found = True
            break
else:
    print(f"Pinecone Query failed or returned no matches: {res}")

if not found:
    print("Target NOT FOUND in Vector Top 1000.")
