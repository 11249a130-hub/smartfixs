-- SmartFix Campus Maintenance Database Schema
-- Compatible with MySQL 5.7+ / 8.0+ and SQLite 3

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL, -- 'student', 'admin', 'staff'
    department VARCHAR(80),
    hostel_block VARCHAR(50),
    room_number VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_code VARCHAR(30) NOT NULL UNIQUE,
    student_id INTEGER,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(120) NOT NULL,
    hostel_block VARCHAR(50) NOT NULL,
    room_number VARCHAR(30) NOT NULL,
    contact_number VARCHAR(20),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(60) NOT NULL,
    asset VARCHAR(80) NOT NULL,
    priority VARCHAR(20) NOT NULL, -- 'Emergency', 'High', 'Medium', 'Low'
    is_safety_critical BOOLEAN DEFAULT 0,
    status VARCHAR(30) DEFAULT 'Submitted', -- 'Submitted', 'Assigned', 'In Progress', 'Resolved', 'Closed'
    assigned_staff_id INTEGER,
    assigned_staff_name VARCHAR(100),
    deadline TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    student_confirmed BOOLEAN DEFAULT 0,
    student_rating INTEGER DEFAULT 0,
    student_feedback TEXT
);

CREATE TABLE IF NOT EXISTS status_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    previous_status VARCHAR(30),
    new_status VARCHAR(30),
    updated_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
