import hashlib
from database import get_connection
from config import print_header, print_line, USER_ROLES
def hash_password(plain_text: str) -> str:
    """
    Converts a plain-text password into a SHA-256 hash string.
    Example: "admin123" → "240be518..."
    This is a one-way operation — you can't reverse it.
    """
    return hashlib.sha256(plain_text.encode()).hexdigest()
def login() -> dict | None:
    """
    Prompts the user for username and password.
    Returns the user row (as dict) if successful, None if failed.
    The returned dict contains:
        id, username, role, full_name, is_active
    """
    print_header("HAMBAA – LOGIN")
    print("  Please log in to continue.\n")
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        username = input("  Username : ").strip()
        password = input("  Password : ").strip()
        if not username or not password:
            print("  [!] Username and password cannot be empty.\n")
            attempts += 1
            continue
        hashed = hash_password(password)
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, role, full_name, is_active
                FROM users
                WHERE username = ? AND password = ?
            """, (username, hashed))
            user = cursor.fetchone()
            conn.close()
            if user is None:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"  [!] Invalid username or password. "
                      f"{remaining} attempt(s) remaining.\n")
                continue
            if user['is_active'] == 0:
                print("  [!] Your account has been deactivated. Contact the admin.\n")
                return None
            print(f"\n  Welcome, {user['full_name'] or user['username']}!")
            print(f"  Role: {user['role'].upper()}")
            print_line()
            return dict(user)
        except Exception as e:
            print(f"  [ERROR]: {e}")
            return None
    print("  [!] Too many failed attempts. Access denied.")
    return None
def create_user(current_user: dict):
    """
    Allows the admin to create a new user account.
    Roles: worker, salesman, watchman, cleaner, farm_owner.
    Only callable if current_user['role'] == 'admin'.
    """
    if current_user['role'] != 'admin':
        print("\n  [!] Access Denied. Only admins can create user accounts.")
        return
    print_header("CREATE USER ACCOUNT")
    username = input("  Username     : ").strip()
    if not username:
        print("  [!] Username cannot be empty.")
        return
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print(f"  [!] Username '{username}' already exists.")
        conn.close()
        return
    full_name = input("  Full Name    : ").strip()
    allowed_roles = ["worker", "salesman", "watchman", "cleaner", "farm_owner"]
    print("\n  Assign Role:")
    for i, role in enumerate(allowed_roles, 1):
        print(f"    {i}. {role.replace('_', ' ').title()}")
    while True:
        choice = input(f"  Select role (1-{len(allowed_roles)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(allowed_roles):
            role = allowed_roles[int(choice) - 1]
            break
        print("  [!] Invalid choice.")
    while True:
        password = input("  Set Password : ").strip()
        if len(password) < 4:
            print("  [!] Password must be at least 4 characters.")
            continue
        confirm = input("  Confirm Pass : ").strip()
        if password != confirm:
            print("  [!] Passwords do not match. Try again.")
            continue
        break
    hashed_password = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hashed_password, role, full_name, current_user['username']))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        print(f"\n  [OK] User '{username}' ({role}) created successfully! (ID: {new_id})")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def view_users(current_user: dict):
    """Display all registered users. Admin only."""
    if current_user['role'] != 'admin':
        print("\n  [!] Access Denied.")
        return
    print_header("ALL SYSTEM USERS")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username, full_name, role, created_by, is_active
            FROM users ORDER BY id
        """)
        users = cursor.fetchall()
        conn.close()
        if not users:
            print("  No users found.")
            return
        print(f"  {'ID':<5} {'Username':<15} {'Full Name':<20} {'Role':<12} {'Active':<8} {'Created By'}")
        print_line("-")
        for u in users:
            active_str = "Yes" if u['is_active'] else "No"
            print(f"  {u['id']:<5} {u['username']:<15} "
                  f"{(u['full_name'] or ''):<20} "
                  f"{u['role']:<12} {active_str:<8} {u['created_by']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def deactivate_user(current_user: dict):
    """Deactivate a user account so they can no longer log in."""
    if current_user['role'] != 'admin':
        print("\n  [!] Access Denied.")
        return
    print_header("DEACTIVATE USER")
    user_id = input("  Enter User ID to deactivate: ").strip()
    if not user_id.isdigit():
        print("  [!] Invalid ID.")
        return
    if int(user_id) == current_user['id']:
        print("  [!] You cannot deactivate your own account.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id),))
        user = cursor.fetchone()
        if not user:
            print(f"  [!] No user found with ID {user_id}.")
            conn.close()
            return
        if user['is_active'] == 0:
            print(f"  [!] User '{user['username']}' is already deactivated.")
            conn.close()
            return
        confirm = input(f"  Deactivate '{user['username']}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  [!] Cancelled.")
            conn.close()
            return
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (int(user_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] User '{user['username']}' has been deactivated.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def reactivate_user(current_user: dict):
    """Re-enable a previously deactivated user account."""
    if current_user['role'] != 'admin':
        print("\n  [!] Access Denied.")
        return
    print_header("REACTIVATE USER")
    user_id = input("  Enter User ID to reactivate: ").strip()
    if not user_id.isdigit():
        print("  [!] Invalid ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (int(user_id),))
        user = cursor.fetchone()
        if not user:
            print(f"  [!] No user found with ID {user_id}.")
            conn.close()
            return
        cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (int(user_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] User '{user['username']}' has been reactivated.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def change_password(current_user: dict):
    """Allows any user to change their own password."""
    print_header("CHANGE PASSWORD")
    old_pass = input("  Current Password : ").strip()
    hashed_old = hash_password(old_pass)
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE id = ? AND password = ?",
            (current_user['id'], hashed_old)
        )
        if not cursor.fetchone():
            print("  [!] Current password is incorrect.")
            conn.close()
            return
        while True:
            new_pass = input("  New Password     : ").strip()
            if len(new_pass) < 4:
                print("  [!] Password must be at least 4 characters.")
                continue
            confirm = input("  Confirm Password : ").strip()
            if new_pass != confirm:
                print("  [!] Passwords do not match.")
                continue
            break
        hashed_new = hash_password(new_pass)
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hashed_new, current_user['id'])
        )
        conn.commit()
        conn.close()
        print("\n  [OK] Password changed successfully!")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def user_management_menu(current_user: dict):
    """Admin-only menu for managing system users."""
    while True:
        print_header("USER MANAGEMENT")
        print("  1. Create New User (Worker / Salesman)")
        print("  2. View All Users")
        print("  3. Deactivate User")
        print("  4. Reactivate User")
        print("  0. Back")
        print_line()
        choice = input("  Select option: ").strip()
        if   choice == "1": create_user(current_user)
        elif choice == "2": view_users(current_user)
        elif choice == "3": deactivate_user(current_user)
        elif choice == "4": reactivate_user(current_user)
        elif choice == "0": break
        else: print("  [!] Invalid option.")
