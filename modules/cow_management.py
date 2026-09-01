from database import get_connection
from config import (print_header, print_line,
                    COW_STATUS_OPTIONS, GENDER_OPTIONS)
def get_today():
    from datetime import date
    return str(date.today())
def pick_option(prompt, options):
    """
    Displays a numbered list and returns the user's choice.
    Keeps asking until a valid number is entered.
    """
    print(f"\n  {prompt}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        choice = input("  Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  [!] Invalid choice. Try again.")
def print_cow_row(cow):
    """Prints one cow's details in a readable format."""
    print(f"""
  ID           : {cow['id']}
  Name         : {cow['name']}
  Breed        : {cow['breed']}
  Age          : {cow['age']} years
  Weight       : {cow['weight']} kg
  Gender       : {cow['gender']}
  Color        : {cow['color']}
  Purchase Date: {cow['purchase_date']}
  Status       : {cow['status']}""")
    print_line("-")
def add_cow():
    """Collects cow details from the user and saves to database."""
    print_header("ADD NEW COW")
    name = input("  Cow Name       : ").strip()
    if not name:
        print("  [!] Name cannot be empty.")
        return
    breed  = input("  Breed          : ").strip()
    color  = input("  Color          : ").strip()
    while True:
        age_input = input("  Age (years)    : ").strip()
        try:
            age = float(age_input)
            break
        except ValueError:
            print("  [!] Please enter a valid number for age.")
    while True:
        weight_input = input("  Weight (kg)    : ").strip()
        try:
            weight = float(weight_input)
            break
        except ValueError:
            print("  [!] Please enter a valid number for weight.")
    gender        = pick_option("Select Gender:", GENDER_OPTIONS)
    status        = pick_option("Select Status:", COW_STATUS_OPTIONS)
    purchase_date = input(f"  Purchase Date (YYYY-MM-DD) [{get_today()}]: ").strip()
    if not purchase_date:
        purchase_date = get_today()
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cows (name, breed, age, weight, gender, color, purchase_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, breed, age, weight, gender, color, purchase_date, status))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        print(f"\n  [OK] Cow '{name}' added successfully! (ID: {new_id})")
    except Exception as e:
        print(f"  [ERROR] Could not add cow: {e}")
def view_all_cows():
    """Fetches and displays all cows from the database."""
    print_header("ALL COWS")
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cows ORDER BY id")
        cows = cursor.fetchall()
        conn.close()
        if not cows:
            print("  No cows found in the database.")
            return
        print(f"  Total cows: {len(cows)}\n")
        for cow in cows:
            print_cow_row(cow)
    except Exception as e:
        print(f"  [ERROR] Could not retrieve cows: {e}")
def search_cow():
    """Search for a cow by name or ID."""
    print_header("SEARCH COW")
    keyword = input("  Enter Cow Name or ID: ").strip()
    if not keyword:
        print("  [!] Please enter a search term.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        if keyword.isdigit():
            cursor.execute("SELECT * FROM cows WHERE id = ?", (int(keyword),))
        else:
            cursor.execute("SELECT * FROM cows WHERE name LIKE ?", (f"%{keyword}%",))
        results = cursor.fetchall()
        conn.close()
        if not results:
            print(f"  No cow found matching '{keyword}'.")
            return
        print(f"  Found {len(results)} result(s):\n")
        for cow in results:
            print_cow_row(cow)
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
def update_cow():
    """Update an existing cow's details."""
    print_header("UPDATE COW")
    cow_id = input("  Enter Cow ID to update: ").strip()
    if not cow_id.isdigit():
        print("  [!] Please enter a valid numeric ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cows WHERE id = ?", (int(cow_id),))
        cow = cursor.fetchone()
        if not cow:
            print(f"  [!] No cow found with ID {cow_id}.")
            conn.close()
            return
        print(f"\n  Current details for Cow ID {cow_id}:")
        print_cow_row(cow)
        print("  (Press ENTER to keep current value)\n")
        name   = input(f"  Name [{cow['name']}]          : ").strip() or cow['name']
        breed  = input(f"  Breed [{cow['breed']}]         : ").strip() or cow['breed']
        color  = input(f"  Color [{cow['color']}]         : ").strip() or cow['color']
        age_in = input(f"  Age [{cow['age']}]             : ").strip()
        age    = float(age_in) if age_in else cow['age']
        wt_in  = input(f"  Weight [{cow['weight']}]       : ").strip()
        weight = float(wt_in) if wt_in else cow['weight']
        gender = pick_option(f"Gender (current: {cow['gender']}):", GENDER_OPTIONS)
        status = pick_option(f"Status (current: {cow['status']}):", COW_STATUS_OPTIONS)
        cursor.execute("""
            UPDATE cows
            SET name=?, breed=?, age=?, weight=?, gender=?, color=?, status=?
            WHERE id=?
        """, (name, breed, age, weight, gender, color, status, int(cow_id)))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Cow ID {cow_id} updated successfully!")
    except ValueError:
        print("  [!] Invalid number entered.")
    except Exception as e:
        print(f"  [ERROR] Update failed: {e}")
def delete_cow():
    """Delete a cow record from the database."""
    print_header("DELETE COW")
    cow_id = input("  Enter Cow ID to delete: ").strip()
    if not cow_id.isdigit():
        print("  [!] Please enter a valid numeric ID.")
        return
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cows WHERE id = ?", (int(cow_id),))
        cow = cursor.fetchone()
        if not cow:
            print(f"  [!] No cow found with ID {cow_id}.")
            conn.close()
            return
        confirm = input(f"  Are you sure you want to delete '{cow['name']}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  [!] Deletion cancelled.")
            conn.close()
            return
        cursor.execute("DELETE FROM cows WHERE id = ?", (int(cow_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Cow '{cow['name']}' deleted successfully!")
    except Exception as e:
        print(f"  [ERROR] Deletion failed: {e}")
def cow_menu():
    """Displays the Cow Management sub-menu."""
    while True:
        print_header("COW MANAGEMENT")
        print("  1. Add Cow")
        print("  2. View All Cows")
        print("  3. Search Cow")
        print("  4. Update Cow")
        print("  5. Delete Cow")
        print("  0. Back to Main Menu")
        print_line()
        choice = input("  Select option: ").strip()
        if   choice == "1": add_cow()
        elif choice == "2": view_all_cows()
        elif choice == "3": search_cow()
        elif choice == "4": update_cow()
        elif choice == "5": delete_cow()
        elif choice == "0": break
        else: print("  [!] Invalid option. Please try again.")
