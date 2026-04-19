import re

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1-A & 1-B Replacements
replacements = {
    "Kotlin": "Kotlin",
    "kotlin": "Kotlin",
    "SQL": "SQL",
    "펌웨어": "Firmware",
    "임베디드": "Embedded_Systems",
    "회로설계": "PCB_Design",
    "Firmware": "Firmware",
    "Bootloader": "Firmware",
    "교육": "Learning_and_Development",
    "DPDK": "DPDK",
    "SPDK": "SPDK",
    "LLVM": "LLVM",
    "AiM": "PIM",
    # 1-B
    "Node.js": "Node.js",
    "Vue.js": "Vue.js",
    "vue.js": "Vue.js",
    "React": "React",
    "React.js": "React",
    "Vue": "Vue.js",
    "Express": "Express",
    "Next.js": "Next.js",
    "Django": "Django",
    "FastAPI": "FastAPI",
    "Spring": "Spring",
    "Python": "Python",
    "Java": "Java",
    "java": "Java",
    "JAVA": "Java",
    "Go": "Go",
    "Golang": "Go"
}

# Apply dictionary logic
# We need to replace occurrences like "Key": "OldValue" with "Key": "NewValue"
# But we don't know the exact OldValue. So we replace `"Key": ".*?"` or `'Key': '.*?'`
for k, v in replacements.items():
    # Replace double quotes
    pattern_double = r'"{0}":\s*"[^"]+"'.format(re.escape(k))
    content = re.sub(pattern_double, f'"{k}": "{v}"', content)
    # Replace single quotes
    pattern_single = r"'{0}':\s*'[^']+'".format(re.escape(k))
    content = re.sub(pattern_single, f"'{k}': '{v}'", content)
    
    # Also in case it wasn't there, we just append it safely if it completely wasn't found
    # But wait, the user's instruction implies modifying existing wrong mappings.
    # What if it's missing? It's better to just inject into CANONICAL_MAP if it's missing.
    # To do this cleanly, we can find the end of CANONICAL_MAP dictionary, but regex is tricky for a 4500 line dict.
    
# Remove Investor_Relations key
content = re.sub(r'\s*"Investor_Relations":\s*"[^"]+",?', '', content)
content = re.sub(r"\s*'Investor_Relations':\s*'[^']+',?", '', content)

# 1-C. Append SKILL_CATEGORIES
skill_categories = """\n\nSKILL_CATEGORIES = {
    "Backend": ["Java", "Spring", "Python", "Django", "FastAPI", "Node.js", "Express", "Go", "Kotlin", "CSharp", "Ruby", "PHP", "Scala", "Rust", "REST_API", "GraphQL", "gRPC", "MSA_Architecture"],
    "Frontend": ["React", "Vue.js", "Next.js", "TypeScript", "JavaScript", "Angular", "Svelte", "Webpack", "Vite"],
    "Mobile": ["Android", "iOS", "Swift", "Flutter", "React_Native"],
    "DevOps": ["Kubernetes", "Docker", "Terraform", "Helm", "ArgoCD", "GitOps", "Jenkins", "Ansible", "CI_CD_Pipeline", "GitHub_Actions", "AWS", "GCP", "Azure", "EKS", "Karpenter", "Istio"],
    "SRE": ["SRE", "Incident_Management", "Observability", "Chaos_Engineering", "OpenTelemetry", "Prometheus", "Grafana", "Datadog"],
    "Data": ["Spark", "Hadoop", "Kafka", "Elasticsearch", "Airflow", "dbt", "Flink", "BigQuery", "Redshift", "Snowflake", "ETL"],
    "Data_Analytics": ["BI", "Tableau", "Looker", "Power_BI", "Superset", "Cohort_Analysis", "Funnel_Analysis", "Metric_Design", "SQL"],
    "AI_ML": ["PyTorch", "TensorFlow", "JAX", "CUDA", "Triton", "TensorRT", "TensorRT_LLM", "BERT", "Transformer", "Fine_Tuning", "MLOps", "Kubeflow", "Hugging_Face"],
    "LLM_Serving": ["vLLM", "SGLang", "LLM", "RAG", "KV_Caching", "PD_Disaggregation", "LLM_Inference_Scheduling", "Tensor_Parallel", "Expert_Parallel", "MoE"],
    "AI_Research": ["NLP", "Computer_Vision", "Diffusion", "GAN", "NeRF", "Reinforcement_Learning", "RLHF", "Knowledge_Distillation", "Multimodal", "Speech_Recognition", "LLM_Evaluation"],
    "Recommendation_System": ["RecSys", "Collaborative_Filtering", "Matrix_Factorization", "Bandit_Algorithm", "Recommendation"],
    "QA_Testing": ["QA_Engineering", "Test_Automation", "Selenium", "Appium", "pytest", "Performance_Testing", "Load_Testing", "KUnit", "Googletest"],
    "Security": ["Penetration_Testing", "Vulnerability_Assessment", "ISMS", "Privacy_Protection", "Information_Security", "Compliance", "Internal_Control"],
    "Blockchain": ["Blockchain", "Smart_Contract", "Solidity", "Web3", "Ethereum", "Hyperledger"],
    "Game_Dev": ["Unity", "Unreal", "Game_Client", "Game_Server", "Shader"],
    "Networking_HPC": ["InfiniBand", "RDMA", "RoCE", "NCCL", "OpenMPI", "AllReduce", "Ethernet", "EFA", "High_Performance_Computing", "DPDK"],
    "NPU_AI_Chip": ["NPU", "HIP", "RISC_V", "Tensix_ISA", "AI_Compiler", "LLVM", "TVM"],
    "SoC_Architecture": ["SoC", "ARM_Architecture", "RISC_V", "HBM", "HBM3", "CXL", "PCIe", "Advanced_Packaging", "TSV"],
    "Chip_Design": ["RTL_Design", "SystemVerilog", "Verilog", "VHDL", "DFT", "Physical_Design", "IP_Design", "UVM", "FPGA", "HLS", "Clock_Domain_Crossing"],
    "Chip_Validation": ["Silicon_Validation", "Chip_Bringup", "Board_Bringup", "Signal_and_Power_Integrity", "Hardware_Simulation_Tools"],
    "Embedded_Firmware": ["Firmware", "RTOS", "Bootloader", "Embedded_Systems", "Embedded_Linux", "Yocto", "Linux_Kernel", "Device_Driver", "PCB_Design", "Automotive_Software", "AUTOSAR"],
    "Storage_Systems": ["NVMe", "NVMe_oF", "SSD_Controller", "SPDK"],
    "Accounting": ["K_IFRS", "US_GAAP", "IFRS", "Financial_Accounting", "Consolidated_Accounting", "Financial_Audit", "Internal_Control", "CPA", "AICPA", "Tax_Accounting", "Management_Accounting", "Transfer_Pricing"],
    "Finance_Planning": ["FP_and_A", "Corporate_Planning", "Budgeting", "Forecasting", "Financial_Systems_Management"],
    "Investment": ["Investment_Management", "Venture_Capital", "Private_Equity", "Mergers_and_Acquisitions", "Due_Diligence", "Valuation", "Valuation_Modeling", "DCF"],
    "Treasury": ["Treasury_Management", "FX_Risk", "Cash_Management"],
    "Fintech": ["Payment_System", "Open_Banking", "AML", "KYC", "Financial_Regulation"],
    "Marketing": ["Performance_Marketing", "Growth_Marketing", "Brand_Management", "Content_Marketing", "SEO", "CRM_Marketing", "App_Marketing"],
    "PR_Communications": ["Public_Relations", "Investor_Relations", "Media_Relations"],
    "Strategy_Planning": ["Corporate_Planning", "Business_Development", "Business_Model_Planning", "Value_Creation_and_PMI"],
    "Product": ["Product_Manager", "Service_Planning", "UX_UI_Design", "Prototyping", "Figma", "A_B_Testing"],
    "HR": ["Talent_Acquisition", "HR_Strategic_Planning", "Compensation_and_Benefits", "Learning_and_Development", "Organizational_Development", "Global_HR"],
    "Legal": ["Legal_Practice", "Patent_Management", "Compliance", "Regulatory_Affairs", "Forensic_Accounting"],
    "Energy": ["Power_Grid_Engineering", "BESS", "ESS", "Solar_Energy", "Renewable_Energy", "VPP", "Battery_Technology", "Offshore_Wind"],
    "Operations": ["SCM", "Logistics_and_Supply_Chain", "Procurement_Buyer", "ERP", "Manufacturing"]
}
"""

if "SKILL_CATEGORIES" not in content:
    content += skill_categories
else:
    # replace existing SKILL_CATEGORIES
    content = re.sub(r'SKILL_CATEGORIES\s*=\s*\{.*?\}\s*$', skill_categories.strip(), content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Update completed for Step 1.")
