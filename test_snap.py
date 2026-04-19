import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.append(os.path.abspath('.'))
from ontology_graph import CANONICAL_MAP
from app.graph_engine.core_graph import SkillGraphEngine
from app.engine.resume_snap import CandidateSnapper

engine = SkillGraphEngine(use_v7=True)
snapper = CandidateSnapper(engine)
res = snapper.extract_and_map_skills(['DataAnalysis', 'ProductOwner'])

with open('test_res.txt', 'w', encoding='utf-8') as f:
    f.write(f'Mapping for DA: {engine.v7_mapping.get("DataAnalysis")}\n')
    f.write(f'Extraction: {res}\n')
