from app.database import SessionLocal
from app.models import Candidate, ParsingCache

db = SessionLocal()
c_count = db.query(Candidate).count()
p_count = db.query(ParsingCache).count()
joined_count = db.query(Candidate).join(ParsingCache).count()
print(f'Candidate count: {c_count}')
print(f'ParsingCache count: {p_count}')
print(f'Joined count: {joined_count}')

kdj = db.query(Candidate).filter(Candidate.name_kr.like('%김대중%')).first()
if kdj:
    print('Found 김대중 ID:', kdj.id)
    print('Raw careers length:', len(kdj.raw_text) if kdj.raw_text else 0)
    if kdj.parsing_cache:
        ext = kdj.parsing_cache.parsed_dict
        print(f'Parsed dict current_company: {ext.get("current_company")}')
        careers = ext.get("careers", [])
        if careers:
            print(f'Careers[0]: {careers[0]}')
        else:
            print('No careers list')
        summary = ext.get("profile_summary", "")
        print(f'Profile Summary: {summary[:100]}')
    else:
        print('No parsing cache for 김대중')
db.close()
