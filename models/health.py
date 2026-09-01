class HealthRecord:
    """
    Represents a single health/medical record for a cow.
    Can be a vaccination, disease, or medicine record.
    """
    def __init__(self, id=None, cow_id=None, date="",
                 record_type="", description="",
                 medicine="", vet_name="", cost=0.0):
        """
        Constructor for HealthRecord.
        Parameters:
            id          : Auto-assigned by database
            cow_id      : ID of the cow
            date        : Date of record (YYYY-MM-DD)
            record_type : "Vaccination", "Disease", "Medicine", "Checkup"
            description : Details about the health event
            medicine    : Name of medicine used (if any)
            vet_name    : Name of the veterinarian
            cost        : Cost of treatment
        """
        self.id          = id
        self.cow_id      = cow_id
        self.date        = date
        self.record_type = record_type
        self.description = description
        self.medicine    = medicine
        self.vet_name    = vet_name
        self.cost        = cost
    def __str__(self):
        return (
            f"ID: {self.id} | Cow ID: {self.cow_id} | Date: {self.date} | "
            f"Type: {self.record_type} | Description: {self.description}"
        )
    def to_dict(self):
        return {
            "ID"         : self.id,
            "Cow ID"     : self.cow_id,
            "Date"       : self.date,
            "Type"       : self.record_type,
            "Description": self.description,
            "Medicine"   : self.medicine,
            "Vet Name"   : self.vet_name,
            "Cost"       : self.cost
        }
