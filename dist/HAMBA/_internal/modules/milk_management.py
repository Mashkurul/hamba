from database import get_connection
from config import print_header, print_line
def get_today():
    from datetime import date
    return str(date.today())
def print_milk_row(record):
    print(f"  ID: {record['id']} | Cow ID: {record['cow_id']} | "
          f"Date: {record['date']} | Liters: {record['liters']} L | "
          f"Session: {record['session']} | Notes: {record['notes']}")
    print_line("-")
def record_milk():
    """Record how much milk a cow produced today."""
    print_header("RECORD DAILY MILK")
    cow_id_input = input("  Cow ID: ").strip()
    if not cow_id_input.isdigit():
        print("  [!] Invalid Cow ID.")
        return
    cow_id = int(cow_id_input)
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, gender FROM cows WHERE id = ?", (cow_id,))
    cow = cursor.fetchone()
    if not cow:
        print(f"  [!] No cow found with ID {cow_id}.")
        conn.close()
        return
    if cow['gender'] != 'Female':
        print(f"  [!] '{cow['name']}' is a male cow ({cow['gender']}).")
        print("  [!] Milk can only be recorded for FEMALE cows.")
        conn.close()
        return
    print(f"  Cow: {cow['name']}")
    date = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    while True:
        liters_input = input("  Liters collected: ").strip()
        try:
            liters = float(liters_input)
            if liters < 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Please enter a valid positive number.")
    print("\n  Session:")
    print("    1. Morning")
    print("    2. Afternoon")
    print("    3. Evening")
    session_map = {"1": "Morning", "2": "Afternoon", "3": "Evening"}
    session_choice = input("  Select session (1/2/3): ").strip()
    session = session_map.get(session_choice, "Morning")
    notes = input("  Notes (optional): ").strip()
    try:
        cursor.execute("""
            INSERT INTO milk (cow_id, date, liters, session, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (cow_id, date, liters, session, notes))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Milk record saved! {liters}L from {cow['name']} on {date}.")
    except Exception as e:
        print(f"  [ERROR] Could not save record: {e}")
def view_milk_history():
    """Display all milk records, optionally filtered by cow."""
    print_header("MILK HISTORY")
    filter_choice = input("  Filter by Cow ID? (Enter ID or press ENTER for all): ").strip()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        if filter_choice.isdigit():
            cursor.execute(
                "SELECT * FROM milk WHERE cow_id = ? ORDER BY date DESC",
                (int(filter_choice),)
            )
        else:
            cursor.execute("SELECT * FROM milk ORDER BY date DESC")
        records = cursor.fetchall()
        conn.close()
        if not records:
            print("  No milk records found.")
            return
        print(f"  Total records: {len(records)}\n")
        for r in records:
            print_milk_row(r)
    except Exception as e:
        print(f"  [ERROR] Could not retrieve records: {e}")
def calculate_total_milk():
    """Calculate total liters produced in a date range."""
    print_header("CALCULATE TOTAL MILK")
    start = input("  Start Date (YYYY-MM-DD): ").strip()
    end   = input("  End Date   (YYYY-MM-DD): ").strip()
    if not start or not end:
        print("  [!] Please enter both start and end dates.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(liters) as total, COUNT(*) as records
            FROM milk
            WHERE date BETWEEN ? AND ?
        """, (start, end))
        result = cursor.fetchone()
        conn.close()
        total   = result['total']   or 0.0
        records = result['records'] or 0
        print(f"\n  From {start} to {end}:")
        print(f"  Total Records : {records}")
        print(f"  Total Milk    : {total:.2f} Liters")
    except Exception as e:
        print(f"  [ERROR] Calculation failed: {e}")
def search_milk():
    """Search milk records by date or cow ID."""
    print_header("SEARCH MILK RECORD")
    print("  1. Search by Date")
    print("  2. Search by Cow ID")
    choice = input("  Select (1/2): ").strip()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        if choice == "1":
            date = input("  Enter Date (YYYY-MM-DD): ").strip()
            cursor.execute("SELECT * FROM milk WHERE date = ?", (date,))
        elif choice == "2":
            cow_id = input("  Enter Cow ID: ").strip()
            cursor.execute("SELECT * FROM milk WHERE cow_id = ?", (cow_id,))
        else:
            print("  [!] Invalid option.")
            conn.close()
            return
        results = cursor.fetchall()
        conn.close()
        if not results:
            print("  No records found.")
            return
        for r in results:
            print_milk_row(r)
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
def milk_menu():
    """Displays the Milk Management sub-menu."""
    while True:
        print_header("MILK MANAGEMENT")
        print("  1. Record Daily Milk")
        print("  2. View Milk History")
        print("  3. Calculate Total Milk")
        print("  4. Search Milk Record")
        print("  0. Back to Main Menu")
        print_line()
        choice = input("  Select option: ").strip()
        if   choice == "1": record_milk()
        elif choice == "2": view_milk_history()
        elif choice == "3": calculate_total_milk()
        elif choice == "4": search_milk()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
