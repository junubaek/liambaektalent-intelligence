import sys
sys.path.insert(0, '.')
from ontology_graph import CANONICAL_MAP

nodes = set(CANONICAL_MAP.values())
check = ['Team_Leadership', 'Financial_Analysis', 'Cost_Reduction', 'UX_Design', 
         'Product_Launch', 'HR_Management', 'Project_Management', 'Data_Analysis',
         'Market_Research', 'Financial_Reporting', 'Sales_Management', 'Content_Strategy',
         'Public_Relations', 'Performance_Marketing', 'Strategic_Planning']

for n in check:
    print(n, ':', n in nodes)

print('\nAll nodes containing Leadership:')
for n in sorted(nodes):
    if 'Leadership' in n or 'HR' in n or 'PR' in n:
        print(' ', n)
