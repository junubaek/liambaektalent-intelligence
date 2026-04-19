import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
try:
    idx = pc.Index('talent-index-v3')
    stats = idx.describe_index_stats()
    with open('check_pinecone_out.txt', 'w', encoding='utf-8') as out:
        out.write(f"Pinecone vector count for talent-index-v3: {stats.total_vector_count}\n")
except Exception as e:
    with open('check_pinecone_out.txt', 'w', encoding='utf-8') as out:
        out.write(f"Error checking pinecone: {e}\n")
