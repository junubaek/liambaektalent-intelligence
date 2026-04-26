from jd_compiler import api_search_v9

def check_depth():
    query = "Neural Network Operations Parallel Programming C++"
    print(f"Query: {query}")
    res = api_search_v9(query)
    
    print("\nTop 10 Results with Depth Scores:")
    for c in res['matched'][:10]:
        print(f"Name: {c['name_kr']}")
        print(f"  - Depth Score: {c['depth_score']:.4f}")
        print(f"  - Final Score: {c['final_score']:.4f}")
        print(f"  - V/G/B: {c['v_score']:.2f}/{c['g_score']:.2f}/{c['bm_score']:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    check_depth()
