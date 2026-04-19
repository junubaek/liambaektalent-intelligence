import json

class AdjacencyEngine:
    """
    v6.3.6 Discovery Governance Engine
    Calculates the 'Adjacency Score' between a discovered pattern and the core ontology clusters.
    Ensures governance by preventing 'Tag Sprawl'.
    """

    def __init__(self, cluster_config):
        self.clusters = cluster_config # Expected to be the CLUSTERS dict from PatternMerger

    def calculate_adjacency(self, new_pattern, target_cluster):
        """
        Returns a score from 0.0 to 1.0.
        > 0.85: Immediate Merge Recommended.
        > 0.60: High Adjacency (Related).
        < 0.40: Low Adjacency (Potentially unique).
        """
        new_pattern = (new_pattern or "").lower().strip().replace("_", " ")
        cluster_aliases = [p.lower().replace("_", " ") for p in self.clusters.get(target_cluster, [])]
        
        # 1. Direct Alias overlap
        if new_pattern in cluster_aliases:
            return 1.0
        
        # 2. Token Overlap
        new_tokens = set(new_pattern.split())
        max_overlap = 0
        for alias in cluster_aliases:
            alias_tokens = set(alias.split())
            if not alias_tokens: continue
            
            overlap = len(new_tokens.intersection(alias_tokens)) / len(new_tokens.union(alias_tokens))
            if overlap > max_overlap:
                max_overlap = overlap
        
        return round(max_overlap, 2)

    def find_best_fit(self, new_pattern):
        """Finds the cluster with highest adjacency."""
        best_cluster = None
        highest_score = 0.0
        
        for cluster in self.clusters:
            score = self.calculate_adjacency(new_pattern, cluster)
            if score > highest_score:
                highest_score = score
                best_cluster = cluster
        
        return best_cluster, highest_score

    def audit_governance(self, candidate_patterns):
        """
        Audits a list of patterns and flags those with high adjacency to existing clusters 
        that aren't yet merged.
        """
        audit_results = []
        for p in candidate_patterns:
            best, score = self.find_best_fit(p)
            if score > 0.85:
                audit_results.append({
                    "pattern": p,
                    "action": "MERGE",
                    "target": best,
                    "score": score,
                    "reason": "Elite Adjacency Detected (>0.85)"
                })
            elif score > 0.60:
                audit_results.append({
                    "pattern": p,
                    "action": "REVIEW",
                    "target": best,
                    "score": score,
                    "reason": "Strong Adjacency Detected (>0.60)"
                })
        return audit_results
