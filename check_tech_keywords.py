import sqlite3

conn = sqlite3.connect("candidates.db")
cursor = conn.cursor()

queries = [
    ("프론트엔드/React", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%프론트엔드%'
           OR lower(raw_text) LIKE '%frontend%'
           OR lower(raw_text) LIKE '%react%'
           OR lower(raw_text) LIKE '%리액트%'
    """),
    ("iOS/Swift", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%ios%'
           OR lower(raw_text) LIKE '%swift%'
           OR lower(raw_text) LIKE '%xcode%'
    """),
    ("안드로이드/Kotlin", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%안드로이드%'
           OR lower(raw_text) LIKE '%android%'
           OR lower(raw_text) LIKE '%kotlin%'
    """),
    ("데이터 분석/SQL", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%데이터 분석%'
           OR lower(raw_text) LIKE '%sql%'
           OR lower(raw_text) LIKE '%python%'
           OR lower(raw_text) LIKE '%머신러닝%'
    """),
    ("UX/디자인", """
        SELECT count(*) FROM candidates
        WHERE lower(raw_text) LIKE '%ux%'
           OR lower(raw_text) LIKE '%figma%'
           OR lower(raw_text) LIKE '%프로덕트 디자인%'
    """)
]

for label, q in queries:
    cursor.execute(q)
    cnt = cursor.fetchone()[0]
    print(f"{label}: {cnt}명")

conn.close()
