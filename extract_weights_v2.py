import math
import json
import os
from collections import defaultdict, Counter
from itertools import combinations

class AdaptiveWeightExtractor:
    def __init__(self, golden_set):
        self.golden_set = golden_set
        self.total_docs = len(golden_set)
        self.skill_counts = Counter()
        self.co_counts = Counter()
        self._build_counts()

    def _build_counts(self):
        for profile in self.golden_set:
            # skills 리스트가 dictionary 형태인 경우를 대비하여 처리
            raw_skills = profile.get("skills", [])
            if isinstance(raw_skills, list) and len(raw_skills) > 0 and isinstance(raw_skills[0], dict):
                skills = set([s["name"] for s in raw_skills])
            else:
                skills = set(raw_skills)

            # single count
            for s in skills:
                self.skill_counts[s] += 1

            # pair count
            for a, b in combinations(sorted(list(skills)), 2):
                key = (a, b)
                self.co_counts[key] += 1

    def compute_importance(self):
        importance = {}
        for skill, tf in self.skill_counts.items():
            df = tf
            # IDF: log(N / (1 + DF))
            idf = math.log(self.total_docs / (1 + df)) + 1
            importance[skill] = tf * idf
        return self._normalize(importance)

    def compute_pmi(self):
        pmi_scores = {}
        for (a, b), co in self.co_counts.items():
            p_a = self.skill_counts[a] / self.total_docs
            p_b = self.skill_counts[b] / self.total_docs
            p_ab = co / self.total_docs

            # PMI = log( P(A,B) / (P(A)P(B)) )
            pmi = math.log((p_ab + 1e-9) / (p_a * p_b + 1e-9))
            pmi_scores[f"{a}___{b}"] = pmi
        return self._normalize(pmi_scores)

    def compute_conditional(self):
        cond = defaultdict(dict)
        for (a, b), co in self.co_counts.items():
            cond[a][b] = co / self.skill_counts[a]
            cond[b][a] = co / self.skill_counts[b]
        return cond

    def _normalize(self, d):
        if not d: return d
        vals = list(d.values())
        min_v, max_v = min(vals), max(vals)
        if max_v - min_v == 0: return {k: 1.0 for k in d}
        return {k: (v - min_v) / (max_v - min_v) for k, v in d.items()}

    def run(self):
        return {
            "skill_importance": self.compute_importance(),
            "skill_pmi": self.compute_pmi(),
            "conditional_weight": self.compute_conditional()
        }

def load_golden_set():
    # v6 골든셋 로드 (32개 도메인 쿼리 포함)
    path = 'golden_dataset_v6.json'
    if not os.path.exists(path):
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 쿼리별 타겟 스킬들을 하나의 '프로필'처럼 간주하여 학습
    profiles = []
    for item in data:
        profiles.append({"skills": item.get("target_skills", [])})
    return profiles

if __name__ == "__main__":
    profiles = load_golden_set()
    print(f"Loaded {len(profiles)} profiles for weight extraction.")
    
    extractor = AdaptiveWeightExtractor(profiles)
    matrix = extractor.run()
    
    with open('position_weight_matrix_v2.json', 'w', encoding='utf-8') as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)
    
    print("Success: Bayesian Weight Matrix (v2) generated.")
