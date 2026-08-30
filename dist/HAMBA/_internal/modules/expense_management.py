# =============================================================
# modules/expense_management.py - Expense & Sales Module
# =============================================================
# Handles all financial operations:
#   - Record Daily Expense
#   - Record Milk Sale
#   - View Expenses
#   - View Sales
#   - Profit Calculation
#   - Monthly Summary
# =============================================================

from database import get_connection
from config import print_header, print_line, EXPENSE_CATEGORIES


def get_today():
    from datetime import date
    return str(date.today())


def pick_category():
    print("\n  Expense Categories:")
    for i, cat in enumerate(EXPENSE_CATEGORIES, 1):
        print(f"    {i}. {cat}")
    while True:
        choice = input("  Select category: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(EXPENSE_CATEGORIES):
            return EXPENSE_CATEGORIES[int(choice) - 1]
        print("  [!] Invalid choice.")


# ---------------------------------------------------------
# Feature 1: Record a daily expense
# ---------------------------------------------------------
def add_expense():
    """Record a farm expense."""
    print_header("ADD EXPENSE")

    date        = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    category    = pick_category()
    description = input("  Description  : ").strip()

    while True:
        amt_input = input("  Amount       : ").strip()
        try:
            amount = float(amt_input)
            if amount <= 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Enter a valid positive number.")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """, (date, category, amount, description))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Expense recorded: {category} – {amount} on {date}.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 2: Record a milk sale
# ---------------------------------------------------------
def add_sale():
    """Record a milk sale transaction."""
    print_header("RECORD MILK SALE")

    date = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()

    while True:
        liters_input = input("  Liters sold          : ").strip()
        try:
            liters = float(liters_input)
            if liters <= 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Enter a valid positive number.")

    while True:
        price_input = input("  Price per liter      : ").strip()
        try:
            price = float(price_input)
            if price <= 0:
                raise ValueError
            break
        except ValueError:
            print("  [!] Enter a valid positive number.")

    total      = liters * price
    buyer_name = input("  Buyer name (optional): ").strip()
    notes      = input("  Notes (optional)     : ").strip()

    print(f"\n  Total Amount = {liters} L × {price} = {total:.2f}")
    confirm = input("  Confirm sale? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  [!] Sale cancelled.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sales (date, liters_sold, price_per_liter, total_amount, buyer_name, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (date, liters, price, total, buyer_name, notes))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Sale recorded! Revenue: {total:.2f}")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 3: View all expenses
# ---------------------------------------------------------
def view_expenses():
    """Display all expense records."""
    print_header("ALL EXPENSES")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = cursor.fetchall()
        conn.close()

        if not expenses:
            print("  No expenses recorded.")
            return

        total = 0.0
        print(f"  {'ID':<5} {'Date':<13} {'Category':<12} {'Amount':>10}  Description")
        print_line("-")
        for e in expenses:
            print(f"  {e['id']:<5} {e['date']:<13} {e['category']:<12} "
                  f"{e['amount']:>10.2f}  {e['description']}")
            total += e['amount']

        print_line("-")
        print(f"  Total Expenses: {total:.2f}")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 4: View all sales
# ---------------------------------------------------------
def view_sales():
    """Display all milk sale records."""
    print_header("ALL SALES")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales ORDER BY date DESC")
        sales = cursor.fetchall()
        conn.close()

        if not sales:
            print("  No sales recorded.")
            return

        total_revenue = 0.0
        total_liters  = 0.0
        for s in sales:
            print(f"  ID: {s['id']} | Date: {s['date']} | "
                  f"Liters: {s['liters_sold']} L | "
                  f"Price: {s['price_per_liter']}/L | "
                  f"Total: {s['total_amount']:.2f} | "
                  f"Buyer: {s['buyer_name']}")
            total_revenue += s['total_amount']
            total_liters  += s['liters_sold']

        print_line("-")
        print(f"  Total Liters Sold : {total_liters:.2f} L")
        print(f"  Total Revenue     : {total_revenue:.2f}")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 5: Profit calculation
# ---------------------------------------------------------
def calculate_profit():
    """Calculate net profit = Total Sales - Total Expenses."""
    print_header("PROFIT CALCULATION")

    start = input("  Start Date (YYYY-MM-DD): ").strip()
    end   = input("  End Date   (YYYY-MM-DD): ").strip()

    if not start or not end:
        print("  [!] Both dates are required.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT SUM(total_amount) as total FROM sales WHERE date BETWEEN ? AND ?",
            (start, end)
        )
        sales_result = cursor.fetchone()

        cursor.execute(
            "SELECT SUM(amount) as total FROM expenses WHERE date BETWEEN ? AND ?",
            (start, end)
        )
        expense_result = cursor.fetchone()
        conn.close()

        total_sales    = sales_result['total']    or 0.0
        total_expenses = expense_result['total']  or 0.0
        net_profit     = total_sales - total_expenses

        print(f"\n  Period        : {start} to {end}")
        print(f"  Total Sales   : {total_sales:.2f}")
        print(f"  Total Expenses: {total_expenses:.2f}")
        print_line("-")
        if net_profit >= 0:
            print(f"  NET PROFIT    : +{net_profit:.2f}  ✓")
        else:
            print(f"  NET LOSS      : {net_profit:.2f}  ✗")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 6: Monthly summary
# ---------------------------------------------------------
def monthly_summary():
    """Show expense and sales summary for a given month."""
    print_header("MONTHLY SUMMARY")

    month = input("  Enter Month (YYYY-MM): ").strip()
    if not month or len(month) != 7:
        print("  [!] Invalid format. Use YYYY-MM (e.g. 2024-03).")
        return

    start = f"{month}-01"
    end   = f"{month}-31"

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Expenses by category
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
        """, (start, end))
        expense_rows = cursor.fetchall()

        # Sales total
        cursor.execute("""
            SELECT SUM(total_amount) as rev, SUM(liters_sold) as liters
            FROM sales
            WHERE date BETWEEN ? AND ?
        """, (start, end))
        sales_row = cursor.fetchone()
        conn.close()

        print(f"\n  Month: {month}\n")
        print("  --- Expenses by Category ---")
        total_exp = 0.0
        if expense_rows:
            for row in expense_rows:
                print(f"  {row['category']:<15}: {row['total']:.2f}")
                total_exp += row['total']
        else:
            print("  No expenses recorded.")

        print_line("-")
        print(f"  Total Expenses  : {total_exp:.2f}")

        total_rev   = sales_row['rev']    or 0.0
        total_liters = sales_row['liters'] or 0.0

        print(f"\n  --- Sales ---")
        print(f"  Liters Sold     : {total_liters:.2f} L")
        print(f"  Total Revenue   : {total_rev:.2f}")
        print_line("-")
        profit = total_rev - total_exp
        sign   = "+" if profit >= 0 else ""
        print(f"  Net Profit/Loss : {sign}{profit:.2f}")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Expense & Sales Menu
# ---------------------------------------------------------
def expense_menu():
    """Displays the Expense & Sales sub-menu."""
    while True:
        print_header("EXPENSE & SALES")
        print("  1. Add Expense")
        print("  2. Record Milk Sale")
        print("  3. View All Expenses")
        print("  4. View All Sales")
        print("  5. Profit Calculation")
        print("  6. Monthly Summary")
        print("  0. Back to Main Menu")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": add_expense()
        elif choice == "2": add_sale()
        elif choice == "3": view_expenses()
        elif choice == "4": view_sales()
        elif choice == "5": calculate_profit()
        elif choice == "6": monthly_summary()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
