import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import initialize_database
from config   import print_header, print_line, APP_TITLE, APP_VERSION, ROLE_PERMISSIONS
from modules.auth import login, change_password, user_management_menu
from modules.cow_management      import cow_menu
from modules.milk_management     import milk_menu
from modules.food_management     import food_menu
from modules.health_management   import health_menu
from modules.employee_management import employee_menu
from modules.expense_management  import expense_menu
from modules.reports             import reports_menu
from modules.ai_assistant        import ai_menu
def show_banner():
    """Prints the welcome/splash screen."""
    os.system("cls" if os.name == "nt" else "clear")
    print_line()
    print(f"  {APP_TITLE}")
    print(f"  Version  : {APP_VERSION}")
    print_line()
    print()
def get_menu_items(role: str) -> list:
    """
    Returns a list of (option_number, label, function) tuples
    that the current role is allowed to see.
    """
    all_items = [
        ("1", "Cow Management",      cow_menu),
        ("2", "Milk Management",     milk_menu),
        ("3", "Food Management",     food_menu),
        ("4", "Health & Medicine",   health_menu),
        ("5", "Employee Management", employee_menu),
        ("6", "Expense & Sales",     expense_menu),
        ("7", "Reports",             reports_menu),
        ("8", "AI Assistant",        ai_menu),
    ]
    allowed = ROLE_PERMISSIONS.get(role, set())
    return [(num, label, fn) for num, label, fn in all_items if num in allowed]
def main_menu(current_user: dict):
    """
    Displays the main menu based on the user's role.
    Admin gets extra options (User Management).
    """
    role      = current_user['role']
    username  = current_user['username']
    menu_items = get_menu_items(role)
    while True:
        print_line()
        print(f"  MAIN MENU  |  Logged in as: {username.upper()}  [{role.upper()}]")
        print_line()
        for num, label, _ in menu_items:
            print(f"  {num}. {label}")
        if role == "admin":
            print("  U. User Management")
        print("  P. Change Password")
        print("  0. Logout")
        print_line()
        choice = input("  Select option: ").strip().upper()
        matched = False
        for num, label, fn in menu_items:
            if choice == num:
                fn()
                matched = True
                break
        if matched:
            continue
        if choice == "U" and role == "admin":
            user_management_menu(current_user)
        elif choice == "P":
            change_password(current_user)
        elif choice == "0":
            print(f"\n  Goodbye, {username}! Logged out.\n")
            break
        else:
            print("  [!] Invalid option or access denied for your role.")
if __name__ == "__main__":
    show_banner()
    print("  Initializing database...")
    initialize_database()
    print()
    current_user = None
    while current_user is None:
        current_user = login()
        if current_user is None:
            print("\n  Login failed. Please try again.\n")
            retry = input("  Try again? (yes/no): ").strip().lower()
            if retry != "yes":
                print("\n  Exiting HAMBAA. Goodbye!\n")
                sys.exit(0)
        print()
    if current_user['role'] == 'watchman':
        from modules.incident_management import watchman_menu
        watchman_menu(current_user)
    elif current_user['role'] == 'cleaner':
        from modules.cleaning_management import cleaner_menu
        cleaner_menu(current_user)
    elif current_user['role'] == 'farm_owner':
        from modules.farm_owner import farm_owner_menu
        farm_owner_menu(current_user)
    else:
        main_menu(current_user)
