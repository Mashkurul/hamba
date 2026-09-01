import os
APP_NAME    = "HAMBAA"
APP_TITLE   = "HAMBAA – AI Based Cow Management System"
APP_VERSION = "1.0.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR  = os.path.join(BASE_DIR, "database")
DATABASE_FILE = os.path.join(DATABASE_DIR, "hamba.db")
LINE_WIDTH = 50
LINE_CHAR  = "="
LINE_CHAR2 = "-"
COW_STATUS_OPTIONS = ["Active", "Sold", "Dead", "Sick"]
GENDER_OPTIONS = ["Female", "Male"]
EMPLOYEE_ROLES = ["Farmer", "Veterinarian", "Manager", "Cleaner", "Guard"]
ATTENDANCE_STATUS = ["Present", "Absent", "Leave"]
EXPENSE_CATEGORIES = ["Feed", "Medicine", "Salary", "Equipment", "Other"]
FOOD_TYPES = ["Hay", "Grass", "Silage", "Concentrate", "Grain", "Mineral", "Other"]
USER_ROLES = ["admin", "worker", "salesman", "watchman", "cleaner", "farm_owner"]
ROLE_PERMISSIONS = {
    "admin":      {"1", "2", "3", "4", "5", "6", "7", "8"},
    "worker":     {"1", "2", "3", "4", "8"},
    "salesman":   {"2", "6", "7"},
    "watchman":   {"1", "2", "8"},
    "cleaner":    {"1", "2", "8"},
    "farm_owner": {"1", "2", "3", "4", "5", "6", "7", "8"},
}
INCIDENT_TYPES = [
    "Theft", "Unauthorized Visitor", "Animal Missing",
    "Equipment Damage", "Fire", "Power Failure",
    "Suspicious Activity", "Other",
]
INCIDENT_PRIORITY = ["Low", "Medium", "High", "Critical"]
INCIDENT_STATUS   = ["Open", "In Progress", "Resolved", "Closed"]
CLEANING_AREAS = [
    "Cow Shed", "Feeding Area", "Milking Area", "Storage Room",
    "Water Area", "Medical Area", "Equipment Area", "Waste Disposal Area",
]
CLEANING_TYPES = [
    "General Cleaning", "Disinfection", "Waste Removal",
    "Water Area Cleaning", "Feeding Area Cleaning", "Milking Area Cleaning",
]
CLEANING_STATUS = ["Pending", "In Progress", "Completed"]
NOTIFICATION_CATEGORIES = ["General", "Security", "Health", "Maintenance", "Feed", "Finance"]
NOTIFICATION_PRIORITY   = ["Normal", "Important", "Emergency", "Critical"]
def print_line(char=LINE_CHAR):
    """Print a separator line of LINE_WIDTH characters."""
    print(char * LINE_WIDTH)
def print_header(title):
    """Print a formatted section header."""
    print_line()
    print(f"  {title}")
    print_line()
