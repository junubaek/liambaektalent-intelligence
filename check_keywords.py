import sqlite3
import pandas as pd

conn = sqlite3.connect('candidates.db')

query = """
SELECT 'NPU런타임' as type, count(*) as count FROM candidates 
WHERE raw_text LIKE '%NPU%' OR raw_text LIKE '%런타임%' AND raw_text LIKE '%커널%'
UNION ALL
SELECT 'HBM', count(*) FROM candidates 
WHERE raw_text LIKE '%HBM%' OR raw_text LIKE '%High Bandwidth Memory%'
UNION ALL
SELECT 'PCIe검증', count(*) FROM candidates 
WHERE raw_text LIKE '%PCIe%' OR raw_text LIKE '%PCI Express%'
UNION ALL
SELECT 'vLLM', count(*) FROM candidates 
WHERE raw_text LIKE '%vLLM%' OR raw_text LIKE '%SGLang%'
UNION ALL
SELECT 'NCCL', count(*) FROM candidates 
WHERE raw_text LIKE '%NCCL%' OR raw_text LIKE '%Collective Communication%'
UNION ALL
SELECT 'SerDes', count(*) FROM candidates 
WHERE raw_text LIKE '%SerDes%' OR raw_text LIKE '%SI/PI%'
UNION ALL
SELECT 'RISC-V', count(*) FROM candidates 
WHERE raw_text LIKE '%RISC-V%' OR raw_text LIKE '%RISC V%'
UNION ALL
SELECT 'CXL', count(*) FROM candidates 
WHERE raw_text LIKE '%CXL%' OR raw_text LIKE '%NVMe-oF%'
UNION ALL
SELECT 'eBPF', count(*) FROM candidates 
WHERE raw_text LIKE '%eBPF%' OR raw_text LIKE '%OVS%'
UNION ALL
SELECT '5G_ORAN', count(*) FROM candidates 
WHERE raw_text LIKE '%O-RAN%' OR raw_text LIKE '%5G NR%'
"""

df = pd.read_sql_query(query, conn)
print("=== Keyword Search Targets ===")
print(df.to_string(index=False))

print("\n=== Over 10 Filter ===")
filtered = df[df['count'] >= 10]
if len(filtered) > 0:
    print(filtered.to_string(index=False))
else:
    print("None over 10")

conn.close()
