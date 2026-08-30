# =============================================================
# models/cow.py - Cow Data Model
# =============================================================
# This file defines the Cow class.
# A "model" is just a Python class that represents one record
# in the database. It holds the data fields for a single cow.
# =============================================================


class Cow:
    """
    Represents a single cow on the farm.
    This class maps directly to the 'cows' table in the database.
    """

    def __init__(self, id=None, name="", breed="", age=0.0,
                 weight=0.0, gender="Female", color="",
                 purchase_date="", status="Active"):
        """
        Constructor – called when you create a new Cow object.

        Parameters:
            id            : Auto-assigned by the database
            name          : Cow's name (e.g. "Bella")
            breed         : Breed type (e.g. "Friesian")
            age           : Age in years
            weight        : Weight in kg
            gender        : "Female" or "Male"
            color         : Coat color
            purchase_date : Date the cow was bought (YYYY-MM-DD)
            status        : "Active", "Sold", "Dead", or "Sick"
        """
        self.id            = id
        self.name          = name
        self.breed         = breed
        self.age           = age
        self.weight        = weight
        self.gender        = gender
        self.color         = color
        self.purchase_date = purchase_date
        self.status        = status

    def __str__(self):
        """
        Returns a readable string when you print a Cow object.
        Example: print(cow)
        """
        return (
            f"ID: {self.id} | Name: {self.name} | Breed: {self.breed} | "
            f"Age: {self.age} yrs | Weight: {self.weight} kg | "
            f"Gender: {self.gender} | Status: {self.status}"
        )

    def to_dict(self):
        """
        Converts the cow object to a dictionary.
        Useful for displaying data in a table format.
        """
        return {
            "ID"           : self.id,
            "Name"         : self.name,
            "Breed"        : self.breed,
            "Age"          : self.age,
            "Weight (kg)"  : self.weight,
            "Gender"       : self.gender,
            "Color"        : self.color,
            "Purchase Date": self.purchase_date,
            "Status"       : self.status
        }
