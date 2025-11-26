import argparse, sqlite3, pandas as pd
from .config import SQLITE_PATH

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, help="Output CSV")
    p.add_argument("--subject-id", help="Filter by subject")
    p.add_argument("--person-id", help="Filter by person")
    args = p.parse_args()

    con = sqlite3.connect(SQLITE_PATH)
    base = (            "SELECT a.id, a.person_id, u.name AS person_name, a.subject_id, s.name AS subject_name, a.ts, a.day "            "FROM attendance a "            "JOIN users u ON a.person_id=u.person_id "            "JOIN subjects s ON a.subject_id=s.subject_id "        )
    where = []
    params = []
    if args.subject_id:
        where.append("a.subject_id=?"); params.append(args.subject_id)
    if args.person_id:
        where.append("a.person_id=?"); params.append(args.person_id)
    if where:
        base += "WHERE " + " AND ".join(where) + " "
    base += "ORDER BY a.ts DESC"

    df = pd.read_sql_query(base, con, params=params)
    df.to_csv(args.out, index=False)
    print(f"[OK] Exported {len(df)} rows to {args.out}")

if __name__ == "__main__":
    main()
