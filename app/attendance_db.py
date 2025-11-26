from __future__ import annotations
import mysql.connector, hashlib
from typing import Tuple, List, Optional
from datetime import datetime, date

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Poiuytr@1',
    'database': 'attendance'
}

DDL = [
    """CREATE TABLE IF NOT EXISTS users (
        person_id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        role ENUM('admin','student') NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS subjects (
        subject_id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id VARCHAR(255) NOT NULL,
        subject_id VARCHAR(255) NOT NULL,
        ts DATETIME NOT NULL,
        day DATE NOT NULL,
        UNIQUE KEY unique_attendance (person_id, subject_id, day),
        FOREIGN KEY (person_id) REFERENCES users(person_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )""",
    """CREATE TABLE IF NOT EXISTS queries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_id VARCHAR(255) NOT NULL,
        query_text TEXT NOT NULL,
        ts DATETIME NOT NULL,
        status ENUM('pending','resolved') NOT NULL DEFAULT 'pending',
        FOREIGN KEY (person_id) REFERENCES users(person_id)
    )"""
]

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def init_db() -> None:
    conn = get_conn()
    cursor = conn.cursor()
    for stmt in DDL:
        cursor.execute(stmt)
    conn.commit()
    cursor.close()
    conn.close()

def ensure_default_admin() -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    (n,) = cursor.fetchone()
    if n == 0:
        cursor.execute("INSERT INTO users(person_id, name, role, password_hash) VALUES (%s,%s,%s,%s)",
                       ('admin','Administrator','admin', _hash('admin')))
        conn.commit()
    cursor.close()
    conn.close()

# Users / Students
def upsert_student(person_id: str, name: str, password: str = '1234') -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users(person_id, name, role, password_hash) VALUES (%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE name=VALUES(name), role='student'",
        (person_id, name, 'student', _hash(password))
    )
    conn.commit()
    cursor.close()
    conn.close()

def verify_login(person_id: str, password: str) -> Optional[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT person_id, name, role, password_hash FROM users WHERE person_id=%s", (person_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row: return None
    if row[3] == _hash(password):
        return row[:3]  # person_id, name, role
    return None

# Subjects
def add_subject(subject_id: str, name: str) -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subjects(subject_id, name) VALUES (%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name)", (subject_id, name))
    conn.commit()
    cursor.close()
    conn.close()

def list_subjects() -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT subject_id, name FROM subjects ORDER BY subject_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def list_students() -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT person_id, name FROM users WHERE role='student' ORDER BY person_id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Attendance
def mark_attendance(person_id: str, subject_id: str) -> Tuple[bool, str]:
    today = date.today()
    now = datetime.now()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO attendance(person_id, subject_id, ts, day) VALUES (%s,%s,%s,%s)",
                       (person_id, subject_id, now, today))
        conn.commit()
        cursor.close()
        conn.close()
        return True, f"Marked at {now.isoformat()}"
    except mysql.connector.errors.IntegrityError:
        cursor.execute("SELECT ts FROM attendance WHERE person_id=%s AND subject_id=%s AND day=%s",
                       (person_id, subject_id, today))
        row = cursor.fetchone()
        ts = row[0] if row else now
        cursor.close()
        conn.close()
        return False, f"Already marked today at {ts}"

def list_attendance(limit: int = 200) -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT a.id, a.person_id, u.name, a.subject_id, s.name, a.ts, a.day "
        "FROM attendance a "
        "JOIN users u ON a.person_id=u.person_id "
        "JOIN subjects s ON a.subject_id=s.subject_id "
        "ORDER BY a.ts DESC LIMIT %s", (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def list_attendance_by_person(person_id: str) -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT a.subject_id, s.name, a.ts, a.day "
        "FROM attendance a JOIN subjects s ON a.subject_id=s.subject_id "
        "WHERE a.person_id=%s ORDER BY a.ts DESC", (person_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Queries
def insert_query(person_id: str, query_text: str) -> None:
    now = datetime.now()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO queries(person_id, query_text, ts, status) VALUES (%s,%s,%s,%s)",
                   (person_id, query_text, now, 'pending'))
    conn.commit()
    cursor.close()
    conn.close()

def list_queries() -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT q.id, q.person_id, u.name, q.query_text, q.ts, q.status "
        "FROM queries q JOIN users u ON q.person_id=u.person_id "
        "ORDER BY q.ts DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_query_status(query_id: int, status: str) -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE queries SET status=%s WHERE id=%s", (status, query_id))
    conn.commit()
    cursor.close()
    conn.close()

# Profile
def update_student(person_id: str, name: str) -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=%s WHERE person_id=%s", (name, person_id))
    conn.commit()
    cursor.close()
    conn.close()

# Attendance Summary
def get_attendance_summary(person_id: str) -> List[tuple]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT s.subject_id, s.name, COUNT(a.id) as attendance_count "
        "FROM subjects s LEFT JOIN attendance a ON s.subject_id=a.subject_id AND a.person_id=%s "
        "GROUP BY s.subject_id, s.name ORDER BY s.subject_id", (person_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def update_attendance_status(attendance_id: int, new_status: str) -> None:
    """Update or delete attendance record. If new_status is 'absent', delete the record."""
    conn = get_conn()
    cursor = conn.cursor()
    if new_status.lower() == 'absent':
        cursor.execute("DELETE FROM attendance WHERE id=%s", (attendance_id,))
    conn.commit()
    cursor.close()
    conn.close()

def add_manual_attendance(person_id: str, subject_id: str, attendance_date: date) -> Tuple[bool, str]:
    """Manually add attendance for a specific date"""
    now = datetime.now()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO attendance(person_id, subject_id, ts, day) VALUES (%s,%s,%s,%s)",
                       (person_id, subject_id, now, attendance_date))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Attendance added successfully"
    except mysql.connector.errors.IntegrityError:
        cursor.close()
        conn.close()
        return False, "Attendance already exists for this date"

def get_detailed_attendance_stats(person_id: str = None) -> List[tuple]:
    """Get detailed attendance statistics with total days and percentage"""
    conn = get_conn()
    cursor = conn.cursor()
    
    if person_id:
        # For specific student
        cursor.execute("""
            SELECT 
                u.person_id,
                u.name,
                s.subject_id,
                s.name as subject_name,
                COUNT(a.id) as present_days,
                (SELECT COUNT(DISTINCT day) FROM attendance WHERE subject_id = s.subject_id) as total_days
            FROM users u
            CROSS JOIN subjects s
            LEFT JOIN attendance a ON u.person_id = a.person_id AND s.subject_id = a.subject_id
            WHERE u.person_id = %s AND u.role = 'student'
            GROUP BY u.person_id, u.name, s.subject_id, s.name
            ORDER BY s.subject_id
        """, (person_id,))
    else:
        # For all students
        cursor.execute("""
            SELECT 
                u.person_id,
                u.name,
                s.subject_id,
                s.name as subject_name,
                COUNT(a.id) as present_days,
                (SELECT COUNT(DISTINCT day) FROM attendance WHERE subject_id = s.subject_id) as total_days
            FROM users u
            CROSS JOIN subjects s
            LEFT JOIN attendance a ON u.person_id = a.person_id AND s.subject_id = a.subject_id
            WHERE u.role = 'student'
            GROUP BY u.person_id, u.name, s.subject_id, s.name
            ORDER BY u.person_id, s.subject_id
        """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def bulk_import_attendance(attendance_records: List[Tuple[str, str, date]]) -> Tuple[int, int, List[str]]:
    """
    Bulk import attendance records
    Returns: (success_count, duplicate_count, error_messages)
    """
    conn = get_conn()
    cursor = conn.cursor()
    success = 0
    duplicates = 0
    errors = []
    
    for person_id, subject_id, attendance_date in attendance_records:
        try:
            now = datetime.now()
            cursor.execute("INSERT INTO attendance(person_id, subject_id, ts, day) VALUES (%s,%s,%s,%s)",
                          (person_id, subject_id, now, attendance_date))
            conn.commit()
            success += 1
        except mysql.connector.errors.IntegrityError:
            duplicates += 1
        except Exception as e:
            errors.append(f"Error for {person_id}/{subject_id}/{attendance_date}: {str(e)}")
    
    cursor.close()
    conn.close()
    return success, duplicates, errors
