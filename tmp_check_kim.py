import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_kim_rank():
    jd_text = "Python 백엔드 시스템 구축 경험자. MSA 아키텍처나 API Gateway 설계 경험 우대. DevOps나 컨테이너 운영 경험자도 환영."
    
    with open("candidates_cache_jd.json", "r", encoding="utf-8") as f:
        candidates = json.load(f)
        
    corpus = [jd_text]
    valid_cands = []
    
    for c in candidates:
        corpus.append(c['summary'])
        valid_cands.append(c)
        
    vectorizer = TfidfVectorizer(max_features=2000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    for i, c in enumerate(valid_cands):
        c['sim'] = float(sims[i])
        
    valid_cands.sort(key=lambda x: x['sim'], reverse=True)
    
    kim = [(i+1, c) for i, c in enumerate(valid_cands) if '김완희' in c['name']]
    
    found_in_top100 = False
    for i, c in enumerate(valid_cands[:100]):
        if '김완희' in c['name']:
            found_in_top100 = True
            
    if found_in_top100:
        print(f"✅ YES, 김완희 is in Top 100.")
    else:
        print(f"❌ NO, 김완희 is NOT in Top 100.")

    print(f"\n[TF-IDF 검색 결과 (전체 {len(valid_cands)}명 중)]")
    if kim:
        for k in kim:
            print(f"- 검색된 이름: {k[1]['name']}")
            print(f"- 현재 순위: {k[0]}위")
            print(f"- 유사성 점수(TF-IDF): {k[1]['sim']:.4f}")
    else:
        print("김완희가 candidates_cache_jd.json 에 존재하지 않습니다.")

if __name__ == "__main__":
    check_kim_rank()
