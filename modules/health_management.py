# =============================================================
# modules/health_management.py - Health Management Module
# =============================================================
# Handles all health-related operations:
#   - Medical History
#   - Vaccination Record
#   - Medicine Record
#   - Disease Record
# =============================================================

from database import get_connection
from config import print_header, print_line


def get_today():
    from datetime import date
    return str(date.today())


RECORD_TYPES = ["Vaccination", "Disease", "Medicine", "Checkup", "Other"]


def pick_record_type():
    print("\n  Record Types:")
    for i, rt in enumerate(RECORD_TYPES, 1):
        print(f"    {i}. {rt}")
    while True:
        choice = input("  Select type: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(RECORD_TYPES):
            return RECORD_TYPES[int(choice) - 1]
        print("  [!] Invalid choice.")


def print_health_row(record):
    print(f"""
  ID          : {record['id']}
  Cow ID      : {record['cow_id']}
  Date        : {record['date']}
  Type        : {record['record_type']}
  Description : {record['description']}
  Medicine    : {record['medicine']}
  Vet Name    : {record['vet_name']}
  Cost        : {record['cost']}""")
    print_line("-")


# ---------------------------------------------------------
# Feature 1: Add health record
# ---------------------------------------------------------
def add_health_record():
    """Add a medical/health record for a cow."""
    print_header("ADD HEALTH RECORD")

    cow_id_input = input("  Cow ID: ").strip()
    if not cow_id_input.isdigit():
        print("  [!] Invalid Cow ID.")
        return
    cow_id = int(cow_id_input)

    # Verify cow exists
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM cows WHERE id = ?", (cow_id,))
    cow = cursor.fetchone()
    if not cow:
        print(f"  [!] No cow found with ID {cow_id}.")
        conn.close()
        return
    print(f"  Cow: {cow['name']}")

    record_type = pick_record_type()
    date        = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    description = input("  Description/Symptoms    : ").strip()
    medicine    = input("  Medicine used (if any)  : ").strip()
    vet_name    = input("  Veterinarian name       : ").strip()

    while True:
        cost_input = input("  Treatment cost          : ").strip()
        try:
            cost = float(cost_input) if cost_input else 0.0
            break
        except ValueError:
            print("  [!] Enter a valid number.")

    try:
        cursor.execute("""
            INSERT INTO health (cow_id, date, record_type, description, medicine, vet_name, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cow_id, date, record_type, description, medicine, vet_name, cost))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Health record added for cow '{cow['name']}'.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 2: View medical history for a cow
# ---------------------------------------------------------
def view_medical_history():
    """View all health records for a specific cow."""
    print_header("MEDICAL HISTORY")

    cow_id_input = input("  Enter Cow ID (or press ENTER for all): ").strip()

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        if cow_id_input.isdigit():
            cursor.execute(
                "SELECT * FROM health WHERE cow_id = ? ORDER BY date DESC",
                (int(cow_id_input),)
            )
        else:
            cursor.execute("SELECT * FROM health ORDER BY date DESC")

        records = cursor.fetchall()
        conn.close()

        if not records:
            print("  No health records found.")
            return

        print(f"  Total records: {len(records)}")
        for r in records:
            print_health_row(r)

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 3: View vaccination records only
# ---------------------------------------------------------
def view_vaccinations():
    """View only vaccination records."""
    print_header("VACCINATION RECORDS")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM health WHERE record_type = 'Vaccination' ORDER BY date DESC"
        )
        records = cursor.fetchall()
        conn.close()

        if not records:
            print("  No vaccination records found.")
            return

        print(f"  Total: {len(records)} vaccination records\n")
        for r in records:
            print_health_row(r)

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 4: View disease records only
# ---------------------------------------------------------
def view_diseases():
    """View only disease records."""
    print_header("DISEASE RECORDS")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM health WHERE record_type = 'Disease' ORDER BY date DESC"
        )
        records = cursor.fetchall()
        conn.close()

        if not records:
            print("  No disease records found.")
            return

        print(f"  Total: {len(records)} disease records\n")
        for r in records:
            print_health_row(r)

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Health Management Menu
# ---------------------------------------------------------
def health_menu():
    """Displays the Health Management sub-menu."""
    while True:
        print_header("HEALTH & MEDICINE")
        print("  1. Add Health Record")
        print("  2. View Medical History")
        print("  3. Vaccination Records")
        print("  4. Disease Records")
        print("  0. Back to Main Menu")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": add_health_record()
        elif choice == "2": view_medical_history()
        elif choice == "3": view_vaccinations()
        elif choice == "4": view_diseases()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
