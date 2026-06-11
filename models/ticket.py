
class Ticket:
    def __init__(self,ticket_id,vehicle,slot_id,entry_time):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.slot_id = slot_id
        self.entry_time = entry_time
        self.exit_time = None
        self.duration = 0
        self.cost = 0

    def calculate_duration(self,exit_time):
        self.exit_time = exit_time
        self.duration = self.exit_time - self.entry_time
        return self.duration

    def calculate_cost(self,rate_per_hour):
        self.cost = self.duration * rate_per_hour
        return self.cost

    def display_info(self):
        return f"""
    Ticket Info:
    Ticket ID : {self.ticket_id}
    Vehicle   : {self.vehicle.plate_num}
    Slot      : {self.slot_id}
    Entry     : {self.entry_time}
    Exit      : {self.exit_time}
    Duration  : {self.duration} hours
    Cost      : {self.cost} EGP
    """
