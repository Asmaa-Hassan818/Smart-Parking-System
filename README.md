# 🅿️ Smart Parking System

A desktop parking management application built with Python and CustomTkinter, demonstrating core Object-Oriented Programming principles, data structures, and GUI design.

---

##  Features

| Feature | Description |
|---|---|
| **Role-based access** | Separate flows for Admin, Subscriber, and Regular Customer |
| **Live parking map** | Visual grid of all slots with real-time occupancy status |
| **FIFO waiting queue** | Vehicles auto-assigned when a slot frees up (`collections.deque`) |
| **Subscription billing** | Hours deducted from balance; extra hours charged at hourly rate |
| **Admin dashboard** | Live stats, activity log, subscriber management, and queue monitor |
| **Animated UI** | Particle background, fade-in transitions, pulsing live indicator |

---

##  Project Structure

```
Smart-Parking-System/
│
├── main.py                        # Entry point — builds ParkingLot & SubscriberManager, launches GUI
│
├── models/                        # Business logic (pure Python, no GUI)
│   ├── user.py                    # Abstract base class User (ABC)
│   ├── customer.py                # Customer(User) — abstract park/exit interface
│   ├── regular_customer.py        # RegularCustomer — pay per hour
│   ├── subscriber_customer.py     # SubscriberCustomer — deducts from subscription balance
│   ├── admin.py                   # Admin — manages lot, subscribers, and queue
│   ├── parking_lot.py             # Core logic: slot assignment, queue, ticket lifecycle
│   ├── parking_slot.py            # Individual slot state
│   ├── ticket.py                  # Ticket with entry/exit time and cost calculation
│   ├── vehicle.py                 # Vehicle data (plate, type, color)
│   └── SubscriberManager.py       # CRUD for subscriber registry
│
├── gui/                           # CustomTkinter screens
│   ├── start_screen.py            # Landing screen with role-selection cards
│   ├── adminLogin.py              # Admin ID authentication screen
│   ├── admin_dashboard.py         # Full admin dashboard (stats, map, popups)
│   ├── subscriberLogin.py         # Subscriber ID login screen
│   ├── subscriber_screen.py       # Subscriber park / exit / balance screen
│   └── regular_screen.py          # Regular customer park / exit screen
│
├── Class_diagram.jpg              # UML Class Diagram
├── requirements.txt               # Python dependencies
└── README.md
```

---

##  OOP Design

```
User (ABC)
├── Customer (ABC)
│   ├── RegularCustomer      — park, exit, calculate cost
│   └── SubscriberCustomer   — park, exit with subscription deduction, check balance
└── Admin                    — view/manage lot, queue, and subscribers
```

**Key OOP concepts applied:**
- **Abstraction** — `User` and `Customer` are abstract classes with `@abstractmethod`
- **Inheritance** — 4-level hierarchy from `User` down to concrete customer types
- **Encapsulation** — all state and logic contained within each class
- **Polymorphism** — `park_vehicle()` and `exit_vehicle()` behave differently per customer type

---

##  Data Structures

| Structure | Used For | Why |
|---|---|---|
| `list` | `ParkingLot.slots` | Ordered slot storage, iterate to find first free |
| `dict` | `ParkingLot.parked_vehicles` | O(1) ticket lookup by ticket ID |
| `collections.deque` | `ParkingLot.waiting_queue` | FIFO queue — O(1) append and popleft |
| `dict` | `SubscriberManager.subscribers` | O(1) subscriber lookup by user ID |

---

##  Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/Asmaa-Hassan818/Smart-Parking-System.git
cd Smart-Parking-System
pip install -r requirements.txt
python main.py
```

### Demo Credentials

| Role | ID |
|---|---|
| Admin | `ADM001`, `ADM002`, `ADM003` |
| Subscriber | `SUB1001`, `SUB1002`, `SUB1003` |

---

##  Screenshots

| Start Screen | Admin Dashboard |
|---|---|
| Role selection with animated particle background | Live stats, parking map, queue monitor |

---

## ️ How It Works

### Parking Flow
1. Customer enters plate number and vehicle details.
2. `ParkingLot.assign_vehicle()` checks for duplicate plates, finds a free slot, and issues a `Ticket`.
3. If the lot is full, the vehicle is added to the `waiting_queue`.
4. On exit, `remove_vehicle()` calculates duration and cost, frees the slot, and automatically assigns the next vehicle from the queue.

### Subscriber Billing
```
if subscription_hours >= duration:
    cost = 0                          # fully covered
else:
    extra = duration - subscription_hours
    cost  = extra × rate_per_hour     # charge only the overage
    subscription_hours = 0
```

---

##  Dependencies

```
customtkinter
```

---

