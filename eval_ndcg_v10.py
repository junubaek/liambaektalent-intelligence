import json, math, time
from jd_compiler import api_search_v9

def dcg(rel):
    return sum(r / math.log2(i + 2) for i, r in enumerate(rel))

def ndcg_at_k(retrieved_ids, relevant_ids, k=10):
    s = set(relevant_ids)
    gains = [1 if x in s else 0 for x in retrieved_ids[:k]]
    ideal = [1] * min(len(relevant_ids), k)
    idcg = dcg(ideal)
    return dcg(gains) / idcg if idcg > 0 else 0.0

with open('golden_dataset_v10.json', encoding='utf-8') as f:
    dataset = json.load(f)

scores = []
print(f"{'ID':<5} {'Query':<45} {'NDCG@10'}")
print('-' * 60)
for q in dataset['queries']:
    qid, text, rel_ids = q['query_id'], q['query'], q['relevant_ids']
    try:
        results = api_search_v9(text, f"eval_{qid}")
        ret_ids = [r.get('id','') for r in results.get('matched', [])]
        score = ndcg_at_k(ret_ids, rel_ids)
    except Exception as e:
        score = 0.0
        print(f"  ERROR {qid}: {e}")
    scores.append(score)
    print(f"{qid:<5} {text[:44]:<45} {score:.4f}")
    time.sleep(0.2)

print('-' * 60)
print(f"Mean NDCG@10: {sum(scores) / len(scores):.4f}  ({len(scores)} queries)")
