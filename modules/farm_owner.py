# =============================================================
# modules/farm_owner.py - Farm Owner Dashboard & Menu
# =============================================================
# The Farm Owner is the highest-level operational user.
# This module provides a comprehensive farm summary plus access
# to every management module (read + write for farm data).
# =============================================================

from datetime import datetime, date
from database import get_connection
from config import print_header, print_line


def get_today():
    return str(date.today())


# ---------------------------------------------------------
# Farm Summary / Dashboard
# ---------------------------------------------------------
def farm_summary():
    """Show overall farm statistics."""
    print_header("FARM SUMMARY")

    try:
        conn = get_connection()
        cur  = conn.cursor()

        def q(sql, *a):
            cur.execute(sql, a)
            r = cur.fetchone()
            return r[0] if r else 0

        total_cows  = q("SELECT COUNT(*) FROM cows")
        healthy     = q("SELECT COUNT(*) FROM cows WHERE status='Active'")
        sick        = q("SELECT COUNT(*) FROM cows WHERE status='Sick'")
        milk_today  = q("SELECT COALESCE(SUM(liters),0) FROM milk WHERE date=?", get_today())
        employees   = q("SELECT COUNT(*) FROM employees WHERE status='Active'")
        att_today   = q("SELECT COUNT(*) FROM attendance WHERE date=?", get_today())
        low_stock   = q("""SELECT COUNT(*) FROM food f
                           LEFT JOIN cows c ON f.cow_id=c.id
                           WHERE f.quantity_kg < 50""")
        vacc_soon   = q("""SELECT COUNT(*) FROM health
                           WHERE record_type='Vaccination'
                             AND date >= date('now') AND date <= date('now','+30 days')""")
        exp_month   = q("""SELECT COALESCE(SUM(amount),0) FROM expenses
                           WHERE date LIKE ?""", get_today()[:7] + "%")
        rev_month   = q("""SELECT COALESCE(SUM(total_amount),0) FROM sales
                           WHERE date LIKE ?""", get_today()[:7] + "%")
        incidents   = q("""SELECT COUNT(*) FROM incidents
                           WHERE status IN ('Open','In Progress')""")
        pending_clean = q("""SELECT COUNT(*) FROM cleaning
                             WHERE status IN ('Pending','In Progress')""")

        print(f"  Total Cows          : {total_cows}")
        print(f"  Healthy Cows        : {healthy}")
        print(f"  Sick Cows           : {sick}")
        print(f"  Today's Milk        : {milk_today:.2f} L")
        print(f"  Active Employees    : {employees}")
        print(f"  Today's Attendance  : {att_today}")
        print(f"  Low Stock Items     : {low_stock}")
        print(f"  Vaccinations Due    : {vacc_soon} (next 30 days)")
        print_line("-")
        print(f"  Month Revenue       : {rev_month:,.2f}")
        print(f"  Month Expenses      : {exp_month:,.2f}")
        print(f"  Month Net           : {rev_month - exp_month:,.2f}")
        print_line("-")
        print(f"  Open Incidents      : {incidents}")
        print(f"  Pending Cleaning    : {pending_clean}")

        conn.close()
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Upcoming events (vaccinations / calving)
# ---------------------------------------------------------
def upcoming_events():
    """Show upcoming vaccinations and health events."""
    print_header("UPCOMING HEALTH / VACCINATION EVENTS")

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT h.date, c.name, h.record_type, COALESCE(h.description,'')
            FROM health h JOIN cows c ON h.cow_id = c.id
            WHERE h.date >= date('now')
            ORDER BY h.date ASC LIMIT 15
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("  No upcoming health events.")
            return

        for r in rows:
            print(f"  {r['date']:<12} {r['name']:<18} {r['record_type']:<12} {r[3]}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Recent activity (expenses + sales + incidents + cleaning)
# ---------------------------------------------------------
def recent_activity():
    """Show recent farm activity across modules."""
    print_header("RECENT ACTIVITY")

    try:
        conn = get_connection()
        cur  = conn.cursor()

        cur.execute("SELECT date, category, amount, description FROM expenses ORDER BY id DESC LIMIT 5")
        exps = cur.fetchall()
        cur.execute("SELECT date, liters_sold, total_amount, buyer_name FROM sales ORDER BY id DESC LIMIT 5")
        sales = cur.fetchall()
        cur.execute("SELECT date, incident_type, status, location FROM incidents ORDER BY id DESC LIMIT 5")
        incs = cur.fetchall()
        cur.execute("SELECT date, area, status FROM cleaning ORDER BY id DESC LIMIT 5")
        cleans = cur.fetchall()
        conn.close()

        print("  --- Recent Expenses ---")
        for r in exps:
            print(f"  {r['date']} {r['category']:<10} {r['amount']:>10.2f}  {r['description']}")
        print("  --- Recent Sales ---")
        for r in sales:
            print(f"  {r['date']} {r['liters_sold']}L -> {r['total_amount']:.2f} ({r['buyer_name']})")
        print("  --- Recent Incidents ---")
        for r in incs:
            print(f"  {r['date']} {r['incident_type']:<20} {r['status']:<12} {r['location']}")
        print("  --- Recent Cleaning ---")
        for r in cleans:
            print(f"  {r['date']} {r['area']:<22} {r['status']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Farm Owner Menu
# ---------------------------------------------------------
def farm_owner_menu(current_user: dict):
    """Farm Owner full management menu."""
    from modules.cow_management      import cow_menu
    from modules.milk_management     import milk_menu
    from modules.health_management   import health_menu
    from modules.food_management     import food_menu
    from modules.employee_management import employee_menu
    from modules.expense_management  import expense_menu
    from modules.reports             import reports_menu
    from modules.ai_assistant        import ai_menu
    from modules.notifications       import view_notifications, view_alerts
    from modules.incident_management import view_all_incidents
    from modules.cleaning_management import view_all_cleaning

    while True:
        print_header("FARM OWNER MENU")
        print("  1. Farm Summary")
        print("  2. Upcoming Health / Vaccinations")
        print("  3. Recent Activity")
        print("  4. Cow Management")
        print("  5. Milk Production")
        print("  6. Health & Vaccination Records")
        print("  7. Food / Feed Management")
        print("  8. Employee Management")
        print("  9. Sales & Expenses")
        print("  10. Reports")
        print("  11. AI Health Prediction & Reports")
        print("  12. View Incidents")
        print("  13. View Cleaning Records")
        print("  14. View Notifications")
        print("  15. View Important Alerts")
        print("  0. Logout")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1":  farm_summary()
        elif choice == "2":  upcoming_events()
        elif choice == "3":  recent_activity()
        elif choice == "4":  cow_menu()
        elif choice == "5":  milk_menu()
        elif choice == "6":  health_menu()
        elif choice == "7":  food_menu()
        elif choice == "8":  employee_menu()
        elif choice == "9":  expense_menu()
        elif choice == "10": reports_menu()
        elif choice == "11": ai_menu()
        elif choice == "12": view_all_incidents()
        elif choice == "13": view_all_cleaning()
        elif choice == "14": view_notifications(current_user)
        elif choice == "15": view_alerts(current_user)
        elif choice == "0":
            print("  Logging out...")
            break
        else:
            print("  [!] Invalid option.")
