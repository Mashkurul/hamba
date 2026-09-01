class Expense:
    """
    Represents a single farm expense record.
    """
    def __init__(self, id=None, date="", category="",
                 amount=0.0, description=""):
        """
        Constructor for Expense.
        Parameters:
            id          : Auto-assigned by database
            date        : Date of expense (YYYY-MM-DD)
            category    : Category (e.g. "Feed", "Medicine", "Salary")
            amount      : Amount spent
            description : Details about the expense
        """
        self.id          = id
        self.date        = date
        self.category    = category
        self.amount      = amount
        self.description = description
    def __str__(self):
        return (
            f"ID: {self.id} | Date: {self.date} | Category: {self.category} | "
            f"Amount: {self.amount} | {self.description}"
        )
    def to_dict(self):
        return {
            "ID"         : self.id,
            "Date"       : self.date,
            "Category"   : self.category,
            "Amount"     : self.amount,
            "Description": self.description
        }
class Sale:
    """
    Represents a single milk sale transaction.
    """
    def __init__(self, id=None, date="", liters_sold=0.0,
                 price_per_liter=0.0, total_amount=0.0,
                 buyer_name="", notes=""):
        """
        Constructor for Sale.
        Parameters:
            id              : Auto-assigned by database
            date            : Date of sale (YYYY-MM-DD)
            liters_sold     : How many liters were sold
            price_per_liter : Price per liter
            total_amount    : liters_sold * price_per_liter
            buyer_name      : Name of the buyer
            notes           : Any additional notes
        """
        self.id              = id
        self.date            = date
        self.liters_sold     = liters_sold
        self.price_per_liter = price_per_liter
        self.total_amount    = total_amount
        self.buyer_name      = buyer_name
        self.notes           = notes
    def __str__(self):
        return (
            f"ID: {self.id} | Date: {self.date} | Liters: {self.liters_sold} | "
            f"Price/L: {self.price_per_liter} | Total: {self.total_amount} | "
            f"Buyer: {self.buyer_name}"
        )
    def to_dict(self):
        return {
            "ID"             : self.id,
            "Date"           : self.date,
            "Liters Sold"    : self.liters_sold,
            "Price/Liter"    : self.price_per_liter,
            "Total Amount"   : self.total_amount,
            "Buyer"          : self.buyer_name,
            "Notes"          : self.notes
        }
