import networkx as nx

class SkillGraphEngine:
    def __init__(self, use_v7=False):
        # 방향성 그래프(Directed Graph) 초기화
        # A depends_on B 라면 에지의 방향은 A -> B (A는 B를 필요로 함)
        self.graph = nx.DiGraph()
        self.use_v7 = use_v7
        
        if self.use_v7:
            import sys
            import os
            # Ensure the root dir is in path
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
            from ontology_graph import build_graph as build_v7, CANONICAL_MAP
            self.graph = build_v7()
            self.canonical_map = CANONICAL_MAP
            self.v7_mapping = {}
            for k, v in self.canonical_map.items():
                self.v7_mapping[str(k)] = v
            for n in self.graph.nodes:
                self.v7_mapping[n] = n
            print(f"✅ V7 Graph Engine Loaded Natively: {self.graph.number_of_nodes()} Nodes")

    def build_graph(self, parsed_nodes):
        """
        ObsidianParser에서 추출한 노드 리스트를 바탕으로 NetworkX 그래프를 구축
        """
        if getattr(self, 'use_v7', False):
            return
        # 1. 먼저 모든 노드를 추가
        for node in parsed_nodes:
            self.graph.add_node(
                node["id"],
                aliases=node["aliases"],
                category=node["category"]
            )
            
        # 2. 엣지 연결 (관계 설정)
        for node in parsed_nodes:
            node_id = node["id"]
            
            # 헬퍼 함수: 존재하지 않는 노드 자동 생성 및 엣지 추가
            def add_edge_safe(u, v, rel, w, bidirectional=False):
                if not self.graph.has_node(v):
                    self.graph.add_node(v, aliases=[], category="Unknown")
                dist_penalty = 1.0 / w
                self.graph.add_edge(u, v, relation=rel, weight=w, distance_penalty=dist_penalty)
                if bidirectional:
                    self.graph.add_edge(v, u, relation=rel, weight=w, distance_penalty=dist_penalty)

            # 5대 관계 가중치 적용
            # depends_on (강한 단방향 종속성) Weight 2.0
            for target in node.get("depends_on", []):
                add_edge_safe(node_id, target, "depends_on", 2.0)
                
            # part_of (상위 개념 포함) Weight 1.5
            for target in node.get("part_of", []):
                add_edge_safe(node_id, target, "part_of", 1.5)
                
            # used_in (응용 분야) Weight 1.5
            for target in node.get("used_in", []):
                add_edge_safe(node_id, target, "used_in", 1.5)
                
            # related_to (측면 연결, 연관성) 양방향 Weight 1.0
            for target in node.get("related_to", []):
                add_edge_safe(node_id, target, "related_to", 1.0, bidirectional=True)
                
            # similar_to (의미적 유사성) 양방향 Weight 1.0
            for target in node.get("similar_to", []):
                add_edge_safe(node_id, target, "similar_to", 1.0, bidirectional=True)
                
        import math
        # 3. 노드 질량(Mass) 계산 (Degree Centrality 기반)
        centrality = nx.degree_centrality(self.graph)
        n_nodes = self.graph.number_of_nodes()
        log_mass = {}
        for node, cent in centrality.items():
            raw_degree = cent * (n_nodes - 1)
            # Log scaling: math.log(1 + raw_degree)
            log_mass[node] = math.log(1 + raw_degree)
            
        nx.set_node_attributes(self.graph, log_mass, 'mass')
        
        print(f"✅ Graph Engine Loaded: {self.graph.number_of_nodes()} Nodes, {self.graph.number_of_edges()} Edges")

    def get_adjacent_skills(self, skill_id, max_distance=2):
        """
        특정 스킬(항성) 주변의 궤도 스킬(인접 노드)들을 검색
        """
        if not self.graph.has_node(skill_id):
            return {}

        # NetworkX의 single_source_dijkstra_path_length를 사용해 거리 계산
        # 거리가 가까울수록 중력이 셈 (관계 가중치 역수 기준)
        lengths = nx.single_source_dijkstra_path_length(self.graph, skill_id, cutoff=max_distance, weight='distance_penalty')
        
        # 자기 자신을 제외하고 리턴 (node: {"distance": dist, "mass": mass})
        result = {}
        for node, dist in lengths.items():
            if node != skill_id:
                # mass attributes are already logged
                mass = self.graph.nodes[node].get('mass', 0.1)
                safe_mass = max(mass, 0.1)
                result[node] = {"distance": dist, "mass": safe_mass}
                
        return result
        
    def get_all_nodes_with_aliases(self):
        """모든 노드와 Alias를 딕셔너리 형태로 반환 (매핑 엔진용)"""
        mapping = {}
        # 더 긴 키워드(Alias)가 우선적으로 매칭될 수 있도록 하기 위해 외부에서 정렬할 기반 제공
        for node, data in self.graph.nodes(data=True):
            mapping[node] = node
            for alias in data.get("aliases", []):
                mapping[alias] = node
                
        # Canonical Map (yaml)에 정의된 추가 Alias(동의어)들을 맵핑에 통합
        if hasattr(self, 'canonical_map') and self.canonical_map:
            for alias, canonical in self.canonical_map.items():
                if self.graph.has_node(canonical):
                    mapping[str(alias)] = canonical
                    
        return mapping
        
    def get_node_mass(self, node_id):
        mass = self.graph.nodes[node_id].get('mass', 0.1)
        return max(mass, 0.1)
        
    def get_node_degree(self, node_id):
        if not self.graph.has_node(node_id):
            return 0
        return self.graph.degree(node_id)

