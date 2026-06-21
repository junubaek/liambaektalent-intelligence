import os
import json
import sys
import sqlite3
import re
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. Update ontology_graph.py
# ============================================================
print("Updating ontology_graph.py...")

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add to UNIFIED_GRAVITY_FIELD
if '"Network_on_Chip": 0.9' not in code:
    code = code.replace(
        '"NPU_Design": 1.0,',
        '"Network_on_Chip": 0.9,\n            "NPU_Design": 1.0,'
    )

if '"Chiplet_Architecture": 0.9' not in code:
    code = code.replace(
        '"SoC": 0.9,',
        '"Chiplet_Architecture": 0.9,\n            "SoC": 0.9,'
    )

# Add to CANONICAL_MAP update block at the end of the file
new_keywords_str = """
    # NoC / SoC Interconnect (한경환)
    'NoC': 'Network_on_Chip',
    'Network-on-Chip': 'Network_on_Chip',
    'Network on Chip': 'Network_on_Chip',
    'Arteris FlexNoC': 'Network_on_Chip',
    'NoC architecture': 'Network_on_Chip',
    'SoC interconnect': 'Network_on_Chip',
    'SoC fabric': 'Network_on_Chip',
    'SoC Architect': 'SoC',
    'SoC architecture': 'SoC',
    'Multi-die': 'Chiplet_Architecture',
    'Chiplet': 'Chiplet_Architecture',
    'chiplet-based': 'Chiplet_Architecture',

    # AiM / In-Memory (이형덕)
    'AiM': 'PIM_and_AI_Memory_Architecture',
    'AiMX': 'PIM_and_AI_Memory_Architecture',
    'in-memory computing': 'PIM_and_AI_Memory_Architecture',
    'In-Memory': 'PIM_and_AI_Memory_Architecture',
    'Processing-In-Memory': 'PIM_and_AI_Memory_Architecture',
    'processing in memory': 'PIM_and_AI_Memory_Architecture',

    # HPC / Parallel (박천혁)
    'RUST': 'Rust',
    'Rust programming': 'Rust',
    'OpenMP': 'High_Performance_Computing',
    'Multi-threading': 'High_Performance_Computing',
    'parallel computing': 'High_Performance_Computing',
    'Parallel computing': 'High_Performance_Computing',
    'CFD': 'High_Performance_Computing',
    'Lattice Boltzmann': 'High_Performance_Computing',
    'PTX ISA': 'CUDA',
    'NVCC': 'CUDA',
    'Multi-GPU': 'GPU_Acceleration',

    # Automotive Embedded (신기욱)
    'AUTOSAR': 'Automotive_Software',
    'CAN bus': 'Automotive_Software',
    'Vector CANalyzer': 'Automotive_Software',
    'CANoe': 'Automotive_Software',
    'HIL': 'Automotive_Software',
    'MISRA': 'Automotive_Compliance',
"""

# Insert right before the last '})' in the file
last_bracket_idx = code.rfind('})')
if last_bracket_idx != -1:
    code = code[:last_bracket_idx] + new_keywords_str + code[last_bracket_idx:]

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("ontology_graph.py updated successfully.")

# Import the updated MAP
from ontology_graph import CANONICAL_MAP

# ============================================================
# 2. Connect to Neo4j and create/verify new nodes
# ============================================================
with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

print("Syncing new ontology nodes to Neo4j...")
with driver.session() as session:
    session.run("MERGE (s:Skill {name: 'Network_on_Chip'})")
    session.run("MERGE (s:Skill {name: 'Chiplet_Architecture'})")
    print("New Skill nodes verified in Neo4j.")

# ============================================================
# Helper parse function
# ============================================================
def parse_resume_to_graph(text):
    text_lower = text.lower()
    matched_skills = set()
    for alias, canonical in CANONICAL_MAP.items():
        # Avoid short noise
        if len(alias) > 1 and alias.lower() in text_lower:
            matched_skills.add(canonical)
    
    # Format as returned structure
    nodes = [{'name': s} for s in sorted(list(matched_skills))]
    return {'nodes': nodes}

# ============================================================
# 3. Part 2: 한경환, 이형덕, 박천혁, 신기욱 재파싱 및 Neo4j 동기화
# ============================================================
print("\n=== Part 2: Re-parsing and Syncing Target Candidates ===")
targets = [
    ('1aaad2d3-348d-48f7-8501-38d7c1f7df03', '한경환'),
    ('31f22567-1b6f-81fd-ae6f-f34e3f501ca7', '이형덕'),
    ('3d322d13-0699-4453-b70e-5a4c2aac38f9', '박천혁'),
    ('ff33752e-5e9c-4b2d-9698-f4022f2a8a57', '신기욱'),
]

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

with driver.session() as session:
    for cid, name in targets:
        cur.execute('SELECT raw_text, current_company, email, phone, profile_summary, total_years, sector FROM candidates WHERE id=?', (cid,))
        row = cur.fetchone()
        if not row:
            print(f"[{name}] SQLite record not found")
            continue
        raw_text, company, email, phone, summary, years, sector = row
        
        result = parse_resume_to_graph(raw_text)
        nodes = result.get('nodes', [])
        print(f'[{name}] 재파싱 노드 {len(nodes)}개: {[n["name"] for n in nodes[:8]]}')
        
        # Sync to Neo4j
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name = $name, c.current_company = $company, c.email = $email,
                c.phone = $phone, c.profile_summary = $summary, c.total_years = $years, c.sector = $sector
        """, id=cid, name=name, company=company, email=email, phone=phone, summary=summary, years=years, sector=sector)
        
        # Clear old skill relationships
        session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=cid)
        
        # Add new skill relationships
        for node in nodes:
            skill_name = node['name']
            session.run("""
                MERGE (c:Candidate {id: $id})
                MERGE (s:Skill {name: $skill})
                MERGE (c)-[r:HAS_SKILL]->(s)
                SET r.source = 'patch_reparse', r.confidence = 1.0
            """, id=cid, skill=skill_name)

# ============================================================
# 4. Part 3: 김태경, 유정한 Neo4j 재동기화
# ============================================================
print("\n=== Part 3: Syncing Kim Tae-kyung and Yu Jeong-han to Neo4j ===")
sync_cids = [
    ('fbc27466-7587-45e6-b459-c2920b5d71fe', '김태경'),
    ('31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
]

with driver.session() as session:
    for cid, name in sync_cids:
        cur.execute('SELECT raw_text, current_company, email, phone, profile_summary, total_years, sector FROM candidates WHERE id=?', (cid,))
        row = cur.fetchone()
        if not row:
            print(f"[{name}] SQLite record not found")
            continue
        raw_text, company, email, phone, summary, years, sector = row
        
        result = parse_resume_to_graph(raw_text)
        nodes = result.get('nodes', [])
        
        # Sync Candidate Properties
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name = $name, c.current_company = $company, c.email = $email,
                c.phone = $phone, c.profile_summary = $summary, c.total_years = $years, c.sector = $sector
        """, id=cid, name=name, company=company, email=email, phone=phone, summary=summary, years=years, sector=sector)
        
        # Clear and Sync Skill Edges
        session.run("MATCH (c:Candidate {id: $id})-[r]->(s:Skill) DELETE r", id=cid)
        
        for node in nodes:
            skill_name = node['name']
            session.run("""
                MERGE (c:Candidate {id: $id})
                MERGE (s:Skill {name: $skill})
                MERGE (c)-[r:HAS_SKILL]->(s)
                SET r.source = 'sync_candidate', r.confidence = 1.0
            """, id=cid, skill=skill_name)
            
        print(f"{cid} ({name}): SUCCESS (Created Candidate & {len(nodes)} Skill Edges)")

conn.close()
driver.close()
