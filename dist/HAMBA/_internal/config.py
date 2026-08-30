# =============================================================
# config.py - Global Configuration for HAMBA System
# =============================================================
# This file stores all the constants and settings used
# throughout the entire HAMBA project.
# Any module can import from here to avoid hardcoding values.
# =============================================================

import os

# ---------------------------------------------------------
# Application Info
# ---------------------------------------------------------
APP_NAME    = "HAMBA"
APP_TITLE   = "HAMBA – AI Based Cow Management System"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "University Project"

# ---------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------
# Get the directory where this config.py file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the database folder and file
DATABASE_DIR  = os.path.join(BASE_DIR, "database")
DATABASE_FILE = os.path.join(DATABASE_DIR, "hamba.db")

# ---------------------------------------------------------
# Display / UI Settings
# ---------------------------------------------------------
# Width of the separator line in the terminal
LINE_WIDTH = 50

# Separator characters
LINE_CHAR  = "="   # used for headers
LINE_CHAR2 = "-"   # used for sub-sections

# ---------------------------------------------------------
# Status Options for Cows
# ---------------------------------------------------------
COW_STATUS_OPTIONS = ["Active", "Sold", "Dead", "Sick"]

# ---------------------------------------------------------
# Gender Options
# ---------------------------------------------------------
GENDER_OPTIONS = ["Female", "Male"]

# ---------------------------------------------------------
# Employee Roles
# ---------------------------------------------------------
EMPLOYEE_ROLES = ["Farmer", "Veterinarian", "Manager", "Cleaner", "Guard"]

# ---------------------------------------------------------
# Attendance Status
# ---------------------------------------------------------
ATTENDANCE_STATUS = ["Present", "Absent", "Leave"]

# ---------------------------------------------------------
# Expense Categories
# ---------------------------------------------------------
EXPENSE_CATEGORIES = ["Feed", "Medicine", "Salary", "Equipment", "Other"]

# ---------------------------------------------------------
# Food Types
# ---------------------------------------------------------
FOOD_TYPES = ["Hay", "Grass", "Silage", "Concentrate", "Grain", "Mineral", "Other"]

# ---------------------------------------------------------
# User Roles
# ---------------------------------------------------------
# Admin   : Full access to everything, can create users
# Worker  : Can manage cows, milk, food, health
# Salesman: Can only access milk sales and expense/sales
USER_ROLES = ["admin", "worker", "salesman"]

# Permissions per role — list of menu option numbers allowed
# Maps role name → set of allowed menu choices
ROLE_PERMISSIONS = {
    "admin": {"1", "2", "3", "4", "5", "6", "7", "8"},   # full access
    "worker": {"1", "2", "3", "4", "8"},                  # cows, milk, food, health, AI
    "salesman": {"2", "6", "7"},                          # milk, sales, reports
}

# ---------------------------------------------------------
# Helper: Print a full-width separator line
# ---------------------------------------------------------
def print_line(char=LINE_CHAR):
    """Print a separator line of LINE_WIDTH characters."""
    print(char * LINE_WIDTH)

# ---------------------------------------------------------
# Helper: Print a centered title inside separator lines
# ---------------------------------------------------------
def print_header(title):
    """Print a formatted section header."""
    print_line()
    print(f"  {title}")
    print_line()
