import sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP
import re

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

replacements = {
    "F/W": "Firmware",
    "반도체/HW": "Semiconductor_Engineering",
    "재무자문/M&A": "Mergers_and_Acquisitions",
    "프로모션/BTL": "BTL_Marketing",
    "평가/보상": "Compensation_and_Benefits",
    "C/O 설계": "PCB_Design",
    "Encryption FDE/FBE": "Information_Security"
}

deletions = [
    "N/A",
    "Trim/Form",
    "GC-MS/MS",
    "LC-MS/MS",
    "ICP/MS"
]

def cleanup():
    with driver.session() as s:
        # Delete nodes
        for node_name in deletions:
            s.run("MATCH (s:Skill {name: $name}) DETACH DELETE s", name=node_name)
            
        print("Deletions complete.")
            
        # Replace nodes
        for old_name, new_name in replacements.items():
            # Get existing relationships
            rels = s.run("MATCH (c:Candidate)-[r]->(old:Skill {name: $old_name}) "
                         "RETURN c.id as cid, type(r) as rtype, properties(r) as props", 
                         old_name=old_name).data()
                         
            if not rels:
                # no edges found, just delete old if it exists
                s.run("MATCH (old:Skill {name: $old_name}) DETACH DELETE old", old_name=old_name)
                continue
                
            # Create/Merge new node
            s.run("MERGE (new:Skill {name: $new_name})", new_name=new_name)
            
            # Map relationships
            for record in rels:
                cid = record['cid']
                rtype = record['rtype']
                props = record['props']
                
                s.run(f"""
                MATCH (c:Candidate {{id: $cid}})
                MATCH (new:Skill {{name: $new_name}})
                MERGE (c)-[r:{rtype}]->(new)
                SET r += $props
                """, cid=cid, new_name=new_name, props=props)
                
            # Delete old node
            s.run("MATCH (old:Skill {name: $old_name}) DETACH DELETE old", old_name=old_name)
            
        print("Replacements complete.")
        
        # Add the mappings to ontology_graph.py to ensure the parser handles them in the future
        file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py'
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        map_string = ""
        for k, v in replacements.items():
            map_string += f'    "{k}": "{v}",\n'
            
        content = re.sub(r'CANONICAL_MAP\s*:\s*dict\[str,\s*str\]\s*=\s*\{', 'CANONICAL_MAP: dict[str, str] = {\n' + map_string, content)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("ontology_graph.py updated.")
        
        # Print total edge count
        cnt = s.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as cnt").single()['cnt']
        print(f"총 엣지 수: {cnt}개")

if __name__ == "__main__":
    cleanup()
    driver.close()
