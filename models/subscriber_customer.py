from models.customer import Customer

class SubscriberCustomer(Customer):
    def __init__(self, user_id, name, parking_lot, subscription_hours):
        super().__init__(user_id, name)
        self.parking_lot = parking_lot
        self.subscription_hours = subscription_hours

    def park_vehicle(self, vehicle, entry_time):
        return self.parking_lot.assign_vehicle(vehicle,entry_time)

    def exit_vehicle(self, ticket_id, exit_time):

        ticket = self.parking_lot.remove_vehicle(ticket_id, exit_time)

        duration = ticket.duration

        if self.subscription_hours >= duration:
            self.subscription_hours -= duration
            ticket.cost = 0  # free
            return "Covered by subscription"

        else:
            remaining = duration - self.subscription_hours
            self.subscription_hours = 0

            ticket.cost = remaining * self.parking_lot.rate_per_hour
            return f"Pay {ticket.cost} EGP"

    def check_balance(self):
        return self.subscription_hours

    def get_menu_options(self):
        return [
            "Park Vehicle",
            "Exit Vehicle",
            "Check Balance"
        ]

