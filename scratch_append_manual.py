import json

addition = """
# --- Manual Core Gravity Fields (Top 20 Orphan Nodes) ---
UNIFIED_GRAVITY_FIELD.update({
    # ── 개발 핵심 ──
    "Android_Development": {
        "core_attracts": {
            "Mobile_Application_Development": 0.9,
            "Frontend_Development": 0.5,
            "Backend_Engineering": 0.4
        },
        "repels": {
            "Financial_Accounting": -0.4,
            "Brand_Management": -0.4,
            "Tax_Accounting": -0.5
        }
    },
    "Mobile_Application_Development": {
        "core_attracts": {
            "Android_Development": 0.8,
            "Frontend_Development": 0.6,
            "Backend_Engineering": 0.5
        },
        "repels": {
            "Financial_Accounting": -0.4,
            "Brand_Management": -0.4
        }
    },
    "Data_Analysis": {
        "core_attracts": {
            "Data_Engineering": 0.8,
            "Data_Science": 0.7,
            "Machine_Learning": 0.6
        },
        "repels": {
            "Brand_Management": -0.3,
            "Tax_Accounting": -0.4,
            "Content_Marketing": -0.3
        }
    },
    "Information_Security": {
        "core_attracts": {
            "Security_Architecture": 0.9,
            "Vulnerability_Assessment": 0.8,
            "Infrastructure_and_Cloud": 0.6
        },
        "repels": {
            "Brand_Management": -0.5,
            "Content_Marketing": -0.5,
            "Tax_Accounting": -0.5
        }
    },
    "Python": {
        "core_attracts": {
            "Backend_Engineering": 0.7,
            "Data_Engineering": 0.7,
            "Machine_Learning": 0.6
        },
        "repels": {
            "Brand_Management": -0.4,
            "Tax_Accounting": -0.5,
            "Content_Marketing": -0.4
        }
    },
    "Java": {
        "core_attracts": {
            "Backend_Java": 0.9,
            "Backend_Engineering": 0.8,
            "MSA_Architecture": 0.6
        },
        "repels": {
            "Brand_Management": -0.4,
            "Tax_Accounting": -0.5,
            "Content_Marketing": -0.4
        }
    },
    "SQL": {
        "core_attracts": {
            "Database_Management": 0.9,
            "Data_Engineering": 0.7,
            "Backend_Engineering": 0.6
        },
        "repels": {
            "Brand_Management": -0.4,
            "Content_Marketing": -0.4
        }
    },

    # ── 마케팅 핵심 ──
    "Digital_Marketing": {
        "core_attracts": {
            "Performance_Marketing": 0.8,
            "Growth_Marketing": 0.7,
            "CRM_Marketing": 0.6
        },
        "repels": {
            "Tax_Accounting": -0.4,
            "Backend_Engineering": -0.3,
            "Financial_Accounting": -0.3
        }
    },
    "Growth_Marketing": {
        "core_attracts": {
            "Performance_Marketing": 0.8,
            "CRM_Marketing": 0.7,
            "Data_Analysis": 0.6
        },
        "repels": {
            "Tax_Accounting": -0.4,
            "Financial_Accounting": -0.3,
            "Backend_Engineering": -0.3
        }
    },

    # ── HR 핵심 ──
    "Payroll_Management": {
        "core_attracts": {
            "Compensation_and_Benefits": 0.9,
            "Labor_Law_Compliance": 0.7,
            "Financial_Accounting": 0.5
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.4,
            "DevOps": -0.4
        }
    },
    "Labor_Law_Compliance": {
        "core_attracts": {
            "Employee_Relations": 0.9,
            "Compensation_and_Benefits": 0.6,
            "HR_Strategic_Planning": 0.5
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.4,
            "DevOps": -0.5
        }
    },
    "Corporate_Culture_Branding": {
        "core_attracts": {
            "Organizational_Development": 0.9,
            "HR_Strategic_Planning": 0.7,
            "Learning_and_Development": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.3,
            "Tax_Accounting": -0.4,
            "DevOps": -0.4
        }
    },
    "Learning_and_Development": {
        "core_attracts": {
            "Organizational_Development": 0.9,
            "Corporate_Culture_Branding": 0.7,
            "HR_Strategic_Planning": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.3,
            "Tax_Accounting": -0.4,
            "DevOps": -0.4
        }
    },

    # ── 재무 핵심 ──
    "Corporate_Funding": {
        "core_attracts": {
            "Treasury_Management": 0.9,
            "IR_Management": 0.7,
            "Financial_Planning_and_Analysis": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.4,
            "DevOps": -0.5
        }
    },
    "Financial_Audit": {
        "core_attracts": {
            "Financial_Accounting": 0.9,
            "Internal_Control": 0.8,
            "Tax_Accounting": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.5,
            "DevOps": -0.5
        }
    },

    # ── 영업 핵심 ──
    "Global_Sales_and_Marketing": {
        "core_attracts": {
            "B2B_Sales": 0.8,
            "Technical_Sales": 0.7,
            "Corporate_Strategic_Planning": 0.5
        },
        "repels": {
            "Financial_Accounting": -0.3,
            "Tax_Accounting": -0.4,
            "DevOps": -0.4
        }
    },
    "B2C_Sales": {
        "core_attracts": {
            "CRM_Marketing": 0.7,
            "Growth_Marketing": 0.6,
            "Performance_Marketing": 0.6
        },
        "repels": {
            "Financial_Accounting": -0.3,
            "Tax_Accounting": -0.4,
            "Backend_Engineering": -0.2
        }
    },

    # ── 전략/기획 핵심 ──
    "New_Business_Development": {
        "core_attracts": {
            "Corporate_Strategic_Planning": 0.8,
            "M_and_A_Strategy": 0.7,
            "IR_Management": 0.5
        },
        "repels": {
            "Financial_Accounting": -0.2,
            "Tax_Accounting": -0.3,
            "DevOps": -0.4
        }
    },
    "Compensation_and_Benefits": {
        "core_attracts": {
            "Payroll_Management": 0.9,
            "HR_Strategic_Planning": 0.7,
            "Labor_Law_Compliance": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.4,
            "DevOps": -0.5
        }
    },
    "Internal_Control": {
        "core_attracts": {
            "Financial_Accounting": 0.8,
            "Financial_Audit": 0.8,
            "Tax_Accounting": 0.6
        },
        "repels": {
            "Backend_Engineering": -0.4,
            "Brand_Management": -0.5,
            "DevOps": -0.5
        }
    },
})
"""

with open("ontology_graph.py", "a", encoding="utf-8") as f:
    f.write(addition)
print("Added manual fields to ontology_graph.py")
