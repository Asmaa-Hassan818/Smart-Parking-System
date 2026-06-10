class Parking_slot:
    def __init__(self,slot_id):
        self.slot_id = slot_id
        self.is_occupied = False
        self.vechile = None

    def assign_vechile(self,vehicle):
        self.vechile = vehicle
        self.is_occupied = True

    def remove_vechile(self,vehicle):
        self.vechile = None
        self.is_occupied = False
    def display_info(self):
        if self.is_occupied:
            status = "Occupied"
        else:
            status = "Available"
        return f"Slot {self.slot_id} - {status}"