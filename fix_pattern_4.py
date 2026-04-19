import json

with open("pattern_report.json", "r", encoding="utf-8") as f:
    report = json.load(f)

cleanup_skills = []
for s in report.get("bottom_50_skills", []):
    if s["count"] == 0:
        cleanup_skills.append(s["skill"])

with open("cleanup_candidates.txt", "w", encoding="utf-8") as f:
    for skill in cleanup_skills:
        f.write(skill + "\n")

print(f"저장 완료: 총 {len(cleanup_skills)}개의 스킬 노드 (0건 연결) -> cleanup_candidates.txt")
