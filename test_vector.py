import os
import json
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_vector_score():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT name_kr as name, raw_text FROM candidates")
    candidates = [dict(r) for r in c.fetchall()]
    conn.close()

    # Query 1: vLLM -> 홍기재
    query1 = "vLLM"
    corpus1 = [query1] + [c.get('raw_text', '') or '' for c in candidates]
    vec1 = TfidfVectorizer(max_features=10000)
    matrix1 = vec1.fit_transform(corpus1)
    sims1 = cosine_similarity(matrix1[0:1], matrix1[1:]).flatten()
    
    hong_score = 0.0
    for i, cand in enumerate(candidates):
        if cand['name'] == '홍기재':
            hong_score = sims1[i]
            break
            
    # Query 2: Terraform -> 오원교
    query2 = "Terraform"
    corpus2 = [query2] + [c.get('raw_text', '') or '' for c in candidates]
    vec2 = TfidfVectorizer(max_features=10000)
    matrix2 = vec2.fit_transform(corpus2)
    sims2 = cosine_similarity(matrix2[0:1], matrix2[1:]).flatten()
    
    oh_score = 0.0
    for i, cand in enumerate(candidates):
        if cand['name'] == '오원교':
            oh_score = sims2[i]
            break

    print(f"vLLM Query - 홍기재 vector_score: {hong_score}")
    print(f"Terraform Query - 오원교 vector_score: {oh_score}")

if __name__ == '__main__':
    check_vector_score()
