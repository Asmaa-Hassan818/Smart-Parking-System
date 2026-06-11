from collections import deque
from models.ticket import Ticket
from models.parking_slot import ParkingSlot
from models.subscriber_customer import SubscriberCustomer

class ParkingLot:
    def __init__(self, rate_per_hour=10):
        self.slots = []
        self.parked_vehicles = {}
        self.waiting_queue = deque()
        self.rate_per_hour = rate_per_hour

    def add_slot(self, slot: ParkingSlot):
        self.slots.append(slot)

    def find_ava_slot(self):
        for slot in self.slots:
            if not slot.is_occupied:
                return slot
        return None

    def check_plate_number(self, plate_number):
        for ticket in self.parked_vehicles.values():
            if ticket.vehicle.plate_num == plate_number:
                return True
        return False

    def create_ticket(self, vehicle, slot_id, entry_time):
        if Ticket.is_subscriber:
            return None
        else:
            ticket_id = "T" + str(len(self.parked_vehicles) + 1000)

        return Ticket(
            ticket_id=ticket_id,
            vehicle=vehicle,
            slot_id=slot_id,
            entry_time=entry_time
        )

    def assign_vehicle(self, vehicle, entry_time , is_subscriber = False):

        if self.check_plate_number(vehicle.plate_number):
            return "Vehicle already parked"

        slot = self.find_ava_slot()

        if slot:
            slot.assign_vehicle(vehicle)

            ticket = self.create_ticket(vehicle, slot.slot_id, entry_time)

            self.parked_vehicles[ticket.ticket_id] = ticket

            return ticket

        else:
            self.waiting_queue.append(vehicle)
            return "No slots available. Added to waiting queue"

    def remove_vehicle(self, ticket_id, exit_time):

        if ticket_id not in self.parked_vehicles:
            return "Ticket not found"

        ticket = self.parked_vehicles[ticket_id]

        ticket.calculate_duration(exit_time)
        ticket.calculate_cost(self.rate_per_hour)

        for slot in self.slots:
            if slot.slot_id == ticket.slot_id:
                slot.remove_vehicle()
                break

        del self.parked_vehicles[ticket_id]

        self.process_waiting_queue()

        return ticket

    def process_waiting_queue(self):

        slot = self.find_ava_slot()

        if slot and self.waiting_queue:
            vehicle = self.waiting_queue.popleft()

            slot.assign_vehicle(vehicle)

            ticket = self.create_ticket(vehicle, slot.slot_id, entry_time=0)

            self.parked_vehicles[ticket.ticket_id] = ticket

    def display_status(self):
        occupied = sum(1 for s in self.slots if s.is_occupied)
        total = len(self.slots)

        return {
            "total_slots": total,
            "occupied": occupied,
            "available": total - occupied,
            "waiting": len(self.waiting_queue)
        }
