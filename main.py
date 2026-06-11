from models.parking_lot import ParkingLot
from models.parking_slot import ParkingSlot
from models.vehicle import vehicle
from models.customer import Customer
from models.regular_customer import RegularCustomer

# create parking lot
lot = ParkingLot(rate_per_hour=10)

# add slots
lot.add_slot(ParkingSlot(1))
lot.add_slot(ParkingSlot(2))

# create user
user = RegularCustomer(1, "Asmaa", lot)

# create vehicle
car = vehicle("123ABC", "car", "red")

# park
ticket = user.park_vehicle(car, entry_time=1)
print(ticket)

# exit
result = user.exit_vehicle(ticket.ticket_id, exit_time=5)
print(result)

# status
print(lot.display_status())