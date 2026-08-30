# =============================================================
# modules/employee_management.py - Employee Management Module
# =============================================================
# Handles all employee-related operations:
#   - Add Employee
#   - View Employees
#   - Mark Attendance
#   - View Attendance
#   - Salary Info
#   - Delete Employee
# =============================================================

from database import get_connection
from config import (print_header, print_line,
                    EMPLOYEE_ROLES, ATTENDANCE_STATUS)


def get_today():
    from datetime import date
    return str(date.today())


def pick_option(prompt, options):
    print(f"\n  {prompt}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        choice = input("  Enter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("  [!] Invalid choice.")


def print_employee_row(emp):
    print(f"""
  ID        : {emp['id']}
  Name      : {emp['name']}
  Role      : {emp['role']}
  Phone     : {emp['phone']}
  Salary    : {emp['salary']}
  Join Date : {emp['join_date']}
  Status    : {emp['status']}""")
    print_line("-")


# ---------------------------------------------------------
# Feature 1: Add employee
# ---------------------------------------------------------
def add_employee():
    """Add a new employee to the system."""
    print_header("ADD EMPLOYEE")

    name = input("  Full Name  : ").strip()
    if not name:
        print("  [!] Name cannot be empty.")
        return

    role  = pick_option("Select Role:", EMPLOYEE_ROLES)
    phone = input("  Phone Number: ").strip()

    while True:
        salary_input = input("  Monthly Salary: ").strip()
        try:
            salary = float(salary_input) if salary_input else 0.0
            break
        except ValueError:
            print("  [!] Enter a valid number.")

    join_date = input(f"  Join Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employees (name, role, phone, salary, join_date, status)
            VALUES (?, ?, ?, ?, ?, 'Active')
        """, (name, role, phone, salary, join_date))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        print(f"\n  [OK] Employee '{name}' added successfully! (ID: {new_id})")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 2: View all employees
# ---------------------------------------------------------
def view_employees():
    """Display all employees."""
    print_header("ALL EMPLOYEES")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY id")
        employees = cursor.fetchall()
        conn.close()

        if not employees:
            print("  No employees found.")
            return

        print(f"  Total employees: {len(employees)}\n")
        for emp in employees:
            print_employee_row(emp)

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 3: Mark attendance
# ---------------------------------------------------------
def mark_attendance():
    """Record today's attendance for an employee."""
    print_header("MARK ATTENDANCE")

    emp_id_input = input("  Employee ID: ").strip()
    if not emp_id_input.isdigit():
        print("  [!] Invalid ID.")
        return
    emp_id = int(emp_id_input)

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM employees WHERE id = ?", (emp_id,))
    emp = cursor.fetchone()
    if not emp:
        print(f"  [!] No employee found with ID {emp_id}.")
        conn.close()
        return

    date   = input(f"  Date (YYYY-MM-DD) [{get_today()}]: ").strip() or get_today()
    status = pick_option("Select Attendance Status:", ATTENDANCE_STATUS)

    try:
        cursor.execute("""
            INSERT INTO attendance (employee_id, date, status)
            VALUES (?, ?, ?)
        """, (emp_id, date, status))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Attendance marked: {emp['name']} – {status} on {date}.")
    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 4: View attendance records
# ---------------------------------------------------------
def view_attendance():
    """View attendance records for all or a specific employee."""
    print_header("ATTENDANCE RECORDS")

    emp_id_input = input("  Employee ID (or press ENTER for all): ").strip()

    try:
        conn   = get_connection()
        cursor = conn.cursor()

        if emp_id_input.isdigit():
            cursor.execute("""
                SELECT a.*, e.name as emp_name
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                WHERE a.employee_id = ?
                ORDER BY a.date DESC
            """, (int(emp_id_input),))
        else:
            cursor.execute("""
                SELECT a.*, e.name as emp_name
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                ORDER BY a.date DESC
            """)

        records = cursor.fetchall()
        conn.close()

        if not records:
            print("  No attendance records found.")
            return

        for r in records:
            print(f"  ID: {r['id']} | Employee: {r['emp_name']} | "
                  f"Date: {r['date']} | Status: {r['status']}")
        print_line("-")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 5: View salary summary
# ---------------------------------------------------------
def view_salary():
    """Show salary information for all employees."""
    print_header("SALARY INFORMATION")

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, salary, status FROM employees ORDER BY id")
        employees = cursor.fetchall()
        conn.close()

        if not employees:
            print("  No employees found.")
            return

        total_salary = 0.0
        print(f"  {'ID':<5} {'Name':<20} {'Role':<15} {'Salary':>10} {'Status':<10}")
        print_line("-")
        for emp in employees:
            print(f"  {emp['id']:<5} {emp['name']:<20} {emp['role']:<15} "
                  f"{emp['salary']:>10.2f} {emp['status']:<10}")
            total_salary += emp['salary']

        print_line("-")
        print(f"  Total Monthly Payroll: {total_salary:.2f}")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Feature 6: Delete employee
# ---------------------------------------------------------
def delete_employee():
    """Delete an employee record."""
    print_header("DELETE EMPLOYEE")

    emp_id = input("  Enter Employee ID to delete: ").strip()
    if not emp_id.isdigit():
        print("  [!] Invalid ID.")
        return

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (int(emp_id),))
        emp = cursor.fetchone()

        if not emp:
            print(f"  [!] No employee found with ID {emp_id}.")
            conn.close()
            return

        confirm = input(f"  Delete '{emp['name']}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("  [!] Cancelled.")
            conn.close()
            return

        cursor.execute("DELETE FROM employees WHERE id = ?", (int(emp_id),))
        conn.commit()
        conn.close()
        print(f"\n  [OK] Employee '{emp['name']}' deleted.")

    except Exception as e:
        print(f"  [ERROR]: {e}")


# ---------------------------------------------------------
# Employee Management Menu
# ---------------------------------------------------------
def employee_menu():
    """Displays the Employee Management sub-menu."""
    while True:
        print_header("EMPLOYEE MANAGEMENT")
        print("  1. Add Employee")
        print("  2. View All Employees")
        print("  3. Mark Attendance")
        print("  4. View Attendance")
        print("  5. Salary Information")
        print("  6. Delete Employee")
        print("  0. Back to Main Menu")
        print_line()

        choice = input("  Select option: ").strip()

        if   choice == "1": add_employee()
        elif choice == "2": view_employees()
        elif choice == "3": mark_attendance()
        elif choice == "4": view_attendance()
        elif choice == "5": view_salary()
        elif choice == "6": delete_employee()
        elif choice == "0": break
        else: print("  [!] Invalid option.")
