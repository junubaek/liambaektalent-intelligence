import os
import re
import yaml

class ObsidianParser:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        # YAML Frontmatter 매칭 정규식
        self.frontmatter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.MULTILINE | re.DOTALL)
        self.wikilink_pattern = re.compile(r'\[\[(.*?)\]\]')
        self.canonical_map = self._load_canonical_map()

    def _load_canonical_map(self):
        map_path = os.path.join(self.vault_path, "Meta", "canonical_map.yaml")
        if os.path.exists(map_path):
            with open(map_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}

    def _extract_links(self, text):
        return self.wikilink_pattern.findall(text)

    def parse_all_nodes(self):
        """
        Vault 내의 모든 마크다운 파일을 파싱하여 Node 딕셔너리 리스트 반환
        """
        nodes = []
        for root, _, files in os.walk(self.vault_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    node_data = self.parse_file(filepath)
                    if node_data:
                        nodes.append(node_data)
        return nodes

    def parse_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None

        # 파일명에서 확장자 제외한 것을 기본 Node ID/Name 으로 사용
        basename = os.path.basename(filepath)
        node_name = os.path.splitext(basename)[0]
        # 안전하게 치환했던 것을 원래 이름으로 복구 (예: _ -> /)
        # 완벽한 복구는 어려우나 MVP 용으로는 유지
        node_name = node_name.replace('_', '/') if '_' in node_name and '전략' not in node_name else node_name
        
        # 앞서 스크립트로 생성할 때 / 를 _ 로 바꿨으므로 하드코딩된 예외 처리
        if node_name == "물류_유통 (Logistics & SCM)": node_name = "물류/유통 (Logistics & SCM)"
        if node_name == "전략_경영기획": node_name = "전략_경영기획" # 예외
        if node_name == "Finance (재무_회계)": node_name = "Finance (재무/회계)"
        if node_name == "앱개발(Android_iOS)": node_name = "앱개발(Android/iOS)"

        node_data = {
            "id": node_name,
            "aliases": [],
            "category": "Unknown",
            "depends_on": [],
            "related_to": [],
            "part_of": [],
            "used_in": [],
            "similar_to": []
        }

        # Frontmatter 파싱
        match = self.frontmatter_pattern.search(content)
        if match:
            yaml_content = match.group(1)
            try:
                metadata = yaml.safe_load(yaml_content)
                if metadata:
                    # Aliases 처리 및 Canonical 맵과 합병
                    file_aliases = metadata.get("aliases", [])
                    node_data["aliases"] = file_aliases if isinstance(file_aliases, list) else []
                    
                    # 도메인 정보 저장
                    node_data["category"] = metadata.get("domain", "Unknown")
                    
                    # 5대 관계 타입 추출 함수
                    def extract_rel(field):
                        raw_list = metadata.get(field, [])
                        extracted = []
                        if isinstance(raw_list, list):
                            for item in raw_list:
                                links = self._extract_links(item)
                                # 파싱된 링크 이름(기술명)을 canonical map에 통과시켜 정규화
                                for l in links:
                                    canonical_name = self.canonical_map.get(l, l)
                                    extracted.append(canonical_name)
                        return extracted

                    node_data["depends_on"] = extract_rel("depends_on")
                    node_data["related_to"] = extract_rel("related_to")
                    node_data["part_of"] = extract_rel("part_of")
                    node_data["used_in"] = extract_rel("used_in")
                    node_data["similar_to"] = extract_rel("similar_to")
                    
            except yaml.YAMLError as exc:
                print(f"YAML Parse Error in {filepath}: {exc}")

        return node_data
