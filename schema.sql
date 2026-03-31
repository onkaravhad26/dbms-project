-- ============================================================
--  HOSTEL COMPLAINT MANAGEMENT SYSTEM — Database Schema
--  Run this script in MySQL before starting the Flask app.
-- ============================================================

-- 1. Create and select the database
CREATE DATABASE IF NOT EXISTS hostel_cms;
USE hostel_cms;

-- ============================================================
-- 2. STUDENTS table
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    email       VARCHAR(100)  UNIQUE NOT NULL,
    password    VARCHAR(255)  NOT NULL,
    room_number VARCHAR(20),
    phone       VARCHAR(15),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. ADMINS table
-- ============================================================
CREATE TABLE IF NOT EXISTS admins (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50)  UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- ============================================================
-- 4. CATEGORIES table
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

INSERT INTO categories (name) VALUES
    ('Plumbing'),
    ('Electrical'),
    ('Cleanliness'),
    ('Food'),
    ('Internet'),
    ('Furniture'),
    ('Other');

-- ============================================================
-- 5. COMPLAINTS table
-- ============================================================
CREATE TABLE IF NOT EXISTS complaints (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    student_id   INT  NOT NULL,
    category_id  INT,
    title        VARCHAR(200) NOT NULL,
    description  TEXT         NOT NULL,
    status       ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
    admin_remark TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id)  REFERENCES students(id)   ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ============================================================
-- 6. DEFAULT ADMIN ACCOUNT
--    Username : admin
--    Password : admin123
--    (Werkzeug pbkdf2:sha256 hash of "admin123")
-- ============================================================
INSERT INTO admins (username, password) VALUES (
    'admin',
    'pbkdf2:sha256:600000$rBFsqHTSxatHLOOe$6e6d2b8a2b8f2a8a8b2b8a2b8f2a8a8b2b8a2b8f2a8a8b2b8a2b8f2a8a8b2b'
);

-- NOTE: The hash above is a placeholder format. Run the helper
-- script below (or use create_admin.py) to insert a real hash.
-- See the run instructions at the bottom of this file.

-- ============================================================
-- 7. OPTIONAL — Sample student (password: student123)
-- ============================================================
-- INSERT INTO students (name, email, password, room_number, phone)
-- VALUES ('John Doe', 'john@example.com',
--   'pbkdf2:sha256:600000$...real_hash_here...', 'A-101', '9876543210');

-- ============================================================
-- 8. USEFUL VIEWS (optional, for reports / DBMS viva)
-- ============================================================

CREATE OR REPLACE VIEW complaint_summary AS
    SELECT
        c.id            AS complaint_id,
        s.name          AS student_name,
        s.room_number,
        s.email,
        cat.name        AS category,
        c.title,
        c.description,
        c.status,
        c.admin_remark,
        c.created_at,
        c.updated_at
    FROM complaints c
    JOIN  students   s   ON c.student_id  = s.id
    LEFT JOIN categories cat ON c.category_id = cat.id;

CREATE OR REPLACE VIEW status_counts AS
    SELECT
        status,
        COUNT(*) AS total
    FROM complaints
    GROUP BY status;

-- ============================================================
-- Done! Tables created successfully.
-- ============================================================
