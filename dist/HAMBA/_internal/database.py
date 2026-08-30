# =============================================================
# database.py - Database Setup & Connection Manager
# =============================================================
# This file is responsible for:
#   1. Creating the SQLite database file (if it doesn't exist)
#   2. Creating all required tables (if they don't exist)
#   3. Providing a reusable get_connection() function
#
# Every other module imports get_connection() from here.
# =============================================================

import sqlite3   # Built-in Python library for SQLite
import hashlib   # For hashing passwords securely
import os        # For file/folder path operations

# Import path settings from our config file
from config import DATABASE_DIR, DATABASE_FILE


# ---------------------------------------------------------
# Function: get_connection
# ---------------------------------------------------------
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
    # Make sure the /database folder exists
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)

    # Connect to (or create) the database file
    conn = sqlite3.connect(DATABASE_FILE)

    # This makes rows behave like dictionaries (access by column name)
    conn.row_factory = sqlite3.Row

    return conn


# ---------------------------------------------------------
# Function: initialize_database
# ---------------------------------------------------------
def initialize_database():
    """
    Creates all tables in the database if they do not already exist.
    This is called once when the application starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # Table: cows
    # Stores all information about each cow on the farm
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: milk
    # Records daily milk production per cow
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: food
    # Tracks food stock and daily feeding schedules
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: health
    # Stores medical history, vaccinations, and diseases
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: employees
    # Stores staff/worker information
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: attendance
    # Records daily employee attendance
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            status      TEXT    NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    # --------------------------------------------------
    # Table: expenses
    # Records all farm expenses
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            description TEXT
        )
    """)

    # --------------------------------------------------
    # Table: sales
    # Records milk sales and revenue
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Table: users
    # Stores login credentials for all system users.
    # Passwords are stored as SHA-256 hashes (never plain text).
    # Roles: admin | worker | salesman
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Seed: Create a default admin account if none exists.
    # Default credentials:  admin / admin123
    # The user should change this password after first login.
    # --------------------------------------------------
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
    admin_exists = cursor.fetchone()['cnt']

    if admin_exists == 0:
        # Hash the default password using SHA-256
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, created_by)
            VALUES (?, ?, 'admin', 'System Administrator', 'system')
        """, ("admin", default_password))
        print("  [OK] Default admin account created. (user: admin / pass: admin123)")

    # Save all table creations
    conn.commit()
    conn.close()

    print("  [OK] Database initialized successfully.")


# ---------------------------------------------------------
# Run this file directly to test database creation
# ---------------------------------------------------------
if __name__ == "__main__":
    initialize_database()
    print(f"  Database is ready at: {DATABASE_FILE}")
