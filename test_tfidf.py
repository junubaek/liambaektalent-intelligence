import logging
from jd_compiler import prefilter_candidates

res = prefilter_candidates("IPO/펀딩 대비 자금 담당자 6년차 자금 Treasury Cash FX 환리스크", num_candidates=300)

found = [name for name in res if "범기" in name or "대중" in name]
print(f"Total retrieved from TF-IDF: {len(res)}")
print(f"Targets found in TF-IDF $names: {found}")
