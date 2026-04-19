import os
import shutil
import yaml

# Top 100 Core Skills Dictionary
# keys: Categories (Domains) -> values: List of Skills
ontology_data = {
    "Business": {
        "Strategy / Biz Ops": ["전략_경영기획", "사업개발_BD", "시장분석", "경쟁전략", "신사업기획", "로드맵기획", "OKR_KPI설계"],
        "Marketing / Growth": ["퍼포먼스마케팅", "브랜드마케팅", "콘텐츠마케팅", "그로스마케팅", "CRM_마케팅", "SEO_SEM", "광고운영", "마케팅데이터분석"],
        "Sales / Revenue": ["B2B영업", "B2C영업", "세일즈전략", "리드제너레이션", "계약협상", "채널영업", "파트너십관리"],
        "Finance": ["재무회계", "관리회계", "FP_A", "기업가치평가", "투자분석", "자금관리", "IR"],
        "Product / Operation": ["제품기획_PM", "서비스기획", "UX기획", "프로젝트관리_PM", "애자일_Scrum", "운영관리", "프로세스개선"],
        "HR / 조직": ["채용_리크루팅", "조직개발_OD", "성과관리", "보상설계", "노무관리", "인재전략"]
    },
    "Tech": {
        "Backend / Infra": ["Backend", "API_설계", "Microservices", "Database", "SQL", "NoSQL", "DistributedSystem", "SystemArchitecture"],
        "AI / Data": ["MachineLearning", "DeepLearning", "데이터분석", "데이터엔지니어링", "MLOps", "NLP", "ComputerVision", "추천시스템"],
        "Frontend": ["Frontend", "React", "NextJS", "TypeScript", "UI_개발", "웹성능최적화"],
        "DevOps / Cloud": ["DevOps", "Docker", "Kubernetes", "CI_CD", "AWS", "GCP", "Azure", "Terraform"],
        "Hardware / DeepTech": ["NPU", "GPU", "FPGA", "ASIC", "SoC", "EmbeddedSystem", "Firmware", "RTOS"],
        "System / Low-level": ["C_C++", "Rust", "OperatingSystem", "MemorySystem", "Compiler", "ParallelComputing"]
    }
}

# Auto-generate relationships based on domains to guarantee >= 3 relationships
# This is a baseline setup. A domain expert will refine these.
def generate_relationships(node_name, domain_name, core_group):
    rels = {
        "depends_on": [],
        "related_to": [],
        "part_of": [],
        "used_in": [],
        "similar_to": []
    }
    
    # 1. Hardcoded DeepTech/AI relationships as requested by user
    if node_name == "NPU":
        rels["depends_on"] = ["SoC", "MemorySystem", "ParallelComputing"]
        rels["related_to"] = ["GPU", "ASIC"]
        rels["used_in"] = ["EdgeAI", "AIInference"] # Assuming these will exist
    elif node_name == "MachineLearning":
        rels["depends_on"] = ["데이터분석", "Python"]
        rels["part_of"] = ["AI_Data"]
        rels["related_to"] = ["DeepLearning", "추천시스템"]
    elif node_name == "퍼포먼스마케팅":
        rels["depends_on"] = ["마케팅데이터분석", "광고운영"]
        rels["related_to"] = ["브랜드마케팅", "CRM_마케팅"]
        rels["used_in"] = ["그로스마케팅"]
    else:
        # 2. Heuristic generation for others
        # Every node is part_of its domain
        rels["part_of"].append(domain_name.replace(" ", ""))
        
        # Link siblings in the same category
        for other_node in ontology_data[core_group][domain_name]:
            if other_node != node_name and len(rels["related_to"]) < 2:
                rels["related_to"].append(other_node)
                
        # Some cross category links
        if core_group == "Tech" and "Data" not in domain_name:
            rels["depends_on"].append("SystemArchitecture")
        if core_group == "Business" and domain_name != "Strategy / Biz Ops":
            rels["depends_on"].append("전략_경영기획")

    return rels

vault_dir = "obsidian_vault"
if os.path.exists(vault_dir):
    shutil.rmtree(vault_dir)

os.makedirs(os.path.join(vault_dir, "Skills", "Business"))
os.makedirs(os.path.join(vault_dir, "Skills", "Tech"))
os.makedirs(os.path.join(vault_dir, "Meta"))

template = '''---
type: skill
domain: {domain}

aliases:
{aliases_str}
mass: auto

depends_on:
{depends_on_str}
related_to:
{related_to_str}
part_of:
{part_of_str}
used_in:
{used_in_str}
similar_to:
{similar_to_str}
---

# {name}

본문은 최소화합니다.
- {domain} 도메인의 핵심 스킬입니다.
'''

canonical_map = {}

# Generate Nodes
count = 0
for core_group, domains in ontology_data.items():
    for domain, skills in domains.items():
        for skill in skills:
            # Canonical Mapping defaults
            safe_skill = skill.replace(" ", "")
            # Basic aliases mock
            aliases = [skill.replace("_", " "), skill.lower()]
            if skill == "FP_A": 
                aliases.append("FP&A")
                safe_skill = "FP&A"
            elif "_PM" in skill:
                aliases.append(skill.split("_")[0])
            
            # Canonical entry
            for a in aliases:
                canonical_map[a] = safe_skill
            canonical_map[safe_skill] = safe_skill
            
            # Relationships
            rels = generate_relationships(safe_skill, domain, core_group)
            
            def format_list(lst):
                if not lst: return "  []"
                return "\n".join([f"  - \"[[{x}]]\"" for x in lst])
            
            content = template.format(
                name=safe_skill,
                domain=domain,
                aliases_str="\n".join([f"  - {a}" for a in aliases]),
                depends_on_str=format_list(rels["depends_on"]),
                related_to_str=format_list(rels["related_to"]),
                part_of_str=format_list(rels["part_of"]),
                used_in_str=format_list(rels["used_in"]),
                similar_to_str=format_list(rels["similar_to"])
            )
            
            # File creation
            file_name = safe_skill.replace("/", "_").replace("&", "_")
            folder = os.path.join(vault_dir, "Skills", core_group)
            filepath = os.path.join(folder, f"{file_name}.md")
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            count += 1

# Generate Canonical Map
canonical_yaml_path = os.path.join(vault_dir, "Meta", "canonical_map.yaml")
with open(canonical_yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(canonical_map, f, allow_unicode=True, default_flow_style=False)

# Add some custom canonicals requested by user
with open(canonical_yaml_path, "a", encoding="utf-8") as f:
    f.write("\n전략: 전략_경영기획\n기획: 전략_경영기획\n사업전략: 전략_경영기획\n")
    f.write("\n퍼포먼스: 퍼포먼스마케팅\n퍼포먼스 마케팅: 퍼포먼스마케팅\n")
    f.write("\n백엔드: Backend\n서버개발: Backend\n")
    f.write("\nAI: MachineLearning\n딥러닝: DeepLearning\n")

print(f"Generated {count} Obsidian nodes in '{vault_dir}/Skills'")
print(f"Generated Canonical Map in '{vault_dir}/Meta/canonical_map.yaml'")
