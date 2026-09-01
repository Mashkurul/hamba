import sqlite3
import hashlib
import os
from config import DATABASE_DIR, DATABASE_FILE
def get_connection():
    """
    Opens and returns a connection to the SQLite database.
    Returns:
        sqlite3.Connection object
    Usage:
        conn = get_connection()
        cursor = conn.cursor()
        ...
        conn.close()
    """
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn
def initialize_database():
    """
    Creates all tables in the database if they do not already exist.
    This is called once when the application starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cows (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            breed           TEXT,
            age             REAL,
            weight          REAL,
            gender          TEXT,
            color           TEXT,
            purchase_date   TEXT,
            status          TEXT    DEFAULT 'Active'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS milk (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cow_id      INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            liters      REAL    NOT NULL,
            session     TEXT,
            notes       TEXT,
            FOREIGN KEY (cow_id) REFERENCES cows(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            food_type   TEXT    NOT NULL,
            quantity_kg REAL    NOT NULL,
            date        TEXT    NOT NULL,
            cow_id      INTEGER,
            notes       TEXT,
            FOREIGN KEY (cow_id) REFERENCES cows(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS health (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cow_id          INTEGER NOT NULL,
            date            TEXT    NOT NULL,
            record_type     TEXT    NOT NULL,
            description     TEXT,
            medicine        TEXT,
            vet_name        TEXT,
            cost            REAL    DEFAULT 0.0,
            FOREIGN KEY (cow_id) REFERENCES cows(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            role        TEXT,
            phone       TEXT,
            salary      REAL    DEFAULT 0.0,
            join_date   TEXT,
            status      TEXT    DEFAULT 'Active'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            status      TEXT    NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            description TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            liters_sold REAL    NOT NULL,
            price_per_liter REAL NOT NULL,
            total_amount    REAL NOT NULL,
            buyer_name  TEXT,
            notes       TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    NOT NULL UNIQUE,
            password     TEXT    NOT NULL,
            role         TEXT    NOT NULL DEFAULT 'worker',
            full_name    TEXT,
            created_by   TEXT    DEFAULT 'system',
            is_active    INTEGER DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            reported_by    TEXT,
            incident_type  TEXT    NOT NULL,
            description    TEXT,
            date           TEXT,
            time           TEXT,
            location       TEXT,
            priority       TEXT    DEFAULT 'Medium',
            status         TEXT    DEFAULT 'Open'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cleaning (
            cleaning_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            cleaner_id     INTEGER,
            area           TEXT    NOT NULL,
            cleaning_type  TEXT    NOT NULL,
            date           TEXT,
            time           TEXT,
            status         TEXT    DEFAULT 'Pending',
            remarks        TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            message      TEXT,
            category     TEXT    DEFAULT 'General',
            priority     TEXT    DEFAULT 'Normal',
            target_role  TEXT    DEFAULT 'all',
            created_by   TEXT    DEFAULT 'system',
            created_at   TEXT,
            is_read      INTEGER DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
    admin_exists = cursor.fetchone()['cnt']
    if admin_exists == 0:
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, created_by)
            VALUES (?, ?, 'admin', 'System Administrator', 'system')
        """, ("admin", default_password))
        print("  [OK] Default admin account created. (user: admin / pass: admin123)")
    conn.commit()
    conn.close()
    print("  [OK] Database initialized successfully.")
if __name__ == "__main__":
    initialize_database()
    print(f"  Database is ready at: {DATABASE_FILE}")
