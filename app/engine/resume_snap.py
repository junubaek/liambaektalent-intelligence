import math
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CandidateSnapper:
    def __init__(self, graph_engine):
        self.graph_engine = graph_engine
        self.node_mapping = self.graph_engine.get_all_nodes_with_aliases()
        
        # Talent Physics Hyperparameters
        self.alpha = 0.7       # Structure Mass (Degree)
        self.beta = 1.2        # Info Mass (IDF)
        self.decay_rate = 0.15 # Time Decay 반감계수
        self.k1 = 1.5          # BM25 Term Frequency Saturation
        self.b = 0.75          # BM25 Length Normalization Penalty

    def calculate_normalized_strength(self, tf, L, L_avg):
        """
        BM25 Document Length Normalization
        스킬이 여러 번 등장하되(TF), 비정상적으로 긴 이력서(L > L_avg)라면 페널티를 주어 밀도를 평가합니다.
        """
        if L_avg <= 0: return tf
        return (tf * (self.k1 + 1)) / (tf + self.k1 * (1.0 - self.b + self.b * (L / L_avg)))

    def apply_time_decay(self, base_strength, cand_name, skill):
        # Deterministic mock years_ago for tie-breaking simulation (0 to 5 years)
        hash_val = int(hashlib.md5(f"{cand_name}_{skill}".encode()).hexdigest(), 16)
        years_ago = float(hash_val % 6)
        return base_strength * math.exp(-self.decay_rate * years_ago)
        
    def calculate_node_mass(self, degree, df, N):
        # Hub Node Hard Capping (전략, 기획 등 문어발식 연결 노드 페널티)
        hub_penalty = 1.0
        if degree > 12: # 12개 이상 연결된 스킬은 범용 스킬로 간주하여 질량을 강제 억제
            hub_penalty = 12.0 / degree # e.g., degree 30 -> 0.4x penalty
            
        structure_mass = math.pow(math.log1p(degree), self.alpha) * hub_penalty
        info_mass = math.pow(math.log1p(N / (df + 1.0)), self.beta)
        return structure_mass * info_mass

    def extract_and_map_skills(self, raw_text_or_list):
        """
        텍스트에서 키워드를 추출해 Graph Node ID와 빈도수(가중치) 딕셔너리로 반환
        """
        matched_nodes = {}
        
        if isinstance(raw_text_or_list, list):
            raw_text = " ".join(str(x) for x in raw_text_or_list)
        elif isinstance(raw_text_or_list, dict):
            # dict 가중치 직접 주입 형태 처리 (Core Intents 용)
            return raw_text_or_list
        else:
            raw_text = str(raw_text_or_list)

        raw_text_lower = raw_text.lower()
        
        sorted_keys = sorted(list(self.node_mapping.keys()), key=len, reverse=True)
        
        for kword in sorted_keys:
            node_id = self.node_mapping[kword]
            kword_lower = str(kword).lower()
            count = raw_text_lower.count(kword_lower)
            
            if count > 0:
                matched_nodes[node_id] = matched_nodes.get(node_id, 0.0) + float(count)
                raw_text_lower = raw_text_lower.replace(kword_lower, " " * len(kword_lower))
                
        return matched_nodes

    def check_domain_match(self, jd_domain, main_sectors):
        if not jd_domain: return 1.0
        if not main_sectors: return 0.5  # 정보 없음 중립 패널티
        
        sectors_str = " ".join(main_sectors).lower()
        jd_d = jd_domain.lower()
        
        # Soft Domain Friction Matrix (도메인 간 마찰 계수)
        if "semiconductor" in jd_d or "반도체" in jd_d:
            if any(k in sectors_str for k in ["semiconductor", "반도체", "장비", "hardware"]):
                return 0.9 # 저항 거의 없음 (유관)
            elif any(k in sectors_str for k in ["software", "소프트웨어", "it", "saas", "tech"]):
                return 0.7 # 약간의 저항 (동일 Tech군 내 타 분야)
            else:
                return 0.2 # 강한 저항 (패션, 리테일 등 완전 비유관 산업)
                
        elif "commerce" in jd_d or "커머스" in jd_d:
            if any(k in sectors_str for k in ["commerce", "커머스", "platform", "플랫폼", "retail", "유통", "fashion", "패션"]):
                return 0.9
            elif any(k in sectors_str for k in ["software", "it", "tech", "content", "콘텐츠", "f&b"]):
                return 0.6
            else:
                return 0.2
                
        elif "it" in jd_d or "tech" in jd_d or "ai" in jd_d or "data" in jd_d:
            if any(k in sectors_str for k in ["it", "software", "소프트웨어", "ai", "data", "cloud", "tech", "platform"]):
                return 0.9
            elif any(k in sectors_str for k in ["commerce", "hardware", "fintech", "game"]):
                return 0.7
            else:
                return 0.3
                
        return 0.5 # Default Friction

    def get_tendency_vector(self, cand_nodes):
        """
        후보자가 보유한 전체 스킬(노드)의 빈도/가중치를 기반으로
        4대 경향성(Center of Mass) 비율을 도출 (합계 1.0)
        """
        categories = {
            "Sales": ["영업", "sales", "b2b", "해외", "md", "마케팅", "퍼포먼스", "그로스", "브랜드", "crm", "콘텐츠", "홍보", "pr"],
            "Tech": ["tech", "software", "소프트웨어", "sw", "인프라", "cloud", "devops", "sre", "be", "fe", "mobile", "ios", "android", "data", "데이터", "ai", "machinelearning", "mlops", "엔지니어", "모델링", "dba", "반도체", "hw", "하드웨어", "설계", "연구", "r&d", "임베디드", "펌웨어", "fw", "공정", "plc", "자동화"],
            "Product": ["product", "기획(화면설계", "uiux", "ui", "ux", "po", "pm", "서비스", "제품"],
            "Business": ["전략", "경영", "strategy", "hr", "재무", "finance", "회계", "m&a", "투자", "물류", "scm", "유통", "컴플라이언스", "법무", "operation", "사업", "운영"]
        }
        
        scores = {"Sales": 0.0, "Tech": 0.0, "Product": 0.0, "Business": 0.0}
        
        for cand_node, weight in cand_nodes.items():
            name_lower = cand_node.lower()
            matched_cat = False
            for cat, kws in categories.items():
                if any(kw in name_lower for kw in kws):
                    scores[cat] += weight
                    matched_cat = True
                    break
            if not matched_cat:
                # 못 찾은 스킬은 Business나 Tech 등에 적절히 분산하거나 무시 가능
                # 여기서는 무시하여 명확한 성향이 지배하도록 함
                pass
                
        total = sum(scores.values())
        if total > 0:
            for cat in scores:
                scores[cat] = scores[cat] / total
        else:
            # 경향성을 판별할 수 없는 경우 가장 중립적인 균등분배
            scores = {"Sales": 0.25, "Tech": 0.25, "Product": 0.25, "Business": 0.25}
            
        return scores

    def calculate_tendency_alignment(self, jd_tendency, cand_tendency):
        """
        JD의 요구 경향성과 이력서의 경향성 간의 내적(Dot Product)을 통해 마찰력/보정 계수 산출 (0.1 ~ 1.0)
        """
        if not jd_tendency:
            return 1.0 # JD 경향성이 주어지지 않은 경우 패널티 없음
            
        # Strategy 키워드를 Business 로 매핑 보정
        jd_t = {}
        for k, v in jd_tendency.items():
            key = "Business" if k == "Strategy" else k
            jd_t[key] = v
            
        dot_product = sum(jd_t.get(cat, 0.0) * cand_tendency.get(cat, 0.0) for cat in ["Sales", "Tech", "Product", "Business"])
        
        # 0이 되면 점수가 완전히 날아가므로, Soft Friction의 철학에 맞게 최소 하한선 0.1 부여
        return max(0.1, dot_product)

    def calculate_gravity(self, jd_nodes, candidate_nodes, cand_name, df_map, N, L, L_avg, core_intents_mapped):
        """
        JD 가상항성과 이력서 벡터 간의 중력 계산 (BM25 Density, Time Decay 및 Intent Weighting 분리)
        """
        score = 0.0
        contributing_nodes = {}
        
        def get_intent_multiplier(node_id):
            return core_intents_mapped.get(node_id, 1.0)
            
        # 1. Direct Match (직접 일치)
        direct_matches = set(jd_nodes.keys()).intersection(set(candidate_nodes.keys()))
        for match in direct_matches:
            degree = self.graph_engine.get_node_degree(match)
            df = df_map.get(match, 0)
            mass = self.calculate_node_mass(degree, df, N)
            
            raw_cand_weight = self.calculate_normalized_strength(candidate_nodes[match], L, L_avg)
            cand_weight = self.apply_time_decay(raw_cand_weight, cand_name, match)
            
            jd_weight = math.log1p(jd_nodes[match])
            intent_boost = get_intent_multiplier(match)
            
            add_score = (mass * cand_weight * jd_weight * 50.0) * intent_boost
            score += add_score
            if add_score > 0:
                contributing_nodes[match] = contributing_nodes.get(match, 0.0) + add_score
        
        # 2. Orbit Match (궤도 일치)
        for jd_node, jd_raw_weight in jd_nodes.items():
            jd_weight = math.log1p(jd_raw_weight)
            jd_degree = self.graph_engine.get_node_degree(jd_node)
            jd_df = df_map.get(jd_node, 0)
            jd_mass = self.calculate_node_mass(jd_degree, jd_df, N)
            
            adjacent_info = self.graph_engine.get_adjacent_skills(jd_node, max_distance=2)
            
            for cand_node, cand_raw_weight in candidate_nodes.items():
                if cand_node in adjacent_info:
                    info = adjacent_info[cand_node]
                    distance = info["distance"]
                    
                    cand_degree = self.graph_engine.get_node_degree(cand_node)
                    cand_df = df_map.get(cand_node, 0)
                    cand_mass = self.calculate_node_mass(cand_degree, cand_df, N)
                    
                    raw_cand_weight = self.calculate_normalized_strength(cand_raw_weight, L, L_avg)
                    cand_weight = self.apply_time_decay(raw_cand_weight, cand_name, cand_node)
                    
                    intent_boost = get_intent_multiplier(jd_node)
                    
                    # 가상 항성(Virtual Node) 중력 공식: (M1 * M2 * v) / distance
                    gravity = ((jd_mass * cand_mass * cand_weight * jd_weight * 20.0) / distance) * intent_boost
                    score += gravity
                    if gravity > 0:
                        contributing_nodes[cand_node] = contributing_nodes.get(cand_node, 0.0) + gravity

        return score, contributing_nodes

    def rank_candidates_for_jd(self, jd_text, candidates_data, opts=None):
        """
        물리학(Physics v2)과 기하학(Geometry v3)을 모두 엮어내는 최종 계산 엔진
        Final Score = Gravity * Semantic * Domain * Intent
        """
        opts = opts or {}
        jd_domain = opts.get("jd_domain")
        core_intents_raw = opts.get("core_intents", {})
        jd_tendency = opts.get("jd_tendency", {})
        
        # Node Mapping
        jd_nodes = self.extract_and_map_skills(jd_text)
        core_intents_mapped = self.extract_and_map_skills(core_intents_raw)
        
        # 자동 JD 경향성 추출 (수동 룰 매핑 방지)
        jd_tendency_auto = self.get_tendency_vector(jd_nodes)
        
        print(f"\n🎯 [JD 매핑 항성]: {jd_nodes}")
        print(f"🧭 [자동 JD 경향성]: {jd_tendency_auto}")
        if core_intents_mapped:
            print(f"🔥 [Intent 부스팅]: {core_intents_mapped}")
            
        # 1. 후보자 파싱 및 DF(Document Frequency) 및 L(문서 길이) 계산
        N = len(candidates_data)
        df_map = {}
        processed_candidates = []
        total_length = 0.0
        
        corpus = [jd_text] # 인덱스 0은 JD query 
        
        for idx, cand in enumerate(candidates_data):
            cand_name = cand.get("name", "Unknown")
            cand_skills_raw = cand.get("raw_skills", [])
            cand_nodes = self.extract_and_map_skills(cand_skills_raw)
            
            cand_length = sum(cand_nodes.values())
            total_length += cand_length
            
            # Tendency Profiling (카테고리 비율 계산)
            cand_tendency = self.get_tendency_vector(cand_nodes)
            
            # Geometric Embedding 용 텍스트 (Experience Summary + 태그들)
            exp_sum = cand.get("experience_summary", "")
            geo_text = f"{exp_sum} {' '.join(cand_skills_raw)}"
            corpus.append(geo_text)
            
            processed_candidates.append({
                "idx": idx + 1,
                "name": cand_name,
                "raw_skills": cand_skills_raw,
                "cand_nodes": cand_nodes,
                "L": cand_length,
                "main_sectors": cand.get("main_sectors", []),
                "cand_tendency": cand_tendency
            })
            
            for node_id in set(cand_nodes.keys()):
                df_map[node_id] = df_map.get(node_id, 0) + 1
        
        L_avg = total_length / N if N > 0 else 1.0
        
        # 2. Geometric Embedding (TF-IDF Cosine Similarity) 계산
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        # 0번 인덱스는 JD, 나머지는 Candidates
        cosine_sim_array = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

        # 3. 4-Factor 결합 매칭
        results = []
        for p_cand in processed_candidates:
            if not p_cand["cand_nodes"]:
                continue

            gravity_score, contributing_nodes = self.calculate_gravity(
                jd_nodes, p_cand["cand_nodes"], p_cand["name"], df_map, N, p_cand["L"], L_avg, core_intents_mapped
            )
            
            if gravity_score > 0:
                # Geometric Alignment (SBERT/TF-IDF)
                sem_sim = cosine_sim_array[p_cand["idx"] - 1]
                semantic_factor = max(0.2, sem_sim * 2.5) # 최소 하한선 및 배율 조정
                
                # Domain Constraint
                domain_factor = self.check_domain_match(jd_domain, p_cand["main_sectors"])
                
                # Tendency Alignment (Dot Product of Category Mass)
                tendency_factor = self.calculate_tendency_alignment(jd_tendency_auto, p_cand["cand_tendency"])
                
                # Hard Filter: 방향성이 완전히 어긋난 경우 (0.15 미만) 아예 제거
                if tendency_factor < 0.15:
                    continue
                
                # Final Score = Gravity * Semantic * Domain * Tendency
                final_score = gravity_score * semantic_factor * domain_factor * tendency_factor
                
                # Report 무결성을 위해 개별 항성 가중치에도 기하학적 페널티 반영
                geom_multiplier = semantic_factor * domain_factor * tendency_factor
                scaled_contributing = {k: round(v * geom_multiplier, 2) for k, v in contributing_nodes.items()}
                
                sorted_contributing = {k: v for k, v in sorted(scaled_contributing.items(), key=lambda item: item[1], reverse=True)}
                results.append({
                    "name": p_cand["name"],
                    "score": round(final_score, 2),
                    "matched_nodes": sorted_contributing, 
                    "raw_skills": p_cand["raw_skills"],
                    "geo_details": f"Gravity({gravity_score:.0f}) * Sem({semantic_factor:.2f}) * Dom({domain_factor:.1f}) * Ten({tendency_factor:.2f})"
                })
                
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
