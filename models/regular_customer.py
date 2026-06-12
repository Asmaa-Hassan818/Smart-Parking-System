from models.customer import Customer


class RegularCustomer(Customer):
    customer_counter = 1000

    def __init__(self, name, parking_lot):
        user_id = f"REG{RegularCustomer.customer_counter}"
        RegularCustomer.customer_counter += 1

        super().__init__(user_id, name)
        self.parking_lot = parking_lot
        self.vehicle = None
        self.ticket = None

    def park_vehicle(self, vehicle):
        self.vehicle = vehicle
        result = self.parking_lot.assign_vehicle(vehicle, customer=self)

        if result["status"] == "parked":
            self.ticket = result["ticket"]

        return result

    def exit_vehicle(self, ticket_id):
        result = self.parking_lot.remove_vehicle(ticket_id)

        if result["status"] == "error":
            return result["message"]

        self.ticket = result["ticket"]
        return result

    def calculate_cost(self):
        return self.ticket.cost if self.ticket else 0

    def get_menu_options(self):
        return ["Park Vehicle", "Exit Vehicle", "Calculate Cost"]