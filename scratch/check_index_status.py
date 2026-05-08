import json
import sys
import os
from neo4j import GraphDatabase

# Ensure project root is in path
sys.path.insert(0, os.getcwd())
from jd_compiler import _get_secret

n_uri = _get_secret('NEO4J_URI')
n_user = _get_secret('NEO4J_USERNAME')
n_pw = _get_secret('NEO4J_PASSWORD')
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

with driver.session() as session:
    res = session.run('SHOW INDEXES YIELD name, type, state, populationPercent WHERE name = "candidate_embedding"').data()
    print(json.dumps(res, indent=2))

driver.close()
