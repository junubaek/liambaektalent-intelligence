import re

updates = {
    # Finance
    "Tax_Accounting": {
        "core_attracts": {"Tax_Advisory_and_Compliance":0.9, "Transfer_Pricing":0.8, "Financial_Accounting":0.5},
        "repels": {"Treasury_Management":-0.3, "IPO_Management":-0.2, "IR_Management":-0.2}
    },
    "IR_Management": {
        "core_attracts": {"IPO_Preparation_and_Execution":0.9, "Investor_Relations":0.9, "Corporate_Disclosure":0.8},
        "repels": {"Tax_Accounting":-0.3, "Treasury_Management":-0.2}
    },

    # HR
    "Talent_Acquisition": {
        "core_attracts": {"Recruiting_and_Talent_Acquisition":0.9, "ATS":0.7, "Corporate_Culture_Branding":0.5},
        "repels": {"Payroll_Management":-0.3, "Labor_Law_Compliance":-0.2}
    },
    "Employee_Relations": {
        "core_attracts": {"Labor_Law_Compliance":0.9, "취업규칙":0.8, "노동청 대응":0.7},
        "repels": {"Talent_Acquisition":-0.2, "Organizational_Development":-0.2}
    },
    "Compensation_and_Benefits": {
        "core_attracts": {"Payroll_Management":0.9, "Performance_and_Compensation_System":0.8, "Financial_Accounting":0.4},
        "repels": {"Talent_Acquisition":-0.2, "Employee_Relations":-0.2}
    },
    "Organizational_Development": {
        "core_attracts": {"Corporate_Culture_Branding":0.8, "Learning_and_Development":0.8, "HR_Strategic_Planning":0.7},
        "repels": {"Payroll_Management":-0.3, "Labor_Law_Compliance":-0.2}
    },
    "HRBP": {
        "core_attracts": {"HR_Strategic_Planning":0.9, "Organizational_Development":0.8, "Talent_Acquisition":0.6},
        "repels": {"Payroll_Management":-0.3, "Labor_Law_Compliance":-0.2}
    },

    # Marketing
    "Brand_Management": {
        "core_attracts": {"Brand_Identity_and_Experience":0.9, "Corporate_Public_Relations":0.8, "Global_Brand_Campaign":0.7},
        "repels": {"Performance_Marketing":-0.3, "CRM_Marketing":-0.2}
    },
    "Content_Marketing": {
        "core_attracts": {"Brand_Communication":0.8, "Content_Marketing_Strategy":0.8, "Influencer_and_Sponsorship_Marketing":0.6},
        "repels": {"Performance_Marketing":-0.2, "CRM_Marketing":-0.2}
    },
    "CRM_Marketing": {
        "core_attracts": {"Data_Engineering":0.7, "Growth_Marketing":0.8, "Data_Analysis":0.7},
        "repels": {"Brand_Management":-0.2, "Content_Marketing":-0.2}
    },
    "Corporate_Public_Relations": {
        "core_attracts": {"Corporate_Crisis_Management":0.8, "Financial_Communication":0.7, "Brand_Communication":0.7},
        "repels": {"Performance_Marketing":-0.3, "CRM_Marketing":-0.2}
    },

    # Tech
    "Data_Engineering": {
        "core_attracts": {"Data_Pipeline_Construction":0.9, "Big_Data_Processing":0.8, "Data_Warehouse_Architecture":0.8},
        "repels": {"Backend_Engineering":-0.1, "MLOps":-0.1}
    },
    "Machine_Learning": {
        "core_attracts": {"Deep_Learning":0.9, "MLOps":0.8, "Data_Science":0.8},
        "repels": {"Backend_Engineering":-0.2, "DevOps":-0.1}
    },
    "Frontend_Development": {
        "core_attracts": {"UX_UI_Design":0.7, "Frontend_Architecture":0.8, "Modern_Frontend_Architecture":0.7},
        "repels": {"Backend_Engineering":-0.2, "DevOps":-0.2}
    },

    # Strategy / Sales / Ops / Legal
    "Corporate_Strategic_Planning": {
        "core_attracts": {"Corporate_Strategy":0.9, "Financial_Planning_and_Analysis":0.7, "M_and_A_Strategy":0.7},
        "repels": {"Financial_Accounting":-0.2, "General_Affairs":-0.3}
    },
    "B2B영업": {
        "core_attracts": {"Global_Sales_and_Marketing":0.8, "영업기획":0.8, "Technical_Sales":0.6},
        "repels": {"B2C영업":-0.1, "Content_Marketing":-0.2}
    },
    "Supply_Chain_Management": {
        "core_attracts": {"Procurement_and_Sourcing":0.8, "Logistics_and_Inventory_Optimization":0.8, "Demand_Forecasting":0.7},
        "repels": {"Corporate_Strategic_Planning":-0.2, "Financial_Planning_and_Analysis":-0.2}
    },
    "Legal_Practice": {
        "core_attracts": {"Corporate_Legal_Counsel":0.9, "Patent_Management":0.7, "Financial_Compliance":0.5},
        "repels": {"Tax_Accounting":-0.3, "Financial_Accounting":-0.2}
    },
    "Compliance": {
        "core_attracts": {"Financial_Compliance":0.9, "Anti_Money_Laundering":0.8, "Data_Privacy_and_Compliance":0.7},
        "repels": {"Legal_Practice":-0.1, "Financial_Accounting":-0.2}
    }
}

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

# For each key, try to find "Key": { ... } in the file
# and inject/replace core_attracts and repels.
for node, data in updates.items():
    # Find node block
    pattern = r'(\"' + re.escape(node) + r'\"\s*:\s*\{)'
    match = re.search(pattern, content)
    if not match:
        # Node not found, append it before the end of UNIFIED_GRAVITY_FIELD
        # Let's find the end of UNIFIED_GRAVITY_FIELD.
        # This is hard via regex, so instead of replacing string, let's just use Python's ast?
        # Actually, if we just find UNIFIED_GRAVITY_FIELD, we can append to the bottom.
        # But maybe we can just do python dict updates in code and write out the dict?
        pass

# It's safer to just write the dict updates at the end of the file.
update_code = "\n# Runtime updates to UNIFIED_GRAVITY_FIELD\n"
for node, data in updates.items():
    update_code += f"if '{node}' not in UNIFIED_GRAVITY_FIELD:\n"
    update_code += f"    UNIFIED_GRAVITY_FIELD['{node}'] = {{}}\n"
    for k, v in data.items():
        update_code += f"UNIFIED_GRAVITY_FIELD['{node}']['{k}'] = {repr(v)}\n"

with open('ontology_graph.py', 'a', encoding='utf-8') as f:
    f.write(update_code)

print("Appended dynamic updates to ontology_graph.py")
