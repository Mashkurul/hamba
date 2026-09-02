from datetime import datetime
from database import get_connection
from config import (print_header, print_line, CLEANING_AREAS,
                    CLEANING_TYPES, CLEANING_STATUS)
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
def add_cleaning_record(current_user: dict):
    """Record a cleaning activity."""
    print_header("ADD CLEANING RECORD")
    cleaner_id = current_user['id']
    area       = pick_from(CLEANING_AREAS, "Area")
    ctype      = pick_from(CLEANING_TYPES, "Cleaning type")
    date       = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    time       = input(f"  Time (HH:MM) [{get_time()}]: ").strip() or get_time()
    status     = pick_from(CLEANING_STATUS, "Status")
    remarks    = input("  Remarks (optional): ").strip()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cleaning (cleaner_id, area, cleaning_type, date, time, status, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cleaner_id, area, ctype, date, time, status, remarks))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Cleaning record saved: {area} - {ctype} ({status}).")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def view_cleaning_tasks():
    """Show cleaning records that are not yet completed."""
    print_header("CLEANING TASKS (PENDING / IN PROGRESS)")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cleaning
            WHERE status IN ('Pending', 'In Progress')
            ORDER BY date ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("  No pending cleaning tasks.")
            return
        for r in rows:
            print(f"  [#{r['cleaning_id']}] {r['area']:<22} {r['cleaning_type']:<24} "
                  f"{r['status']:<12} {r['date']} {r['time']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def mark_task_complete():
    """Mark a cleaning task as Completed."""
    print_header("MARK CLEANING TASK COMPLETE")
    task_id = input("  Cleaning task ID: ").strip()
    if not task_id.isdigit():
        print("  [!] Invalid ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cleaning WHERE cleaning_id = ?", (int(task_id),))
        row = cursor.fetchone()
        if not row:
            print(f"  [!] No cleaning task found with ID {task_id}.")
            conn.close()
            return
        cursor.execute("UPDATE cleaning SET status = 'Completed' WHERE cleaning_id = ?",
                       (int(task_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Task #{task_id} ({row['area']}) marked as Completed.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def view_cleaning_history():
    """Display all cleaning records."""
    print_header("CLEANING HISTORY")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cleaning ORDER BY date DESC, time DESC")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("  No cleaning records yet.")
            return
        print(f"  {'ID':<4} {'Area':<22} {'Type':<24} {'Status':<12} {'Date':<12} {'Time'}")
        print_line("-")
        for r in rows:
            print(f"  {r['cleaning_id']:<4} {r['area']:<22} {r['cleaning_type']:<24} "
                  f"{r['status']:<12} {r['date']:<12} {r['time']}")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def report_cleaning_problem():
    """Report a dirty/unsafe area as a high-priority cleaning record."""
    print_header("REPORT CLEANING PROBLEM")
    area    = pick_from(CLEANING_AREAS, "Problem area")
    problem = input("  Describe the problem: ").strip()
    if not problem:
        print("  [!] Description is required.")
        return
    date = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    time = get_time()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cleaning (cleaner_id, area, cleaning_type, date, time, status, remarks)
            VALUES (NULL, ?, 'General Cleaning', ?, ?, 'In Progress', ?)
        """, (area, date, time, f"PROBLEM: {problem}"))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Problem reported for {area}. It is now flagged as In Progress.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def view_cleaning_areas():
    """Show the standard cleaning areas."""
    print_header("REQUIRED CLEANING AREAS")
    for i, area in enumerate(CLEANING_AREAS, 1):
        print(f"  {i}. {area}")
def cleaner_menu(current_user: dict):
    """Cleaner-specific menu."""
    from modules.notifications import view_notifications, view_alerts
    while True:
        print_header("CLEANER MENU")
        print("  1. View Cleaning Tasks")
        print("  2. Mark Cleaning Task Complete")
        print("  3. Add Cleaning Record")
        print("  4. View Cleaning History")
        print("  5. Report Cleaning Problem")
        print("  6. View Notifications")
        print("  7. View Important Alerts")
        print("  8. View Required Cleaning Areas")
        print("  0. Logout")
        print_line()
        choice = input("  Select option: ").strip()
        if   choice == "1": view_cleaning_tasks()
        elif choice == "2": mark_task_complete()
        elif choice == "3": add_cleaning_record(current_user)
        elif choice == "4": view_cleaning_history()
        elif choice == "5": report_cleaning_problem()
        elif choice == "6": view_notifications(current_user)
        elif choice == "7": view_alerts(current_user)
        elif choice == "8": view_cleaning_areas()
        elif choice == "0":
            print("  Logging out...")
            break
        else:
            print("  [!] Invalid option.")
def view_all_cleaning():
    view_cleaning_history()
