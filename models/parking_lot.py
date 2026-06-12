from collections import deque
from models.ticket import Ticket
from models.parking_slot import ParkingSlot


class ParkingLot:
    def __init__(self, rate_per_hour=10):
        self.slots = []
        self.parked_vehicles = {}      # ticket_id -> Ticket
        self.waiting_queue = deque()   # holds tuples: (customer, vehicle)
        self.rate_per_hour = rate_per_hour
        self.ticket_counter = 1000

    def add_slot(self, slot: ParkingSlot):
        self.slots.append(slot)

    def find_ava_slot(self):
        for slot in self.slots:
            if not slot.is_occupied:
                return slot
        return None

    def check_plate_number(self, plate_num):
        for ticket in self.parked_vehicles.values():
            if ticket.vehicle.plate_num == plate_num:
                return True
        return False

    def create_ticket(self, vehicle, slot_id):
        ticket_id = f"T{self.ticket_counter}"
        self.ticket_counter += 1
        return Ticket(
            ticket_id=ticket_id,
            vehicle=vehicle,
            slot_id=slot_id,
        )

    def assign_vehicle(self, vehicle, customer=None):
        """
        Tries to park the vehicle.
        Returns a dict ALWAYS with a "status" key:
          - status="parked" -> "ticket": Ticket object
          - status="queue"  -> "message": str
          - status="error"  -> "message": str
        """
        if self.check_plate_number(vehicle.plate_num):
            return {
                "status": "error",
                "message": "Vehicle already parked"
            }

        slot = self.find_ava_slot()

        if slot:
            slot.assign_vehicle(vehicle)
            ticket = self.create_ticket(vehicle, slot.slot_id)
            self.parked_vehicles[ticket.ticket_id] = ticket

            return {
                "status": "parked",
                "ticket": ticket
            }
        else:
            self.waiting_queue.append((customer, vehicle))
            return {
                "status": "queue",
                "message": f"Garage full. Added to waiting queue (position {len(self.waiting_queue)})"
            }

    def remove_vehicle(self, ticket_id):
        """
        Always returns a dict with "status":
          - status="error" -> "message"
          - status="done"  -> "ticket": Ticket object (with duration & cost calculated)
        """
        if ticket_id not in self.parked_vehicles:
            return {
                "status": "error",
                "message": "Ticket not found"
            }

        ticket = self.parked_vehicles[ticket_id]

        ticket.calculate_duration()
        ticket.calculate_cost(self.rate_per_hour)

        for slot in self.slots:
            if slot.slot_id == ticket.slot_id:
                slot.remove_vehicle()
                break

        del self.parked_vehicles[ticket_id]

        queue_result = self.process_waiting_queue()

        return {
            "status": "done",
            "ticket": ticket,
            "cost": ticket.cost,
            "queue_processed": queue_result
        }

    def process_waiting_queue(self):
        """
        If a slot is free and someone is waiting, assign them automatically.
        Returns the new Ticket if someone moved from queue -> parked, else None.
        """
        slot = self.find_ava_slot()

        if slot and self.waiting_queue:
            customer, vehicle = self.waiting_queue.popleft()

            slot.assign_vehicle(vehicle)
            ticket = self.create_ticket(vehicle, slot.slot_id)
            self.parked_vehicles[ticket.ticket_id] = ticket

            if customer is not None:
                customer.ticket = ticket

            return ticket

        return None

    def display_status(self):
        occupied = sum(1 for s in self.slots if s.is_occupied)
        total = len(self.slots)

        return {
            "total_slots": total,
            "occupied": occupied,
            "available": total - occupied,
            "waiting": len(self.waiting_queue)
        }