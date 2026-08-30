# =============================================================
# models/employee.py - Employee Data Model
# =============================================================
# Defines the Employee class which maps to the 'employees'
# table in the database.
# =============================================================


class Employee:
    """
    Represents a single farm employee/worker.
    """

    def __init__(self, id=None, name="", role="",
                 phone="", salary=0.0, join_date="", status="Active"):
        """
        Constructor for Employee.

        Parameters:
            id        : Auto-assigned by the database
            name      : Employee full name
            role      : Job role (e.g. "Farmer", "Veterinarian")
            phone     : Contact number
            salary    : Monthly salary amount
            join_date : Date joined (YYYY-MM-DD)
            status    : "Active" or "Inactive"
        """
        self.id        = id
        self.name      = name
        self.role      = role
        self.phone     = phone
        self.salary    = salary
        self.join_date = join_date
        self.status    = status

    def __str__(self):
        return (
            f"ID: {self.id} | Name: {self.name} | Role: {self.role} | "
            f"Phone: {self.phone} | Salary: {self.salary} | Status: {self.status}"
        )

    def to_dict(self):
        return {
            "ID"       : self.id,
            "Name"     : self.name,
            "Role"     : self.role,
            "Phone"    : self.phone,
            "Salary"   : self.salary,
            "Join Date": self.join_date,
            "Status"   : self.status
        }
