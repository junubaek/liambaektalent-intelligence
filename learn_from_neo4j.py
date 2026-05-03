from neo4j import GraphDatabase
import os
import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from dotenv import load_dotenv

# .env 로드 (Neo4j 접속 정보)
load_dotenv()

class Neo4jSkillLearner:
    def __init__(self):
        self.uri = "neo4j+ssc://72de4959.databases.neo4j.io"
        self.user = "72de4959"
        self.password = "oicDGhFqhTz-5NhnnW0uGEKOIrSUs0GZBdKtzRhyvns"
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def fetch_all_candidate_skills(self):
        query = """
        MATCH (c:Candidate)-[:HAS_SKILL|USED_AS_MAIN|DEVELOPED|MANAGED]->(s)
        WHERE NOT s:Candidate
        RETURN c.name as name, collect(s.name) as skills
        """
        profiles = []
        with self.driver.session() as session:
            result = session.run(query)
            for record in result:
                profiles.append({
                    "name": record["name"],
                    "skills": list(set(record["skills"])) # 중복 제거
                })
        return profiles

class AdaptiveWeightExtractor:
    def __init__(self, profiles):
        self.profiles = profiles
        self.total_docs = len(profiles)
        self.skill_counts = Counter()
        self.co_counts = Counter()
        self._build_counts()

    def _build_counts(self):
        for p in self.profiles:
            skills = p["skills"]
            for s in skills:
                self.skill_counts[s] += 1
            for a, b in combinations(sorted(skills), 2):
                self.co_counts[(a, b)] += 1

    def run(self):
        importance = {}
        for skill, tf in self.skill_counts.items():
            idf = math.log(self.total_docs / (1 + tf)) + 1
            importance[skill] = tf * idf
        
        pmi_scores = {}
        for (a, b), co in self.co_counts.items():
            p_a = self.skill_counts[a] / self.total_docs
            p_b = self.skill_counts[b] / self.total_docs
            p_ab = co / self.total_docs
            pmi = math.log((p_ab + 1e-9) / (p_a * p_b + 1e-9))
            pmi_scores[f"{a}___{b}"] = pmi

        cond = defaultdict(dict)
        for (a, b), co in self.co_counts.items():
            cond[a][b] = co / self.skill_counts[a]
            cond[b][a] = co / self.skill_counts[b]

        return {
            "skill_importance": self._normalize(importance),
            "skill_pmi": self._normalize(pmi_scores),
            "conditional_weight": cond,
            "total_samples": self.total_docs
        }

    def _normalize(self, d):
        if not d: return d
        vals = list(d.values())
        min_v, max_v = min(vals), max(vals)
        if max_v - min_v == 0: return {k: 1.0 for k in d}
        return {k: (v - min_v) / (max_v - min_v) for k, v in d.items()}

if __name__ == "__main__":
    learner = Neo4jSkillLearner()
    try:
        print("Fetching candidate profiles from Neo4j...")
        profiles = learner.fetch_all_candidate_skills()
        print(f"Loaded {len(profiles)} profiles.")
        
        extractor = AdaptiveWeightExtractor(profiles)
        matrix = extractor.run()
        
        with open('global_skill_likelihood.json', 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2, ensure_ascii=False)
        print("Success: Global Skill Likelihood Matrix generated.")
    finally:
        learner.close()
