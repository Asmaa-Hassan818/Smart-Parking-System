class SubscriberManager:
    def __init__(self):
        self.subscribers = {}

    def add_subscriber(self, customer):
        self.subscribers[customer.user_id] = customer

    def remove_subscriber(self,customer_id):
        if customer_id in self.subscribers:
            del self.subscribers[customer_id]

    def search_subscriber(self,customer_id):
        return self.subscribers.get(customer_id)

    def view_subscribers(self):
        return self.subscribers
