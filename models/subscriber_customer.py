from models.customer import Customer


class SubscriberCustomer(Customer):
    subscriber_counter = 1000

    def __init__(self, name, parking_lot, subscription_hours):
        SubscriberCustomer.subscriber_counter += 1
        user_id = f"SUB{SubscriberCustomer.subscriber_counter}"

        super().__init__(user_id, name)
        self.parking_lot = parking_lot
        self.subscription_hours = subscription_hours
        self.vehicle = None
        self.ticket = None
        self.parking_history = []   # list of dicts saved on each exit

    def park_vehicle(self, vehicle):
        self.vehicle = vehicle
        result = self.parking_lot.assign_vehicle(vehicle, customer=self)

        if result["status"] == "parked":
            self.ticket = result["ticket"]

        return result

    def exit_vehicle(self, ticket_id):
        """
        Subscriber exit logic:
        - duration is calculated by the parking lot
        - if subscription_hours >= duration  -> fully covered, cost = 0
        - if subscription_hours <  duration  -> use up all remaining hours,
          charge for the extra hours at rate_per_hour
        """
        result = self.parking_lot.remove_vehicle(ticket_id)

        if result["status"] == "error":
            return result["message"]

        ticket = result["ticket"]
        duration = ticket.duration

        if self.subscription_hours >= duration:
            self.subscription_hours -= duration
            ticket.cost = 0
            message = (
                f"{ticket.display_info()}\n"
                f"Covered by subscription. No payment required.\n"
                f"Remaining subscription hours: {round(self.subscription_hours, 2)}"
            )
        else:
            extra_hours = duration - self.subscription_hours
            self.subscription_hours = 0
            ticket.cost = round(extra_hours * self.parking_lot.rate_per_hour, 2)
            message = (
                f"{ticket.display_info()}\n"
                f"Subscription hours used up.\n"
                f"Extra hours: {round(extra_hours, 4)} -> Pay {ticket.cost} EGP\n"
                f"Remaining subscription hours: 0"
            )

        self.parking_history.append({
            "ticket_id":  ticket.ticket_id,
            "plate":      ticket.vehicle.plate_num,
            "slot":       ticket.slot_id,
            "entry":      ticket.entry_time,
            "exit":       ticket.exit_time,
            "duration":   round(duration, 4),
            "cost":       ticket.cost,
        })

        return {
            "status": "done",
            "ticket": ticket,
            "message": message
        }

    def check_balance(self):
        return self.subscription_hours

    def get_menu_options(self):
        return [
            "Park Vehicle",
            "Exit Vehicle",
            "Check Balance"
        ]


class SubscriberManager:
    def __init__(self):
        self.subscribers = {}

    def add_subscriber(self, customer):
        self.subscribers[customer.user_id] = customer

    def remove_subscriber(self, customer_id):
        if customer_id in self.subscribers:
            del self.subscribers[customer_id]

    def search_subscriber(self, customer_id):
        return self.subscribers.get(customer_id)

    def view_subscribers(self):
        return self.subscribers