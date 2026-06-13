from models.parking_lot import ParkingLot
from models.parking_slot import ParkingSlot
from models.subscriber_customer import SubscriberCustomer, SubscriberManager

from gui.start_screen import StartScreen


def build_parking_lot():
    lot = ParkingLot(rate_per_hour=10)
    for row in ["A", "B"]:
        for num in range(1, 6):
            lot.add_slot(ParkingSlot(slot_id=f"{row}{num}"))
    return lot


def build_subscriber_manager(parking_lot):
    manager = SubscriberManager()
    test_subs = [
        ("Asmaa", 20),
        ("Sara",  15),
        ("Ahmed",  5),
    ]
    for name, hours in test_subs:
        sub = SubscriberCustomer(name=name, parking_lot=parking_lot,
                                 subscription_hours=hours)
        manager.add_subscriber(sub)
        print(f"[INIT] Subscriber: {sub.user_id} - {sub.name}")
    return manager


if __name__ == "__main__":
    parking_lot        = build_parking_lot()
    subscriber_manager = build_subscriber_manager(parking_lot)

    app = StartScreen(parking_lot=parking_lot,
                      subscriber_manager=subscriber_manager)
    app.mainloop()
