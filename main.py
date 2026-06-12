from models.parking_lot import ParkingLot
from models.parking_slot import ParkingSlot
from models.vehicle import vehicle
from models.subscriber_customer import SubscriberCustomer
from datetime import timedelta


def get_ticket(result):
    if isinstance(result, dict) and "ticket" in result:
        return result["ticket"]
    return None


def print_result(result):
    print(result)


print("\n================ INIT PARKING LOT ================\n")

parking = ParkingLot(rate_per_hour=10)

print(parking.display_status())


# ==================================================
# ADD SLOTS
# ==================================================
print("\n================ ADD SLOTS ================\n")

parking.add_slot(ParkingSlot("A1"))
parking.add_slot(ParkingSlot("A2"))
parking.add_slot(ParkingSlot("A3"))

print(parking.display_status())


# ==================================================
# SUBSCRIBER SETUP
# ==================================================
print("\n================ SUBSCRIBER TESTS ================\n")

sub = SubscriberCustomer("Ahmed", parking, 10)


# ==================================================
# CASE 1: ENOUGH HOURS
# ==================================================
print("\n--- CASE 1: Enough Subscription Hours ---\n")

v1 = vehicle("SUB1", "Car", "Black")
r1 = sub.park_vehicle(v1)

t1 = get_ticket(r1)

if t1:
    # simulate 2 hours usage
    t1.entry_time -= timedelta(hours=2)

    result = sub.exit_vehicle(t1.ticket_id)
    print(result["message"])
else:
    print_result(r1)


# ==================================================
# CASE 2: NOT ENOUGH HOURS
# ==================================================
print("\n--- CASE 2: Not Enough Subscription Hours ---\n")

sub.subscription_hours = 1  # reset small balance

v2 = vehicle("SUB2", "Car", "White")
r2 = sub.park_vehicle(v2)

t2 = get_ticket(r2)

if t2:
    # simulate 3 hours usage
    t2.entry_time -= timedelta(hours=3)

    result = sub.exit_vehicle(t2.ticket_id)
    print(result["message"])
else:
    print_result(r2)


# ==================================================
# STATUS CHECK
# ==================================================
print("\n================ FINAL STATUS ================\n")

print(parking.display_status())

print("\n================ DONE ================\n")