import math
from neo4j import GraphDatabase

class Neo4jCandidateSnapper:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_gravity_cypher(self, has_id_filter=False):
        """
        수리물리 모델을 완전한 Cypher 쿼리로 포팅.
        [입력파라미터]
        - $jd_tendency: {sales: float, tech: float, product: float, biz: float}
        - $jd_nodes: [{name: str, weight: float, is_core: bool}, ...]
        - $candidate_ids: list[str] (Optional)
        """
        # Cypher Query 로직 설계:
        # 1. Candidate 노드 순회 및 Tendency Alignment (Dot Product) 계산
        # 2. Hard Filter 적용 (tendency < 0.15 제외)
        # 3. 입력된 jd_nodes(가상 항성)들로부터 최대 2-hop 내에 있는 candidate의 Skill 탐색
        # 4. 거리(hops)에 따른 반비례 중력(Mass / (1+Distance)) 계산
        # 5. Core Intent, Hub Penalty 적용하여 최종 Score 합산 후 정렬
        
        query = f"""
        // 1. 후보자의 경향성 내적 (Dot Product) 및 0.15 Hard Filter
        MATCH (c:Candidate)
        {"WHERE c.id IN $candidate_ids" if has_id_filter else ""}
        
        WITH c,
             (coalesce(c.tendency_sales, 0) * $jd_t_sales + 
              coalesce(c.tendency_tech, 0) * $jd_t_tech + 
              coalesce(c.tendency_product, 0) * $jd_t_product + 
              coalesce(c.tendency_biz, 0) * $jd_t_biz) AS tendency_score
        {"WHERE tendency_score >= 0.15" if not has_id_filter else ""}

        // 2. 가상 항성(JD_Nodes) UNWIND
        UNWIND $jd_nodes AS jd_node
        
        // 3. 후보자의 스킬 중에서 JD 노드와 0~2 hop 이내에 있는 경로 탐색
        MATCH (c)-[hs:HAS_SKILL]->(cand_skill:Skill)
        MATCH p = shortestPath((s:Skill)-[:DEPENDS_ON|SIMILAR_TO*0..2]-(cand_skill)) // 무방향 2-hop
        WHERE s.name = jd_node.name
        
        // 4. 거리 및 질량 계산
        WITH c, tendency_score, jd_node, cand_skill, length(p) AS distance, hs.raw_weight AS c_weight
        
        // Hub Penalty (Degree가 너무 높으면 블랙홀 현상 방지)
        WITH c, tendency_score, jd_node, cand_skill, distance, c_weight,
             (cand_skill.mass * 10) / (cand_skill.degree + 12.0) AS safe_mass 
             
        // Core Intent Boosting
        WITH c, tendency_score, jd_node, cand_skill, distance, c_weight, safe_mass,
             CASE WHEN jd_node.is_core THEN 4.0 ELSE 1.0 END AS core_boost
             
        // 중력 = (질량 * 후보자기여도 * 부스트) / (1 + 거리)
        WITH c, tendency_score, jd_node,
             max((safe_mass * c_weight * jd_node.weight * core_boost) / (1.0 + distance)) AS max_gravity_for_this_jd_node
             
        // 5. 각 JD 노드별 최대 중력을 합산
        WITH c, tendency_score, sum(max_gravity_for_this_jd_node) AS raw_gravity
        
        // 최종 점수 = 중력 * 선호도
        WITH c, tendency_score, raw_gravity, (raw_gravity * tendency_score) AS final_score
        ORDER BY final_score DESC
        LIMIT 50
        
        RETURN c.name AS name, c.id AS id, c.sectors AS sectors, tendency_score, coalesce(raw_gravity, 0) AS raw_gravity, coalesce(final_score, 0) AS final_score
        """
        return query

    def search_candidates(self, jd_tendency, jd_nodes_list, candidate_ids=None):
        if candidate_ids is not None and len(candidate_ids) == 0:
            return []
            
        has_id_filter = candidate_ids is not None
        query = self.build_gravity_cypher(has_id_filter)
        
        jd_t_sales = jd_tendency.get("Sales", 0)
        jd_t_tech = jd_tendency.get("Tech", 0)
        jd_t_product = jd_tendency.get("Product", 0)
        jd_t_biz = jd_tendency.get("Business", 0)
        
        with self.driver.session() as session:
            result = session.run(query, 
                                 jd_t_sales=jd_t_sales, 
                                 jd_t_tech=jd_t_tech, 
                                 jd_t_product=jd_t_product, 
                                 jd_t_biz=jd_t_biz,
                                 jd_nodes=jd_nodes_list,
                                 candidate_ids=candidate_ids or [])
            return [record.data() for record in result]
