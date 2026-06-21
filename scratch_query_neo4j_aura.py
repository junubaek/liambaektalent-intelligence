import sys
sys.stdout.reconfigure(encoding='utf-8')

# Import the configured Neo4j driver from backend or app
# Let's see where the driver is defined. In backend/main.py or similar?
# Let's inspect jd_compiler's neo4j session since it successfully queried it.
import jd_compiler

# Let's see if we can run a custom query through jd_compiler's session helper or if it has a driver.
# Let's print the attributes of jd_compiler to see if it has a neo4j driver or session maker.
print("jd_compiler attributes:")
print([x for x in dir(jd_compiler) if 'neo' in x.lower() or 'driver' in x.lower() or 'session' in x.lower()])

# Let's run a query using the same neo4j driver that jd_compiler uses!
# Usually jd_compiler imports driver or session from backend or maintains its own.
# Let's check how jd_compiler connects to Neo4j.
try:
    from backend.main import get_neo4j_driver
    driver = get_neo4j_driver()
    print("Successfully imported driver from backend.main")
except Exception as e:
    print(f"Could not import driver from backend.main: {e}")
    # Let's try importing from app or other files
    try:
        from app.engine.neo4j_snapper import get_driver
        driver = get_driver()
        print("Successfully imported driver from app")
    except Exception as e2:
        print(f"Could not import driver from app: {e2}")
        driver = None

if driver:
    node_query = """
    MATCH (c:Candidate) WHERE c.name_kr IN ['오원교', '이상헌', '이영도'] OR c.name CONTAINS 'Wongyo'
    RETURN c.id, c.name_kr, c.name, c.current_company
    """
    
    edge_query = """
    MATCH (c:Candidate)-[r]->(s:Skill)
    WHERE c.name_kr IN ['오원교', '이상헌', '이영도']
    RETURN c.name_kr as name_kr, type(r) as rel, s.name as skill
    """
    
    try:
        with driver.session() as session:
            # Nodes
            print("\n--- Neo4j Nodes (Aura) ---")
            res = session.run(node_query)
            for r in res:
                print(f"  ID: {r['c.id']} | name_kr: {r['c.name_kr']} | name: {r['c.name']} | 회사: {r['c.current_company']}")
                
            # Edges
            print("\n--- Neo4j Edges (Aura) ---")
            res = session.run(edge_query)
            for r in res:
                print(f"  [{r['name_kr']}] {r['rel']} -> {r['skill']}")
    except Exception as e:
        print(f"Error querying Aura: {e}")
    finally:
        driver.close()
