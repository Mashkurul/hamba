# =============================================================
# modules/incident_management.py - Watchman Incident Module
# =============================================================
# Handles security incident recording and monitoring:
#   - Add incident
#   - View incidents
#   - Search incidents
#   - Update incident status
# =============================================================

from datetime import datetime
from database import get_connection
from config import (print_header, print_line, INCIDENT_TYPES,
                    INCIDENT_PRIORITY, INCIDENT_STATUS)


def get_today():
    from datetime import date
    return str(date.today())


def get_time():
    return datetime.now().strftime("%H:%M")


def pick_from(options, prompt):
    """Show a numbered list and return the chosen option."""
    print("\n  Options:")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        choice = input(f"  {prompt}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  [!] Invalid choice.")


# ---------------------------------------------------------
# Feature 1: Add an incident
# ---------------------------------------------------------
def add_incident(current_user: dict):
    """Record a new security incident."""
    print_header("RECORD INCIDENT")

    reported_by   = current_user['username']
    incident_type = pick_from(INCIDENT_TYPES, "Incident type")
    description   = input("  Description : ").strip()
    date          = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    time          = input(f"  Time (HH:MM) [{get_time()}]: ").strip() or get_time()
    location      = input("  Location    : ").strip()
    priority      = pick_from(INCIDENT_PRIORITY, "Priority")

    if not description:
        print("  [!] Description is required.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO incidents
                (reported_by, incident_type, description, date, time, location, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Open')
        """, (reported_by, incident_type, description, date, time, location, priority))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Incident recorded: {incident_type} ({priority}) at {location}.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 2: View incidents
# ---------------------------------------------------------
def view_incidents():
    """Display all incidents."""
    print_header("ALL INCIDENTS")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents ORDER BY date DESC, time DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No incidents recorded.")
            return

        print(f"  {'ID':<4} {'Type':<22} {'Priority':<9} {'Status':<12} {'Date':<12} {'Location'}")
        print_line("-")
        for r in rows:
            print(f"  {r['incident_id']:<4} {r['incident_type']:<22} "
                  f"{r['priority']:<9} {r['status']:<12} {r['date']:<12} {r['location']}")
        print_line("-")
        open_count = sum(1 for r in rows if r['status'] in ("Open", "In Progress"))
        print(f"  Open incidents: {open_count} / {len(rows)}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 3: Search incidents
# ---------------------------------------------------------
def search_incidents():
    """Search incidents by keyword in type/description/location."""
    print_header("SEARCH INCIDENTS")

    keyword = input("  Search keyword: ").strip().lower()
    if not keyword:
        print("  [!] Keyword is required.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM incidents
            WHERE LOWER(incident_type) LIKE ? OR LOWER(description) LIKE ?
               OR LOWER(location) LIKE ? OR LOWER(status) LIKE ?
            ORDER BY date DESC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print(f"  No incidents match '{keyword}'.")
            return

        print(f"\n  Found {len(rows)} incident(s):\n")
        for r in rows:
            print(f"  [#{r['incident_id']}] {r['incident_type']} | {r['priority']} | "
                  f"{r['status']} | {r['date']} {r['time']} | {r['location']}")
            if r['description']:
                print(f"      {r['description']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 4: Update incident status
# ---------------------------------------------------------
def update_incident_status():
    """Update the status of an existing incident."""
    print_header("UPDATE INCIDENT STATUS")

    incident_id = input("  Incident ID: ").strip()
    if not incident_id.isdigit():
        print("  [!] Invalid ID.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents WHERE incident_id = ?", (int(incident_id),))
        row = cursor.fetchone()
        if not row:
            print(f"  [!] No incident found with ID {incident_id}.")
            conn.close()
            return

        print(f"\n  Current: [{row['incident_type']}] {row['status']} - {row['description']}")
        new_status = pick_from(INCIDENT_STATUS, "New status")
        cursor.execute("UPDATE incidents SET status = ? WHERE incident_id = ?",
                       (new_status, int(incident_id)))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Incident #{incident_id} status updated to '{new_status}'.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Self-attendance (watchman / cleaner mark their own attendance)
# Uses the users table — each user is an employee of the farm.
# ---------------------------------------------------------
def mark_own_attendance(current_user: dict):
    """Mark today's attendance for the current user."""
    print_header("MARK OWN ATTENDANCE")

    from config import ATTENDANCE_STATUS
    status = pick_from(ATTENDANCE_STATUS, "Status")
    date   = get_today()

    try:
        conn = get_connection()
        cur  = conn.cursor()
        # Record in the shared attendance table using the user id as employee ref
        cur.execute("""
            INSERT INTO attendance (employee_id, date, status)
            VALUES (?, ?, ?)
        """, (current_user['id'], date, status))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Attendance marked: {current_user['username']} - {status} on {date}.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


def view_own_attendance(current_user: dict, today_only=False):
    """View attendance history for the current user."""
    print_header("MY ATTENDANCE")

    try:
        conn = get_connection()
        cur  = conn.cursor()
        if today_only:
            cur.execute("""
                SELECT date, status FROM attendance
                WHERE employee_id = ? AND date = ?
                ORDER BY date DESC
            """, (current_user['id'], get_today()))
        else:
            cur.execute("""
                SELECT date, status FROM attendance
                WHERE employee_id = ?
                ORDER BY date DESC
            """, (current_user['id'],))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print(f"  No attendance records for {current_user['username']}.")
            return

        for r in rows:
            print(f"  {r['date']:<12} {r['status']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


def view_employee_presence():
    """Show which employees are present today (from attendance)."""
    print_header("EMPLOYEE PRESENCE TODAY")

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT a.status, COUNT(*) as cnt
            FROM attendance a
            WHERE a.date = ?
            GROUP BY a.status
        """, (get_today(),))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("  No attendance marked for today yet.")
            return

        total = 0
        for r in rows:
            print(f"  {r['status']:<10}: {r['cnt']}")
            total += r['cnt']
        print_line("-")
        print(f"  Total marked today: {total}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Watchman Menu
# ---------------------------------------------------------
def watchman_menu(current_user: dict):
    """Watchman-specific menu."""
    from modules.notifications import view_notifications, view_alerts
    from modules.cow_management import view_all_cows
    from modules.reports import milk_production_report

    while True:
        print_header("WATCHMAN MENU")
        print("  1. View Today's Attendance")
        print("  2. Mark Own Attendance")
        print("  3. Record Farm Incident")
        print("  4. View Farm Incidents")
        print("  5. Search Incidents")
        print("  6. Update Incident Status")
        print("  7. View Notifications")
        print("  8. View Important Alerts")
        print("  9. View Basic Cow Status")
        print("  10. View Employee Presence")
        print("  11. View Milk Production Report")
        print("  12. Report Suspicious Activity")
        print("  0. Logout")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1":  view_own_attendance(current_user, today_only=True)
        elif choice == "2":  mark_own_attendance(current_user)
        elif choice == "3":  add_incident(current_user)
        elif choice == "4":  view_incidents()
        elif choice == "5":  search_incidents()
        elif choice == "6":  update_incident_status()
        elif choice == "7":  view_notifications(current_user)
        elif choice == "8":  view_alerts(current_user)
        elif choice == "9":  view_all_cows()
        elif choice == "10": view_employee_presence()
        elif choice == "11": milk_production_report()
        elif choice == "12": add_incident(current_user)
        elif choice == "0":
            print("  Logging out...")
            break
        else:
            print("  [!] Invalid option.")


# ---------------------------------------------------------
# Shared: view all incidents (used by owner/admin)
# ---------------------------------------------------------
def view_all_incidents():
    view_incidents()
