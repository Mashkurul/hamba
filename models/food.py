# =============================================================
# models/food.py - Food / Feed Record Data Model
# =============================================================
# Defines the FoodRecord class which maps to the 'food'
# table in the database.
# =============================================================


class FoodRecord:
    """
    Represents a single feed/food record for the farm.
    Could be a stock entry or a daily feeding record.
    """

    def __init__(self, id=None, food_type="", quantity_kg=0.0,
                 date="", cow_id=None, notes=""):
        """
        Constructor for FoodRecord.

        Parameters:
            id          : Auto-assigned by database
            food_type   : Type of food (e.g. "Hay", "Grass")
            quantity_kg : Quantity in kilograms
            date        : Date of feeding or stock entry (YYYY-MM-DD)
            cow_id      : ID of cow (optional – if feeding a specific cow)
            notes       : Any additional notes
        """
        self.id          = id
        self.food_type   = food_type
        self.quantity_kg = quantity_kg
        self.date        = date
        self.cow_id      = cow_id
        self.notes       = notes

    def __str__(self):
        return (
            f"ID: {self.id} | Type: {self.food_type} | "
            f"Qty: {self.quantity_kg} kg | Date: {self.date} | Cow ID: {self.cow_id}"
        )

    def to_dict(self):
        return {
            "ID"         : self.id,
            "Food Type"  : self.food_type,
            "Quantity kg": self.quantity_kg,
            "Date"       : self.date,
            "Cow ID"     : self.cow_id,
            "Notes"      : self.notes
        }
