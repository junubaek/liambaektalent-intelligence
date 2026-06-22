import sqlite3, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = [
    '배유정','김완희','배문성','강건규','최우성',
    '이형무','전형준','엄승태','신동윤','김도형','이석현',
    '홍기재','김민상','최성우','김학주','박상수','고영석',
    '이진호','정의수','고여찬','강종훈','이민찬',
    '김상원','김종민','임동수','김준호','박민규',
    '윤석훈','고유현','김지우','정현구','손태희',
    '김태욱','김성우','김동민',
    '손범래','최경석','신동호','신수용','석윤석',
    '김태준','오수진','곽창신','김대중','박관우',
    '김정수','성시민','이진우','김승민','김태익',
    '백수진','이영두','유연진','곽경민','김채윤','이상헌',
    '한혜정','이아람','곽효진','백수연','장수빈','이영도','백재현',
    '강정우','양민철','이민영','안유리','권성환','정혜연','강성주','김은형'
]

for name in names:
    cur.execute("""
        SELECT id, name_kr, current_title, current_company, sector
        FROM candidates WHERE name_kr=? AND is_duplicate=0
        ORDER BY total_years DESC
    """, (name,))
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"{r[1]} | {r[0]} | {r[2]} | {r[3]} | {r[4]}")
    else:
        print(f"[NOT FOUND] {name}")
conn.close()
