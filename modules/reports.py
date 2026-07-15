# =============================================================
# modules/reports.py - Reports Module
# =============================================================
# Generates various reports:
#   - Daily Report
#   - Monthly Report
#   - Milk Production Report
#   - Expense Report
# =============================================================

from database import get_connection
from config import print_header, print_line


def get_today():
    from datetime import date
    return str(date.today())


# ---------------------------------------------------------
# Report 1: Daily Report
# ---------------------------------------------------------
def daily_report():
    """Generate a full report for a specific day."""
    print_header("DAILY REPORT")

    date = input(f"  Enter Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()

    conn   = get_connection()
    cursor = conn.cursor()

    print(f"\n  ===== DAILY REPORT: {date} =====\n")

    # --- Milk Production ---
    cursor.execute("""
        SELECT m.*, c.name as cow_name
        FROM milk m JOIN cows c ON m.cow_id = c.id
        WHERE m.date = ?
    """, (date,))
    milk_records = cursor.fetchall()
    total_milk = sum(r['liters'] for r in milk_records)

    print("  [ MILK PRODUCTION ]")
    if milk_records:
        for r in milk_records:
            print(f"  {r['cow_name']:<15} | {r['session']:<10} | {r['liters']} L")
        print(f"  Total Milk: {total_milk:.2f} L")
    else:
        print("  No milk recorded.")

    print()

    # --- Feeding ---
    cursor.execute("SELECT * FROM food WHERE date = ?", (date,))
    food_records = cursor.fetchall()
    total_feed = sum(r['quantity_kg'] for r in food_records)

    print("  [ FEEDING ]")
    if food_records:
        for r in food_records:
            print(f"  {r['food_type']:<15} | {r['quantity_kg']} kg")
        print(f"  Total Feed: {total_feed:.2f} kg")
    else:
        print("  No feed records.")

    print()

    # --- Expenses ---
    cursor.execute("SELECT * FROM expenses WHERE date = ?", (date,))
    expense_records = cursor.fetchall()
    total_expense = sum(r['amount'] for r in expense_records)

    print("  [ EXPENSES ]")
    if expense_records:
        for r in expense_records:
            print(f"  {r['category']:<15} | {r['amount']:.2f} | {r['description']}")
        print(f"  Total Expenses: {total_expense:.2f}")
    else:
        print("  No expenses.")

    print()

    # --- Sales ---
    cursor.execute("SELECT * FROM sales WHERE date = ?", (date,))
    sale_records = cursor.fetchall()
    total_sales = sum(r['total_amount'] for r in sale_records)

    print("  [ SALES ]")
    if sale_records:
        for r in sale_records:
            print(f"  {r['liters_sold']} L × {r['price_per_liter']} = {r['total_amount']:.2f}")
        print(f"  Total Revenue: {total_sales:.2f}")
    else:
        print("  No sales.")

    print()
    print_line("-")
    net = total_sales - total_expense
    print(f"  Net Profit/Loss for {date}: {'+' if net >= 0 else ''}{net:.2f}")

    conn.close()


# ---------------------------------------------------------
# Report 2: Monthly Report
# ---------------------------------------------------------
def monthly_report():
    """Generate a summary report for a full month."""
    print_header("MONTHLY REPORT")

    month = input("  Enter Month (YYYY-MM): ").strip()
    if not month or len(month) != 7:
        print("  [!] Invalid format. Use YYYY-MM.")
        return

    start = f"{month}-01"
    end   = f"{month}-31"

    conn   = get_connection()
    cursor = conn.cursor()

    print(f"\n  ===== MONTHLY REPORT: {month} =====\n")

    # Milk
    cursor.execute(
        "SELECT SUM(liters) as total, COUNT(*) as sessions FROM milk WHERE date BETWEEN ? AND ?",
        (start, end)
    )
    milk = cursor.fetchone()
    total_milk     = milk['total']    or 0.0
    milk_sessions  = milk['sessions'] or 0

    # Cows count
    cursor.execute("SELECT COUNT(*) as total FROM cows WHERE status = 'Active'")
    active_cows = cursor.fetchone()['total']

    # Expenses
    cursor.execute(
        "SELECT SUM(amount) as total FROM expenses WHERE date BETWEEN ? AND ?",
        (start, end)
    )
    exp = cursor.fetchone()
    total_expenses = exp['total'] or 0.0

    # Sales
    cursor.execute(
        "SELECT SUM(total_amount) as rev, SUM(liters_sold) as liters FROM sales WHERE date BETWEEN ? AND ?",
        (start, end)
    )
    sales = cursor.fetchone()
    total_revenue = sales['rev']    or 0.0
    liters_sold   = sales['liters'] or 0.0

    # Health events
    cursor.execute(
        "SELECT COUNT(*) as total FROM health WHERE date BETWEEN ? AND ?",
        (start, end)
    )
    health_events = cursor.fetchone()['total']

    conn.close()

    print(f"  Active Cows       : {active_cows}")
    print(f"  Milk Produced     : {total_milk:.2f} L ({milk_sessions} sessions)")
    print(f"  Milk Sold         : {liters_sold:.2f} L")
    print(f"  Total Revenue     : {total_revenue:.2f}")
    print(f"  Total Expenses    : {total_expenses:.2f}")
    print(f"  Health Events     : {health_events}")
    print_line("-")
    net = total_revenue - total_expenses
    print(f"  Net Profit / Loss : {'+' if net >= 0 else ''}{net:.2f}")


# ---------------------------------------------------------
# Report 3: Milk Production Report
# ---------------------------------------------------------
def milk_production_report():
    """Show milk production summary per cow over a date range."""
    print_header("MILK PRODUCTION REPORT")

    start = input("  Start Date (YYYY-MM-DD): ").strip()
    end   = input("  End Date   (YYYY-MM-DD): ").strip()

    if not start or not end:
        print("  [!] Both dates required.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name, SUM(m.liters) as total_liters, COUNT(*) as sessions
            FROM milk m
            JOIN cows c ON m.cow_id = c.id
            WHERE m.date BETWEEN ? AND ?
            GROUP BY m.cow_id
            ORDER BY total_liters DESC
        """, (start, end))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No milk records found for this period.")
            return

        print(f"\n  Period: {start} to {end}\n")
        print(f"  {'Cow Name':<20} {'Sessions':>10} {'Total (L)':>12}")
        print_line("-")
        grand_total = 0.0
        for row in rows:
            print(f"  {row['name']:<20} {row['sessions']:>10} {row['total_liters']:>12.2f}")
            grand_total += row['total_liters']
        print_line("-")
        print(f"  {'GRAND TOTAL':<20} {'':>10} {grand_total:>12.2f} L")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Report 4: Expense Report
# ---------------------------------------------------------
def expense_report():
    """Show expense breakdown by category over a date range."""
    print_header("EXPENSE REPORT")

    start = input("  Start Date (YYYY-MM-DD): ").strip()
    end   = input("  End Date   (YYYY-MM-DD): ").strip()

    if not start or not end:
        print("  [!] Both dates required.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
        """, (start, end))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No expenses found for this period.")
            return

        print(f"\n  Period: {start} to {end}\n")
        print(f"  {'Category':<15} {'Count':>8} {'Total Amount':>15}")
        print_line("-")
        grand_total = 0.0
        for row in rows:
            print(f"  {row['category']:<15} {row['count']:>8} {row['total']:>15.2f}")
            grand_total += row['total']
        print_line("-")
        print(f"  {'TOTAL':<15} {'':>8} {grand_total:>15.2f}")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Reports Menu
# ---------------------------------------------------------
def reports_menu():
    """Displays the Reports sub-menu."""
    while True:
        print_header("REPORTS")
        print("  1. Daily Report")
        print("  2. Monthly Report")
        print("  3. Milk Production Report")
        print("  4. Expense Report")
        print("  0. Back to Main Menu")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": daily_report()
        elif choice == "2": monthly_report()
        elif choice == "3": milk_production_report()
        elif choice == "4": expense_report()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
