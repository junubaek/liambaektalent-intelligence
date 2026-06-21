import json

with open("golden_dataset_v8.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    q = item.get('query')
    if q == 'Technical Program Manager':
        print("TPM Query found!")
        print("Relevant IDs in golden:", item.get('relevant_ids'))
        print("Relevant Names in golden:", item.get('relevant_names'))
