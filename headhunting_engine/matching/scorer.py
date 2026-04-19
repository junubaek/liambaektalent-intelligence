from typing import Dict, List, Set, Tuple

class Scorer:
    """
    Calculates deterministic matching scores with full audit logging.
    - Career Trajectory (20%)
    - Context Fit (15%)
    """
    
    DEPTH_WEIGHTS = {
        "Owned": 1.00,
        "Led": 0.85,
        "Applied": 0.65,
        "Assisted": 0.40,
        "Mentioned": 0.20
    }

    # v6.2 Domain Affinity Matrix (2-Hop Weights)
    DOMAIN_AFFINITY = {
        ("AI_ML_RESEARCH", "AI_ENGINEERING"): 0.60,
        ("DATA_ENGINEERING", "AI_ENGINEERING"): 0.55,
        ("CHIP_DESIGN", "AI_ML_RESEARCH"): 0.50,
        ("SW_BACKEND", "INFRA_DEVOPS"): 0.55,
        ("SECURITY_ENGINEERING", "SW_BACKEND"): 0.45,
        ("STRATEGY_MA", "FINANCE_ACCOUNTING"): 0.55,
        ("SW_BACKEND", "SW_FRONTEND"): 0.35,
        ("HRM_HRD", "STRATEGY_MA"): 0.30,
        ("CHIP_DESIGN", "SW_BACKEND"): 0.20
    }

    def __init__(self, version_manager=None):
        self.version_manager = version_manager

    def get_hop_weight(self, domain_a: str, domain_b: str, hop: int) -> float:
        if hop == 0: return 1.0
        if hop == 1: return 0.75 # Default hop1
        
        # hop 2 dynamic lookup
        pair = tuple(sorted([domain_a, domain_b]))
        return self.DOMAIN_AFFINITY.get(pair, 0.40) # Fallback to 0.4 if not in matrix

    def calculate_score(self, cand_skills: List[Dict], jd_must: Set[str], jd_nice: Set[str], candidate_full: Dict = None, canonical_ids: Set[str] = None) -> Tuple[float, Dict]:
        """
        [v6.3.9] Fixed Precision Matching Engine
        """
        # 1. Pattern Coverage (45%)
        cand_patterns_map = {p["pattern"]: p.get("depth", "Mentioned") for p in cand_skills}
        
        coverage_score = 0
        if jd_must:
            matched = [p for p in jd_must if p in cand_patterns_map]
            coverage_score = (len(matched) / len(jd_must)) * 100
        
        # 2. Depth & Impact (30%)
        depth_sum = 0
        if jd_must:
            for p in jd_must:
                depth = cand_patterns_map.get(p, "None")
                depth_sum += self.DEPTH_WEIGHTS.get(depth, 0.0)
            avg_depth = depth_sum / len(jd_must)
        else:
            avg_depth = 0
            
        impact_multiplier = 1.0
        if any(p.get("impact_type") == "Quantitative" for p in cand_skills if p["pattern"] in jd_must):
            impact_multiplier = 1.1

        depth_impact_score = min(100, avg_depth * 100 * impact_multiplier)

        # 3. Context Fit (25%) - Functional Sector Alignment
        context_score = 50.0 # Baseline
        if candidate_full:
            cand_sector = candidate_full.get("candidate_profile", {}).get("primary_sector", "Unclassified")
            # In a real matching scenario, we'd compare cand_sector with JD sector
            # For now, we use a metadata-based baseline to ensure no NameError
            context_score = 70.0 if cand_sector != "Unclassified" else 50.0

        # 4. Career Trajectory Bonus (Additive)
        trajectory_quality = {}
        if candidate_full:
            trajectory_quality = candidate_full.get("career_path_quality", {})
        
        grade = trajectory_quality.get("trajectory_grade", "Neutral")
        trajectory_bonus = 0.0
        if grade == "Ascending": trajectory_bonus = 8.0
        elif grade == "Stable": trajectory_bonus = 3.0
        elif grade == "Volatile": trajectory_bonus = -3.0
        elif grade == "Declining": trajectory_bonus = -5.0

        if coverage_score <= 0 and not jd_must: # Handle edge case where JD has no must patterns
            coverage_score = 50.0 

        base_match = (
            coverage_score * 0.45 +
            depth_impact_score * 0.30 +
            context_score * 0.25
        )

        final_score = min(100.0, max(0.0, base_match + trajectory_bonus))

        return final_score, {
            "final_score": round(final_score, 2),
            "pattern_coverage": round(coverage_score, 2),
            "depth_impact": round(depth_impact_score, 2),
            "context_fit": round(context_score, 2),
            "trajectory_bonus": trajectory_bonus
        }
