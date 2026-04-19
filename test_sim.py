import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

with open("candidates_cache_jd.json", "r", encoding="utf-8") as f:
    candidates = json.load(f)

jd_text = "IPO/펀딩 대비 자금 담당자 6년차"
boost_str = " 자금 Treasury Cash FX 환리스크" * 5
expanded_jd = jd_text + boost_str

corpus = [expanded_jd]
for c in candidates:
    corpus.append(c['summary'])

vectorizer = TfidfVectorizer(max_features=10000)
tfidf_matrix = vectorizer.fit_transform(corpus)
sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

for i, c in enumerate(candidates):
    c['sim'] = float(sims[i])

candidates.sort(key=lambda x: x['sim'], reverse=True)

rank = 1
for c in candidates:
    name = c['name']
    if '김대중' in name or '이범기' in name:
        print(f"Rank {rank}: {name} | Sim: {c['sim']} | Summary: {c['summary'][:100]}")
    rank += 1
