import sys
import json
sys.path.append('.')

from app.graph_engine.core_graph import SkillGraphEngine
from app.engine.resume_snap import CandidateSnapper

graph = SkillGraphEngine()
snapper = CandidateSnapper(graph)

test_list = ['Project Manager(PM)', 'Product Owner(PO)', 'Financial System', '정산 시스템', '회계', '데이터 라인 구축', '시스템 설계', '시스템 기획', '재무회계']

extracted = snapper.extract_and_map_skills(test_list)
print("EXTRACTED:", json.dumps(extracted, indent=2, ensure_ascii=False))
