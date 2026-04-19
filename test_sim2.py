import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load candidates
with open("candidates_cache_jd.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

# 2. Build corpus
corpus = [c["summary"] for c in candidates]
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus)

# 3. Simulate expanded query
expanded_query = "IPO/펀딩 대비 자금 담당자 6년차 자금 Treasury Cash FX 환리스크 자금 Treasury Cash FX 환리스크 자금 Treasury Cash FX 환리스크 자금 Treasury Cash FX 환리스크 자금 Treasury Cash FX 환리스크"
query_vec = vectorizer.transform([expanded_query.lower()])

# 4. Calculate similarities
sims = cosine_similarity(query_vec, tfidf_matrix).flatten()

# 5. Find 김대중 and 이범기
for idx, c in enumerate(candidates):
    if "이범기" in c["name"] or "김대중" in c["name"]:
        print(f"Target: {c['name']}")
        print(f"Index: {idx}, TF-IDF Score: {sims[idx]}")
        print(f"Summary: {c['summary']}")
        
# 6. Check top 300 threshold
top_indices = sims.argsort()[-300:][::-1]
threshold_score = sims[top_indices[-1]]
print(f"Threshold score for top 300: {threshold_score}")
