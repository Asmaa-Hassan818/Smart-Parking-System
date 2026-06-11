from models.user import User

class Admin(User):
    def __init__(self,admin_id,user_id, name ,subscriber_manager, parking_lot):
        super().__init__(user_id, name)
        self.admin_id = admin_id
        self.subscriber_manager = subscriber_manager
        self.parking_lot = parking_lot

    def view_parking_map(self):
        return self.parking_lot.display_status()

    def view_all_vehicles(self):
        return self.parking_lot.parked_vehicles

    def view_waiting_queue(self):
        return list(self.parking_lot.waiting_queue)

    def add_subscriber(self, customer):
        self.subscriber_manager.add_subscriber(customer)

    def remove_subscriber(self, customer_id):
        self.subscriber_manager.remove_subscriber(customer_id)

    def search_subscriber(self, customer_id):
        return self.subscriber_manager.search_subscriber(customer_id)

    def view_subscribers(self):
        return self.subscriber_manager.subscribers

    def get_menu_options(self):
        return [
            "View Parking Map",
            "View All Vehicles",
            "View Waiting Queue",
            "Manage Subscribers"
        ]



