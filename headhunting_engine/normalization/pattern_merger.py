try:
    from .adjacency_engine import AdjacencyEngine
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from adjacency_engine import AdjacencyEngine

class PatternMerger:
    """
    v6.3.6 Strategic Pattern Merger
    Groups technically adjacent or redundant functional patterns into High-Value Clusters.
    """
    
    # Core Strategic Clusters (Goal: Stay under 100 total tags across the DB)
    CLUSTERS = {
        "Strategic_Market_Intelligence": [
            "Market Research", "Competitor Analysis", "Consumer Insights", 
            "Market_Data", "Market_Trend", "Market_Intelligence", "Market_Strategy"
        ],
        "Leadership_HRM": [
            "Team_Leadership", "People_Management", "Mentoring", "Hiring",
            "Organization_Culture", "HR_", "Talent_", "Recruitment",
            "Conflict_Resolution", "Team_Building", "Resource_Allocation", "Personnel"
        ],
        "Frontend_Development": [
            "React", "Vue", "Angular", "Typescript", "Web_Development", "Javascript",
            "Ui_Ux_Implementation", "Frontend", "Css", "Html", "Next.Js"
        ],
        "Backend_Development": [
            "Java", "Python", "Go_Language", "Spring_Boot", "Node.Js", "Backend",
            "Microservices", "Rest_Api", "Api_Development", "Server_Side",
            "Sql_Database", "No_Sql", "Database_Management", "Query_Optimization"
        ],
        "Business_Strategy_Sales": [
            "Business_Development", "Strategic_Planning", "New_Business",
            "Go-To-Market", "Partnership", "Revenue", "Sales_", "Account_Management",
            "Customer_Relationship", "Crm", "B2B", "B2C", "Marketing_Strategy"
        ],
        "Product_UX_Analytics": [
            "Data_Analysis", "Product_Insights", "User_Behavior", "Analytics",
            "Kpi_", "Ab_Testing", "Growth_Hacking", "Ui/Ux", "Design_", "Figma",
            "Product_Management", "Product_Development"
        ],
        "Project_Lifecycle": [
            "Agile", "Scrum", "Project_Management", "Project_Lead",
            "Project_Lifecycle", "Stakeholder", "Risk_Management", "Operations"
        ],
        "Cloud_DevOps_Security": [
            "Aws", "Azure", "Gcp", "Docker", "Kubernetes", "Ci_Cd", "Devops",
            "Infrastructure", "Sre", "Cloud_", "Information_Security", "Network_Security", "Compliance"
        ]
    }

    def __init__(self, custom_clusters=None):
        self.clusters = custom_clusters or self.CLUSTERS
        self.mapping = {}
        for cluster, aliases in self.clusters.items():
            for alias in aliases:
                self.mapping[alias.lower().replace(" ", "_")] = cluster
                self.mapping[alias.lower()] = cluster
        self.governor = AdjacencyEngine(self.clusters)

    def audit_governance(self, patterns):
        return self.governor.audit_governance(patterns)

    def merge(self, pattern_name):
        """Maps a pattern name to its strategic cluster."""
        clean_name = (pattern_name or "").lower().strip().replace(" ", "_")
        if not clean_name:
            return None
        
        # Exact match in mapping
        if clean_name in self.mapping:
            return self.mapping[clean_name]
        
        # Substring match (e.g., "AWS Architecture" -> "Cloud_DevOps")
        for alias, cluster in self.mapping.items():
            if alias in clean_name or clean_name in alias:
                return cluster
        
        # Fallback: Just return the original name (title cased) if no cluster found
        return pattern_name.title().replace(" ", "_")

    def merge_list(self, patterns, limit=7):
        """Processes a list of patterns, merges them, and returns a unique limited list."""
        merged = []
        for p in patterns:
            m = self.merge(p)
            if m and m != "Standardized_Functional_Pattern" and m not in merged:
                merged.append(m)
        return merged[:limit]
