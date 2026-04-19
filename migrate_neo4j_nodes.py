from neo4j import GraphDatabase

MIGRATION_MAP = {
    "기술영업_PreSales": "Technical_Sales",
    "물류_Logistics": "Logistics_and_Supply_Chain",
    "조직개발_OD": "Organizational_Development",
    "투자_M&A": "Mergers_and_Acquisitions",
    "언론홍보_PR": "Public_Relations",
    "채용_리크루팅": "Talent_Acquisition",
    "그로스마케팅": "Growth_Marketing",
    "퍼포먼스마케팅": "Performance_Marketing",
    "브랜드마케팅": "Brand_Management",
    "콘텐츠마케팅": "Content_Marketing",
    "보안_Security": "Information_Security",
    "정보보안": "Information_Security",
    "법무_Legal": "Legal_Practice",
    "세무_Tax": "Tax_Accounting",
    "재무회계": "Financial_Accounting",
    "특허_IP": "Patent_Management",
    "사업개발_BD": "Business_Development"
}

def migrate_nodes():
    driver = GraphDatabase.driver("neo4j://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    with driver.session() as session:
        for old_name, new_name in MIGRATION_MAP.items():
            print(f"Migrating {old_name} -> {new_name}...")
            
            # 1. Fetch all outgoing relationships from Candidate to old_name
            result = session.run(
                "MATCH (c:Candidate)-[r]->(old:Skill {name: $old_name}) RETURN c.id AS cid, type(r) AS r_type",
                old_name=old_name
            )
            edges = [(record["cid"], record["r_type"]) for record in result]
            
            # 2. Re-create edges to new_name
            for cid, r_type in edges:
                session.run(
                    f"MATCH (c:Candidate {{id: $cid}}) "
                    f"MERGE (new:Skill {{name: $new_name}}) "
                    f"MERGE (c)-[:{r_type}]->(new)",
                    cid=cid, new_name=new_name
                )
            
            # 3. Delete old node
            session.run(
                "MATCH (old:Skill {name: $old_name}) DETACH DELETE old",
                old_name=old_name
            )
            
            print(f"  Moved {len(edges)} edges and deleted '{old_name}' node.")
            
    driver.close()

if __name__ == "__main__":
    migrate_nodes()
