"""
SmartFix Database Layer
Supports both MySQL and SQLite seamlessly with automatic fallback.
On Vercel Serverless, safely uses /tmp/smartfix.db when remote MySQL is not set.
"""

import os
import sqlite3
import datetime
from typing import Dict, List, Any, Optional

DATABASE_URL = os.environ.get("DATABASE_URL")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = os.environ.get("MYSQL_DB", "smartfix")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

USE_MYSQL = bool(MYSQL_HOST or (DATABASE_URL and DATABASE_URL.startswith("mysql")))


def get_sqlite_path() -> str:
    # On Vercel serverless, /tmp is the only writable directory
    if os.environ.get("VERCEL"):
        return "/tmp/smartfix.db"
    return os.path.join(os.path.dirname(__file__), "smartfix.db")


def get_connection():
    if USE_MYSQL:
        try:
            import pymysql
            from urllib.parse import urlparse

            if DATABASE_URL:
                parsed = urlparse(DATABASE_URL)
                return pymysql.connect(
                    host=parsed.hostname,
                    user=parsed.username,
                    password=parsed.password,
                    database=parsed.path.lstrip("/"),
                    port=parsed.port or 3306,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
            else:
                return pymysql.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    port=MYSQL_PORT,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
        except Exception as e:
            print(f"[Warning] MySQL connection failed ({e}). Falling back to SQLite.")

    # SQLite Fallback
    db_path = get_sqlite_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    is_sqlite = not (USE_MYSQL and hasattr(cursor, 'fetchall') and not isinstance(conn, sqlite3.Connection))

    if is_sqlite:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            hostel_block TEXT,
            room_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_code TEXT NOT NULL UNIQUE,
            student_id INTEGER,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            hostel_block TEXT NOT NULL,
            room_number TEXT NOT NULL,
            contact_number TEXT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            asset TEXT NOT NULL,
            priority TEXT NOT NULL,
            is_safety_critical INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Submitted',
            assigned_staff_id INTEGER,
            assigned_staff_name TEXT,
            deadline TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT,
            resolution_notes TEXT,
            student_confirmed INTEGER DEFAULT 0,
            student_rating INTEGER DEFAULT 0,
            student_feedback TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            previous_status TEXT,
            new_status TEXT,
            updated_by TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
    else:
        # MySQL syntax
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(30) NOT NULL,
            department VARCHAR(80),
            hostel_block VARCHAR(50),
            room_number VARCHAR(30),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            complaint_code VARCHAR(30) NOT NULL UNIQUE,
            student_id INT,
            student_name VARCHAR(100) NOT NULL,
            student_email VARCHAR(120) NOT NULL,
            hostel_block VARCHAR(50) NOT NULL,
            room_number VARCHAR(30) NOT NULL,
            contact_number VARCHAR(20),
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(60) NOT NULL,
            asset VARCHAR(80) NOT NULL,
            priority VARCHAR(20) NOT NULL,
            is_safety_critical TINYINT(1) DEFAULT 0,
            status VARCHAR(30) DEFAULT 'Submitted',
            assigned_staff_id INT,
            assigned_staff_name VARCHAR(100),
            deadline DATETIME NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME NULL,
            resolution_notes TEXT,
            student_confirmed TINYINT(1) DEFAULT 0,
            student_rating INT DEFAULT 0,
            student_feedback TEXT
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS status_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            complaint_id INT NOT NULL,
            previous_status VARCHAR(30),
            new_status VARCHAR(30),
            updated_by VARCHAR(100),
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

    conn.close()
    seed_default_data()


def seed_default_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Check if users already seeded
    cursor.execute("SELECT COUNT(*) as count FROM users")
    row = cursor.fetchone()
    count = row['count'] if isinstance(row, dict) else row[0]

    if count == 0:
        default_users = [
            ("Rahul Verma", "rahul.verma@college.edu", "student123", "student", "Engineering", "Hostel Block A", "204"),
            ("Priya Sharma", "priya.sharma@college.edu", "student123", "student", "Architecture", "Hostel Block B", "112"),
            ("Arjun Nair", "arjun.nair@college.edu", "student123", "student", "Computer Science", "Hostel Block C", "305"),
            ("Campus Admin", "admin@smartfix.campus", "admin123", "admin", "Estate & Maintenance Office", None, None),
            ("Ramesh Kumar", "ramesh.electrician@smartfix.campus", "staff123", "staff", "Electrical", None, None),
            ("Suresh Patil", "suresh.plumber@smartfix.campus", "staff123", "staff", "Plumbing", None, None),
            ("Mahendra Singh", "mahendra.carpenter@smartfix.campus", "staff123", "staff", "Furniture & Carpentry", None, None),
            ("Ankit Verma", "ankit.it@smartfix.campus", "staff123", "staff", "IT & Classroom Equipment", None, None),
            ("Vikram Rathore", "vikram.civil@smartfix.campus", "staff123", "staff", "Hostel Infrastructure & Safety", None, None)
        ]

        for u in default_users:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, department, hostel_block, room_number) VALUES (?, ?, ?, ?, ?, ?, ?)"
                if isinstance(conn, sqlite3.Connection) else
                "INSERT INTO users (name, email, password_hash, role, department, hostel_block, room_number) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                u
            )

        # Seed realistic sample complaints
        now = datetime.datetime.now()
        urgent_deadline = (now + datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
        overdue_deadline = (now - datetime.timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S")
        future_deadline = (now + datetime.timedelta(hours=36)).strftime("%Y-%m-%d %H:%M:%S")
        resolved_deadline = (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

        sample_complaints = [
            (
                "FIX-2026-001", 1, "Rahul Verma", "rahul.verma@college.edu", "Hostel Block A", "204", "+91 9876543210",
                "Sparks and burning smell from ceiling fan switchboard",
                "Sparks are shooting out whenever I try to switch on the ceiling fan socket. There is a strong burning wire odor in the room.",
                "Safety & Hazard", "Switchboard / Socket", "Emergency", 1, "In Progress", 5, "Ramesh Kumar",
                urgent_deadline, now.strftime("%Y-%m-%d %H:%M:%S"), None, "Inspected by Ramesh. Faulty wiring isolated; replacing the internal fuse and socket switch board.", 0, 0, None
            ),
            (
                "FIX-2026-002", 2, "Priya Sharma", "priya.sharma@college.edu", "Hostel Block B", "112", "+91 9812345678",
                "Washbasin drain pipe ruptured and water flooding washroom floor",
                "The washbasin drain pipe underneath is cracked and dirty water is overflowing all over the washroom floor.",
                "Plumbing", "Washbasin / Sink", "High", 0, "Assigned", 6, "Suresh Patil",
                overdue_deadline, (now - datetime.timedelta(hours=28)).strftime("%Y-%m-%d %H:%M:%S"), None, None, 0, 0, None
            ),
            (
                "FIX-2026-003", 3, "Arjun Nair", "arjun.nair@college.edu", "Hostel Block C", "305", "+91 9955443322",
                "Hostel study chair wheel broken and backrest loose",
                "The castor wheel of the revolving study chair is completely broken off, and the backrest support screws are loose.",
                "Furniture", "Chair", "Medium", 0, "Submitted", None, None,
                future_deadline, now.strftime("%Y-%m-%d %H:%M:%S"), None, None, 0, 0, None
            ),
            (
                "FIX-2026-004", 1, "Rahul Verma", "rahul.verma@college.edu", "Hostel Block A", "204", "+91 9876543210",
                "Hostel bathroom geyser not heating water",
                "Geyser is turning on with red indicator light but water remains ice cold even after waiting 30 minutes.",
                "Electrical", "Geyser / Water Heater", "Medium", 0, "Resolved", 5, "Ramesh Kumar",
                resolved_deadline, (now - datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "Replaced defective heating element rod and thermostat. Tested hot water output at 55 deg C.", 1, 5, "Excellent service, repaired on the same day!"
            )
        ]

        query = (
            """INSERT INTO complaints (
                complaint_code, student_id, student_name, student_email, hostel_block, room_number,
                contact_number, title, description, category, asset, priority, is_safety_critical,
                status, assigned_staff_id, assigned_staff_name, deadline, created_at, resolved_at,
                resolution_notes, student_confirmed, student_rating, student_feedback
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            if isinstance(conn, sqlite3.Connection) else
            """INSERT INTO complaints (
                complaint_code, student_id, student_name, student_email, hostel_block, room_number,
                contact_number, title, description, category, asset, priority, is_safety_critical,
                status, assigned_staff_id, assigned_staff_name, deadline, created_at, resolved_at,
                resolution_notes, student_confirmed, student_rating, student_feedback
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        )

        for c in sample_complaints:
            cursor.execute(query, c)

        if isinstance(conn, sqlite3.Connection):
            conn.commit()

    conn.close()


def row_to_dict(row) -> Dict[str, Any]:
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    return dict(row)


def rows_to_list(rows) -> List[Dict[str, Any]]:
    return [row_to_dict(r) for r in rows]


def get_all_users() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, department, hostel_block, room_number FROM users ORDER BY role, name")
    rows = cursor.fetchall()
    conn.close()
    return rows_to_list(rows)


def get_staff_members() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, department FROM users WHERE role = 'staff' ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows_to_list(rows)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    param = (user_id,)
    cursor.execute(
        "SELECT id, name, email, role, department, hostel_block, room_number FROM users WHERE id = ?"
        if isinstance(conn, sqlite3.Connection) else
        "SELECT id, name, email, role, department, hostel_block, room_number FROM users WHERE id = %s",
        param
    )
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def get_complaints(role: str = 'admin', user_id: Optional[int] = None, filter_status: Optional[str] = None, filter_category: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    sql = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if role == 'student' and user_id:
        sql += " AND student_id = ?" if is_sqlite else " AND student_id = %s"
        params.append(user_id)
    elif role == 'staff' and user_id:
        sql += " AND assigned_staff_id = ?" if is_sqlite else " AND assigned_staff_id = %s"
        params.append(user_id)

    if filter_status and filter_status != 'All':
        sql += " AND status = ?" if is_sqlite else " AND status = %s"
        params.append(filter_status)

    if filter_category and filter_category != 'All':
        sql += " AND category = ?" if is_sqlite else " AND category = %s"
        params.append(filter_category)

    if search and search.strip():
        term = f"%{search.strip()}%"
        sql += " AND (title LIKE ? OR description LIKE ? OR complaint_code LIKE ? OR asset LIKE ?)" if is_sqlite else " AND (title LIKE %s OR description LIKE %s OR complaint_code LIKE %s OR asset LIKE %s)"
        params.extend([term, term, term, term])

    sql += " ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, created_at DESC"

    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    complaints = rows_to_list(rows)

    # Compute SLA deadline status dynamically
    now = datetime.datetime.now()
    for c in complaints:
        c['is_overdue'] = False
        c['time_remaining_str'] = "No deadline"
        deadline_str = c.get('deadline')
        if deadline_str and c.get('status') not in ['Resolved', 'Closed']:
            try:
                # Handle possible microsecond string or standard format
                clean_deadline_str = str(deadline_str).split('.')[0]
                dl = datetime.datetime.strptime(clean_deadline_str, "%Y-%m-%d %H:%M:%S")
                diff = dl - now
                if diff.total_seconds() < 0:
                    c['is_overdue'] = True
                    overdue_hrs = int(abs(diff.total_seconds()) // 3600)
                    c['time_remaining_str'] = f"Overdue by {overdue_hrs}h"
                else:
                    hours = int(diff.total_seconds() // 3600)
                    minutes = int((diff.total_seconds() % 3600) // 60)
                    c['time_remaining_str'] = f"{hours}h {minutes}m remaining"
            except Exception:
                c['time_remaining_str'] = str(deadline_str)
        elif c.get('status') in ['Resolved', 'Closed']:
            c['time_remaining_str'] = "Completed"

    conn.close()
    return complaints


def get_complaint_by_id(cid: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM complaints WHERE id = ?"
        if isinstance(conn, sqlite3.Connection) else
        "SELECT * FROM complaints WHERE id = %s",
        (cid,)
    )
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def create_complaint(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    # Generate unique complaint code like FIX-2026-782
    import random
    code = f"FIX-2026-{random.randint(100, 999)}"

    now = datetime.datetime.now()
    sla_hours = int(data.get('sla_hours', 48))
    deadline = (now + datetime.timedelta(hours=sla_hours)).strftime("%Y-%m-%d %H:%M:%S")

    query = (
        """INSERT INTO complaints (
            complaint_code, student_id, student_name, student_email, hostel_block, room_number,
            contact_number, title, description, category, asset, priority, is_safety_critical,
            status, deadline, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, ?)"""
        if is_sqlite else
        """INSERT INTO complaints (
            complaint_code, student_id, student_name, student_email, hostel_block, room_number,
            contact_number, title, description, category, asset, priority, is_safety_critical,
            status, deadline, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Submitted', %s, %s)"""
    )

    values = (
        code,
        data.get('student_id', 1),
        data.get('student_name', 'Rahul Verma'),
        data.get('student_email', 'rahul.verma@college.edu'),
        data.get('hostel_block', 'Hostel Block A'),
        data.get('room_number', '101'),
        data.get('contact_number', ''),
        data.get('title', 'Maintenance Issue'),
        data.get('description', ''),
        data.get('category', 'Hostel Infrastructure'),
        data.get('asset', 'General Facility'),
        data.get('priority', 'Medium'),
        1 if data.get('is_safety_critical') else 0,
        deadline,
        now.strftime("%Y-%m-%d %H:%M:%S")
    )

    cursor.execute(query, values)
    new_id = cursor.lastrowid
    if is_sqlite:
        conn.commit()

    # Log initial status
    log_query = (
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (?, NULL, 'Submitted', ?, ?)"
        if is_sqlite else
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (%s, NULL, 'Submitted', %s, %s)"
    )
    cursor.execute(log_query, (new_id, data.get('student_name', 'Student'), "Complaint submitted through SmartFix NLP portal."))
    if is_sqlite:
        conn.commit()

    conn.close()
    return get_complaint_by_id(new_id)


def assign_complaint(cid: int, staff_id: int, staff_name: str, admin_name: str = "Admin") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    query = (
        "UPDATE complaints SET assigned_staff_id = ?, assigned_staff_name = ?, status = 'Assigned' WHERE id = ?"
        if is_sqlite else
        "UPDATE complaints SET assigned_staff_id = %s, assigned_staff_name = %s, status = 'Assigned' WHERE id = %s"
    )
    cursor.execute(query, (staff_id, staff_name, cid))

    log_query = (
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (?, 'Submitted', 'Assigned', ?, ?)"
        if is_sqlite else
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (%s, 'Submitted', 'Assigned', %s, %s)"
    )
    cursor.execute(log_query, (cid, admin_name, f"Assigned to {staff_name} for repair and site inspection."))

    if is_sqlite:
        conn.commit()
    conn.close()
    return True


def update_complaint_status(cid: int, new_status: str, updated_by: str, notes: Optional[str] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    prev_c = get_complaint_by_id(cid)
    prev_status = prev_c['status'] if prev_c else 'Submitted'

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if new_status in ['Resolved', 'Closed']:
        query = (
            "UPDATE complaints SET status = ?, resolution_notes = ?, resolved_at = ? WHERE id = ?"
            if is_sqlite else
            "UPDATE complaints SET status = %s, resolution_notes = %s, resolved_at = %s WHERE id = %s"
        )
        cursor.execute(query, (new_status, notes or "Marked as resolved by maintenance team.", now_str, cid))
    else:
        query = (
            "UPDATE complaints SET status = ?, resolution_notes = COALESCE(?, resolution_notes) WHERE id = ?"
            if is_sqlite else
            "UPDATE complaints SET status = %s, resolution_notes = COALESCE(%s, resolution_notes) WHERE id = %s"
        )
        cursor.execute(query, (new_status, notes, cid))

    log_query = (
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (?, ?, ?, ?, ?)"
        if is_sqlite else
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (%s, %s, %s, %s, %s)"
    )
    cursor.execute(log_query, (cid, prev_status, new_status, updated_by, notes or f"Status changed to {new_status}."))

    if is_sqlite:
        conn.commit()
    conn.close()
    return True


def confirm_resolution(cid: int, rating: int, feedback: str, student_name: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    query = (
        "UPDATE complaints SET status = 'Closed', student_confirmed = 1, student_rating = ?, student_feedback = ? WHERE id = ?"
        if is_sqlite else
        "UPDATE complaints SET status = 'Closed', student_confirmed = 1, student_rating = %s, student_feedback = %s WHERE id = %s"
    )
    cursor.execute(query, (rating, feedback, cid))

    log_query = (
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (?, 'Resolved', 'Closed', ?, ?)"
        if is_sqlite else
        "INSERT INTO status_logs (complaint_id, previous_status, new_status, updated_by, notes) VALUES (%s, 'Resolved', 'Closed', %s, %s)"
    )
    cursor.execute(log_query, (cid, student_name, f"Student confirmed fix. Rating: {rating}/5 stars. Feedback: '{feedback}'"))

    if is_sqlite:
        conn.commit()
    conn.close()
    return True


def get_complaint_logs(cid: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection)

    query = (
        "SELECT * FROM status_logs WHERE complaint_id = ? ORDER BY created_at ASC"
        if is_sqlite else
        "SELECT * FROM status_logs WHERE complaint_id = %s ORDER BY created_at ASC"
    )
    cursor.execute(query, (cid,))
    rows = cursor.fetchall()
    conn.close()
    return rows_to_list(rows)


def get_dashboard_analytics() -> Dict[str, Any]:
    all_complaints = get_complaints(role='admin')

    total = len(all_complaints)
    submitted = sum(1 for c in all_complaints if c['status'] == 'Submitted')
    assigned = sum(1 for c in all_complaints if c['status'] == 'Assigned')
    in_progress = sum(1 for c in all_complaints if c['status'] == 'In Progress')
    resolved = sum(1 for c in all_complaints if c['status'] in ['Resolved', 'Closed'])
    urgent_critical = sum(1 for c in all_complaints if c['priority'] == 'Emergency' or c.get('is_safety_critical'))
    overdue = sum(1 for c in all_complaints if c.get('is_overdue'))

    # Category distribution
    categories: Dict[str, int] = {}
    for c in all_complaints:
        cat = c['category']
        categories[cat] = categories.get(cat, 0) + 1

    # Priority distribution
    priorities = {
        'Emergency': sum(1 for c in all_complaints if c['priority'] == 'Emergency'),
        'High': sum(1 for c in all_complaints if c['priority'] == 'High'),
        'Medium': sum(1 for c in all_complaints if c['priority'] == 'Medium'),
        'Low': sum(1 for c in all_complaints if c['priority'] == 'Low')
    }

    return {
        "total": total,
        "submitted": submitted,
        "assigned": assigned,
        "in_progress": in_progress,
        "resolved": resolved,
        "urgent_critical": urgent_critical,
        "overdue": overdue,
        "categories": categories,
        "priorities": priorities,
        "resolution_rate": round((resolved / total * 100) if total > 0 else 0, 1)
    }
