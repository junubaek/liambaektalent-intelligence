import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # Get column names
    cur.execute("PRAGMA table_info(candidates)")
    cols = [c[1] for c in cur.fetchall()]
    print("Table columns:", cols)

    # We will search for any column that resembles filename/file/path
    file_cols = [c for c in cols if 'file' in c.lower() or 'path' in c.lower() or 'source' in c.lower()]
    print("Potential file columns:", file_cols)

    query_cols = ['id', 'name_kr'] + file_cols
    query_str = ", ".join(query_cols)

    cur.execute(f"SELECT {query_str} FROM candidates WHERE id IN ('bb55fc1a-c237-433e-9ef6-e79584cbb347', '83fd1454-3319-49d4-9b02-72de5fa65487')")
    for r in cur.fetchall():
        print(f"\n{r[1]} ({r[0]}):")
        for col, val in zip(file_cols, r[2:]):
            print(f"  {col}: {val}")

    conn.close()

if __name__ == '__main__':
    main()
