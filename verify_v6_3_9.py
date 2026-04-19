import sys
import os
import json

# Add parent directory
sys.path.append(os.getcwd())

from headhunting_engine.matching.scorer import Scorer

def test_scorer():
    print("🧪 Testing Scorer logic (v6.3.9)...")
    scorer = Scorer()
    
    # Mock data
    cand_skills = [
        {"pattern": "Backend_Development", "depth": "Owned", "impact_type": "Quantitative"},
        {"pattern": "Cloud_DevOps_Security", "depth": "Led"}
    ]
    jd_must = {"Backend_Development", "Frontend_Development"}
    jd_nice = set()
    candidate_full = {
        "candidate_profile": {"primary_sector": "TECH_SW"},
        "career_path_quality": {"trajectory_grade": "Ascending"}
    }
    
    try:
        score, logs = scorer.calculate_score(cand_skills, jd_must, jd_nice, candidate_full)
        print(f"✅ Score: {score}")
        print(f"📊 Logs: {json.dumps(logs, indent=2)}")
        
        # Check for NameError or logic failure
        assert "final_score" in logs
        assert logs["context_fit"] == 70.0
        assert logs["trajectory_bonus"] == 8.0
        print("✨ Scorer Verification Passed!")
        
    except Exception as e:
        print(f"❌ Scorer Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scorer()
