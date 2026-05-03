import json
with open('golden_dataset_v6.json', 'r', encoding='utf-8') as f:
    golden = json.load(f)
q3 = golden[3]
print(f"Query: {q3['query']}")
print(f"Relevant IDs: {q3['relevant_ids']}")
