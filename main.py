# =============================================================
# main.py - HAMBA Application Entry Point
# =============================================================
# This is the file you run to start the HAMBA system.
# It initializes the database and shows the main menu.
#
# Run with:  python main.py
# =============================================================

import sys
import os

# Add project root to path so all imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import initialize_database
from config import print_header, print_line, APP_TITLE, APP_VERSION

# Import all sub-menu functions from modules
from modules.cow_management      import cow_menu
from modules.milk_management     import milk_menu
from modules.food_management     import food_menu
from modules.health_management   import health_menu
from modules.employee_management import employee_menu
from modules.expense_management  import expense_menu
from modules.reports             import reports_menu
from modules.ai_assistant        import ai_menu


# ---------------------------------------------------------
# Show welcome banner
# ---------------------------------------------------------
def show_banner():
    """Prints the welcome screen when the app starts."""
    os.system("cls" if os.name == "nt" else "clear")  # clear terminal
    print_line()
    print(f"  {APP_TITLE}")
    print(f"  Version: {APP_VERSION}")
    print(f"  University Project")
    print_line()
    print()


# ---------------------------------------------------------
# Main Menu
# ---------------------------------------------------------
def main_menu():
    """
    Displays the main menu and routes the user
    to the selected module.
    """
    while True:
        print_header("MAIN MENU")
        print("  1. Cow Management")
        print("  2. Milk Management")
        print("  3. Food Management")
        print("  4. Health & Medicine")
        print("  5. Employee Management")
        print("  6. Expense & Sales")
        print("  7. Reports")
        print("  8. AI Assistant")
        print("  9. Exit")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": cow_menu()
        elif choice == "2": milk_menu()
        elif choice == "3": food_menu()
        elif choice == "4": health_menu()
        elif choice == "5": employee_menu()
        elif choice == "6": expense_menu()
        elif choice == "7": reports_menu()
        elif choice == "8": ai_menu()
        elif choice == "9":
            print("\n  Thank you for using HAMBA. Goodbye!\n")
            break
        else:
            print("  [!] Invalid option. Please enter a number from 1-9.")


# ---------------------------------------------------------
# Application Start
# ---------------------------------------------------------
if __name__ == "__main__":
    # Step 1: Show welcome banner
    show_banner()

    # Step 2: Initialize database (creates tables if needed)
    print("  Initializing database...")
    initialize_database()
    print()

    # Step 3: Launch the main menu
    main_menu()
