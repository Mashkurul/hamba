class MilkRecord:
    """
    Represents a single daily milk production record for a cow.
    """
    def __init__(self, id=None, cow_id=None, date="",
                 liters=0.0, session="Morning", notes=""):
        """
        Constructor for MilkRecord.
        Parameters:
            id      : Auto-assigned by database
            cow_id  : ID of the cow that produced the milk
            date    : Date of collection (YYYY-MM-DD)
            liters  : Amount of milk collected in liters
            session : "Morning", "Afternoon", or "Evening"
            notes   : Any additional notes
        """
        self.id      = id
        self.cow_id  = cow_id
        self.date    = date
        self.liters  = liters
        self.session = session
        self.notes   = notes
    def __str__(self):
        return (
            f"ID: {self.id} | Cow ID: {self.cow_id} | Date: {self.date} | "
            f"Liters: {self.liters} | Session: {self.session}"
        )
    def to_dict(self):
        return {
            "ID"     : self.id,
            "Cow ID" : self.cow_id,
            "Date"   : self.date,
            "Liters" : self.liters,
            "Session": self.session,
            "Notes"  : self.notes
        }
