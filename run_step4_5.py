import sys
import json
from neo4j import GraphDatabase
import ontology_graph
import re

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

# 1. Update ontology_graph.py with new mappings
new_mappings = {
    "Infrastructure_and_Cloud": "DevOps",
    "Recruiting_and_Talent_Acquisition": "Talent_Acquisition",
    "Payment_and_Settlement_System": "Payment_System",
    "IPO_Preparation_and_Execution": "IPO",
    "Financial_Planning_and_Analysis": "FP_and_A",
    "Data_Science_and_Analysis": "Data_Analytics",
    "Global_Sales_and_Marketing": "Global_Sales",
    "Project_and_Portfolio_Management": "PMO",
    "Accounting_Process_and_System_Improvement": "Financial_Systems_Management",
    "Testing_and_Verification": "QA_Engineering",
    "RF_Verification_and_Test": "RF_Validation",
    "Chip_and_PKG_Design": "Advanced_Packaging",
    "Automation_Equipment_Design_and_Development": "Manufacturing_Automation",
    "Manufacturing_Equipment_Design_and_Development": "Manufacturing_Automation",
    "Security_Incident_Analysis_and_Reporting": "Information_Security",
    "Security_Monitoring_and_Operations": "Information_Security"
}

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

for k, v in new_mappings.items():
    if f'"{k}":' not in content and f"'{k}':" not in content:
        # Just inject it somewhere safe, like right before CANONICAL_MAP ends or just hardcode string substitution
        pass

# It's cleaner to just dynamically use the map inside this script for the Cypher migration,
# but we should definitely persist them to CANONICAL_MAP for future use.
map_string = ""
for k, v in new_mappings.items():
    map_string += f'    "{k}": "{v}",\n'

# Put at the beginning of CANONICAL_MAP
content = re.sub(r'CANONICAL_MAP\s*:\s*dict\[str,\s*str\]\s*=\s*\{', 'CANONICAL_MAP: dict[str, str] = {\n' + map_string, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run():
    lines = []
    with driver.session() as session:
        # Deletions
        deletions = [
            "Fan-In_and_-out_WLP_Technology",
            "WLAN_and_WCDMA_Schematic_Design",
            "WLAN_Schematic_and_PCB_Layout_Design",
            "Cellular_Phone_and_Dongle_Development",
            "HVAC_and_Boiler_System_Management",
            "Safety_and_Fire_Safety_Management",
            "Facility_Maintenance_and_Operations",
            "International_and_Domestic_Procurement",
            "Tester_Development_and_Manufacturing"
        ]
        
        for n in deletions:
            session.run("MATCH (s:Skill {name: $n}) DETACH DELETE s", n=n)
            
        lines.append("=== 삭제 대상 노드 DETACH DELETE 완료 ===")

        # Migrations
        migrated_nodes_count = 0
        for old_name, new_name in new_mappings.items():
            rels = session.run("MATCH (c:Candidate)-[r]->(old:Skill {name: $old_name}) RETURN c.id as cid, type(r) as rtype, properties(r) as props", old_name=old_name).data()
            if rels:
                session.run("MERGE (new:Skill {name: $new_name})", new_name=new_name)
                for record in rels:
                    cid = record['cid']
                    rtype = record['rtype']
                    props = record['props']
                    session.run(f"""
                    MATCH (c:Candidate {{id: $cid}})
                    MATCH (new:Skill {{name: $new_name}})
                    MERGE (c)-[r:{rtype}]->(new)
                    SET r += $props
                    """, cid=cid, new_name=new_name, props=props)
                # Delete old
                session.run("MATCH (old:Skill {name: $old_name}) DETACH DELETE old", old_name=old_name)
                migrated_nodes_count += 1
                
        lines.append(f"추가 복합 명사구 치환 완료: {migrated_nodes_count} 종")
        
        # Post-count
        total_edges = session.run("MATCH (c:Candidate)-[r]->(s:Skill) RETURN count(r) as cnt").single()['cnt']
        lines.append(f"치환 완료 후 총 엣지 수: {total_edges}")
        
        # Remaining complex nodes
        lines.append("\n=== 남은 복합 명사구 노드 (_and_ 또는 _or_) ===")
        remaining = session.run("""
        MATCH (s:Skill)
        WHERE s.name CONTAINS '_and_' OR s.name CONTAINS '_or_'
        RETURN s.name as name, count{(s)<-[]-()} as edge_cnt
        ORDER BY edge_cnt DESC
        """)
        for item in remaining:
            lines.append(f"[{item['edge_cnt']:4d} edges] {item['name']}")

        # ---------------------------------------------
        # STEP 5: Category apply
        # ---------------------------------------------
        lines.append("\n=== [Step 5] 카테고리 속성 부여 ===")
        import importlib
        importlib.reload(ontology_graph) # To get updated script if needed, but categories are already there
        
        updated_count = 0
        for category_name, skills in ontology_graph.SKILL_CATEGORIES.items():
            for skill_name in skills:
                res = session.run("MATCH (s:Skill {name: $skill}) SET s.category = $cat RETURN count(s) as c", skill=skill_name, cat=category_name)
                updated_count += res.single()['c']
        
        lines.append(f"총 {updated_count}개 Skill 노드들에 카테고리(category) 속성 부여 완료.")

    with open("step4_5_out.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    run()
