from database import get_connection
from config import print_header, print_line, FOOD_TYPES
def get_today():
    from datetime import date
    return str(date.today())
def pick_food_type():
    """Let user pick a food type from the list."""
    print("\n  Food Types:")
    for i, ft in enumerate(FOOD_TYPES, 1):
        print(f"    {i}. {ft}")
    while True:
        choice = input("  Select food type: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(FOOD_TYPES):
            return FOOD_TYPES[int(choice) - 1]
        print("  [!] Invalid choice.")
def print_food_row(record):
    print(f"  ID: {record['id']} | Type: {record['food_type']} | "
          f"Qty: {record['quantity_kg']} kg | Date: {record['date']} | "
          f"Cow ID: {record['cow_id']} | Notes: {record['notes']}")
    print_line("-")
def add_feed():
    """Add a new food/feed record to the database."""
    print_header("ADD FEED RECORD")
    food_type = pick_food_type()
    while True:
        qty_input = input("  Quantity (kg): ").strip()
        try:
            quantity = float(qty_input)
            if quantity <= 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Enter a valid positive number.")
    date = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    cow_id_input = input("  Cow ID (optional, press ENTER to skip): ").strip()
    cow_id = int(cow_id_input) if cow_id_input.isdigit() else None
    notes = input("  Notes (optional): ").strip()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO food (food_type, quantity_kg, date, cow_id, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (food_type, quantity, date, cow_id, notes))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Feed record added: {quantity} kg of {food_type} on {date}.")
    except Exception as e:
        print(f"  [ERROR] Could not add record: {e}")
def view_food_stock():
    """View all food/feed records."""
    print_header("FOOD STOCK & FEED RECORDS")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food ORDER BY date DESC")
        records = cursor.fetchall()
        conn.close()
        if not records:
            print("  No feed records found.")
            return
        total_by_type = {}
        for r in records:
            total_by_type[r['food_type']] = total_by_type.get(r['food_type'], 0) + r['quantity_kg']
        print("  --- Stock Summary ---")
        for ft, qty in total_by_type.items():
            print(f"  {ft:<15}: {qty:.2f} kg")
        print_line("-")
        print(f"\n  Total records: {len(records)}\n")
        for r in records:
            print_food_row(r)
    except Exception as e:
        print(f"  [ERROR] Could not retrieve records: {e}")
def daily_feeding():
    """Show all feed records for today."""
    print_header("TODAY'S FEEDING RECORDS")
    today = get_today()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food WHERE date = ?", (today,))
        records = cursor.fetchall()
        conn.close()
        if not records:
            print(f"  No feeding records for today ({today}).")
            return
        total_kg = sum(r['quantity_kg'] for r in records)
        print(f"  Date: {today} | Records: {len(records)} | Total: {total_kg:.2f} kg\n")
        for r in records:
            print_food_row(r)
    except Exception as e:
        print(f"  [ERROR]: {e}")
def update_feed():
    """Update an existing feed record."""
    print_header("UPDATE FEED RECORD")
    record_id = input("  Enter Feed Record ID: ").strip()
    if not record_id.isdigit():
        print("  [!] Invalid ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food WHERE id = ?", (int(record_id),))
        record = cursor.fetchone()
        if not record:
            print(f"  [!] No record found with ID {record_id}.")
            conn.close()
            return
        print_food_row(record)
        print("  (Press ENTER to keep current value)\n")
        food_type = pick_food_type()
        qty_in   = input(f"  Quantity [{record['quantity_kg']}] kg: ").strip()
        quantity = float(qty_in) if qty_in else record['quantity_kg']
        date_in = input(f"  Date [{record['date']}]: ").strip()
        date    = date_in if date_in else record['date']
        notes_in = input(f"  Notes [{record['notes']}]: ").strip()
        notes    = notes_in if notes_in else record['notes']
        cursor.execute("""
            UPDATE food SET food_type=?, quantity_kg=?, date=?, notes=?
            WHERE id=?
        """, (food_type, quantity, date, notes, int(record_id)))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Feed record ID {record_id} updated.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def delete_feed():
    """Delete a feed record."""
    print_header("DELETE FEED RECORD")
    record_id = input("  Enter Feed Record ID to delete: ").strip()
    if not record_id.isdigit():
        print("  [!] Invalid ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food WHERE id = ?", (int(record_id),))
        record = cursor.fetchone()
        if not record:
            print(f"  [!] No record found with ID {record_id}.")
            conn.close()
            return
        confirm = input(f"  Delete record ID {record_id}? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  [!] Cancelled.")
            conn.close()
            return
        cursor.execute("DELETE FROM food WHERE id = ?", (int(record_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Feed record ID {record_id} deleted.")
    except Exception as e:
        print(f"  [ERROR]: {e}")
def food_menu():
    """Displays the Food Management sub-menu."""
    while True:
        print_header("FOOD MANAGEMENT")
        print("  1. Add Feed Record")
        print("  2. View Food Stock")
        print("  3. Today's Feeding")
        print("  4. Update Feed Record")
        print("  5. Delete Feed Record")
        print("  0. Back to Main Menu")
        print_line()
        choice = input("  Select option: ").strip()
        if   choice == "1": add_feed()
        elif choice == "2": view_food_stock()
        elif choice == "3": daily_feeding()
        elif choice == "4": update_feed()
        elif choice == "5": delete_feed()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
