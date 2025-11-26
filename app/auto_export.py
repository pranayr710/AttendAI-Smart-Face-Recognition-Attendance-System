import mysql.connector, pandas as pd
from .attendance_db import DB_CONFIG
from .config import AUTO_EXPORT_MASTER, AUTO_EXPORT_DAILY

def export_master():
    conn = mysql.connector.connect(**DB_CONFIG)
    df = pd.read_sql_query(
        """
        SELECT a.id, a.person_id, u.name AS person_name, a.subject_id, s.name AS subject_name, DATE_FORMAT(a.ts, '%Y-%m-%d %H:%i:%s') AS ts, DATE_FORMAT(a.day, '%Y-%m-%d') AS day
        FROM attendance a
        JOIN users u ON a.person_id = u.person_id
        JOIN subjects s ON a.subject_id = s.subject_id
        ORDER BY a.ts DESC
        """, conn)
    df.to_csv(str(AUTO_EXPORT_MASTER), index=False)
    conn.close()

def export_daily():
    conn = mysql.connector.connect(**DB_CONFIG)
    df = pd.read_sql_query(
        """
        SELECT a.person_id, u.name AS person_name, a.subject_id, s.name AS subject_name, DATE_FORMAT(a.day, '%Y-%m-%d') AS day, DATE_FORMAT(MIN(a.ts), '%Y-%m-%d %H:%i:%s') AS first_mark
        FROM attendance a
        JOIN users u ON a.person_id = u.person_id
        JOIN subjects s ON a.subject_id = s.subject_id
        GROUP BY a.person_id, a.subject_id, a.day
        ORDER BY a.day DESC, a.person_id
        """, conn)
    df.to_csv(str(AUTO_EXPORT_DAILY), index=False)
    conn.close()

def export_all():
    export_master()
    export_daily()
