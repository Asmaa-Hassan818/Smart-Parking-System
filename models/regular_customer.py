from models.customer import Customer

class RegularCustomer(Customer):
    def __init__(self, user_id, name, parking_lot):
        super().__init__(user_id, name)
        self.parking_lot = parking_lot
        self.vehicle = None
        self.ticket = None

    def park_vehicle(self,vehicle,entry_time):
        self.vehicle = vehicle
        self.ticket = self.parking_lot.assign_vehicle(vehicle,entry_time)
        return self.ticket

    def exit_vehicle(self,ticket_id, exit_time):
        return self.parking_lot.remove_vehicle(ticket_id, exit_time)

    def calculate_cost(self):
        return self.ticket.cost if self.ticket else 0

    def get_menu_options(self):
        return ["Park Vehicle", "Exit Vehicle", "Calculate Cost"]
