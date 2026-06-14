import customtkinter as ctk
import math
import random

from models.admin import Admin
from models.parking_lot import ParkingLot
from models.parking_slot import ParkingSlot
from models.subscriber_customer import SubscriberCustomer, SubscriberManager
from models.vehicle import vehicle

ctk.set_appearance_mode("dark")

BG_COLOR       = "#0b0f1a"
PANEL_COLOR    = "#121829"
PANEL_BORDER   = "#1f2a44"
NEON_BLUE      = "#3ad6ff"
NEON_GREEN     = "#39ffb0"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"
SLOT_FREE      = "#173a2f"
SLOT_FREE_BD   = NEON_GREEN
SLOT_OCC       = "#3a1f25"
SLOT_OCC_BD    = "#ff6b6b"
WARN_COLOR     = "#ffd166"
DANGER_COLOR   = "#ff6b6b"



class ParticleOverlay(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.particles = []
        self.bind("<Configure>", self._on_resize)
        self._ready = False

    def _on_resize(self, event):
        if not self._ready:
            self._ready = True
            self._build(event.width, event.height)
            self._animate()

    def _build(self, w, h):
        for _ in range(35):
            x = random.uniform(0, w); y = random.uniform(0, h)
            r = random.uniform(1.2, 3); speed = random.uniform(0.25, 0.8)
            color = random.choice([NEON_BLUE, NEON_GREEN])
            item = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            self.particles.append({"id": item, "speed": speed,
                                   "phase": random.uniform(0, math.tau)})

    def _animate(self):
        h = self.winfo_height()
        for p in self.particles:
            p["phase"] += 0.03
            self.move(p["id"], math.sin(p["phase"]) * 0.4, -p["speed"])
            coords = self.coords(p["id"])
            if coords and coords[1] < -5:
                self.move(p["id"], 0, h + 10)
        try:
            self.after(40, self._animate)
        except Exception:
            return


class GlassFrame(ctk.CTkFrame):
    def __init__(self, master, accent=NEON_BLUE, **kwargs):
        kwargs.setdefault("corner_radius", 18)
        kwargs.setdefault("fg_color", PANEL_COLOR)
        kwargs.setdefault("border_width", 1.5)
        kwargs.setdefault("border_color", PANEL_BORDER)
        super().__init__(master, **kwargs)
        self.accent = accent


class StatCard(GlassFrame):
    def __init__(self, master, icon, value, label, accent=NEON_BLUE):
        super().__init__(master, accent=accent, height=110)
        self.grid_propagate(False)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))
        icon_box = ctk.CTkFrame(top, width=42, height=42, corner_radius=12,
                                fg_color="#0c1830", border_width=1.5,
                                border_color=accent)
        icon_box.pack(side="left"); icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon,
                     font=("Segoe UI Emoji", 18)).place(relx=.5, rely=.5, anchor="center")
        self.value_label = ctk.CTkLabel(top, text=str(value),
                                        font=("Segoe UI", 26, "bold"),
                                        text_color=TEXT_PRIMARY)
        self.value_label.pack(side="right")
        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=18, pady=(6, 14))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


class NavButton(ctk.CTkButton):
    def __init__(self, master, icon, text, command=None, active=False):
        super().__init__(
            master, text=f"  {icon}   {text}", anchor="w",
            font=("Segoe UI", 13, "bold" if active else "normal"),
            height=44, corner_radius=12,
            fg_color="#16263f" if active else "transparent",
            hover_color="#16263f",
            text_color=NEON_BLUE if active else TEXT_SECONDARY,
            border_width=1.5 if active else 0,
            border_color=NEON_BLUE, command=command)
        self._active = active
        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)

    def set_active(self, state: bool):
        self._active = state
        self.configure(
            fg_color="#16263f" if state else "transparent",
            text_color=NEON_BLUE if state else TEXT_SECONDARY,
            border_width=1.5 if state else 0,
            font=("Segoe UI", 13, "bold" if state else "normal"))

    def _hover_on(self, _=None):
        if not self._active: self.configure(text_color=TEXT_PRIMARY)

    def _hover_off(self, _=None):
        if not self._active: self.configure(text_color=TEXT_SECONDARY)


class SlotTile(ctk.CTkFrame):
    def __init__(self, master, slot_id, occupied=False, plate=""):
        bg = SLOT_OCC if occupied else SLOT_FREE
        bd = SLOT_OCC_BD if occupied else SLOT_FREE_BD
        super().__init__(master, width=92, height=72, corner_radius=12,
                         fg_color=bg, border_width=1.5, border_color=bd)
        self.grid_propagate(False)
        ctk.CTkLabel(self, text=slot_id, font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).place(relx=.5, rely=.32, anchor="center")
        status_text  = plate if (occupied and plate) else ("Occupied" if occupied else "Free")
        status_color = "#ffb3b3" if occupied else "#9affd6"
        ctk.CTkLabel(self, text=status_text, font=("Segoe UI", 10),
                     text_color=status_color).place(relx=.5, rely=.72, anchor="center")



def _glass_popup(title_text, width=700, height=520):
    win = ctk.CTkToplevel()
    win.title(title_text)
    win.geometry(f"{width}x{height}")
    win.configure(fg_color=BG_COLOR)
    win.grab_set()
    win.attributes("-topmost", True)
    hdr = ctk.CTkFrame(win, fg_color=PANEL_COLOR, corner_radius=0,
                        height=54, border_width=0)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    ctk.CTkLabel(hdr, text=title_text, font=("Segoe UI", 16, "bold"),
                 text_color=NEON_BLUE).pack(side="left", padx=22, pady=14)
    ctk.CTkButton(hdr, text="✕", width=36, height=36, corner_radius=8,
                  fg_color="transparent", hover_color=SLOT_OCC,
                  text_color=TEXT_SECONDARY, font=("Segoe UI", 14),
                  command=win.destroy).pack(side="right", padx=12)
    body = ctk.CTkFrame(win, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=22, pady=16)
    return win, body


def _neon_btn(master, text, color, command, width=140, height=38):
    return ctk.CTkButton(
        master, text=text, width=width, height=height,
        corner_radius=10, fg_color="#0c1830", hover_color="#16263f",
        border_width=1.5, border_color=color, text_color=color,
        font=("Segoe UI", 12, "bold"), command=command)



class ParkingMapPopup:
    def __init__(self, parking_lot: ParkingLot):
        self.lot = parking_lot
        win, body = _glass_popup("🅿️ Live Parking Map", width=720, height=560)
        self.win  = win

        legend = ctk.CTkFrame(body, fg_color="transparent")
        legend.pack(fill="x", pady=(0, 12))
        for color, lbl in [(NEON_GREEN, "Available"), (SLOT_OCC_BD, "Occupied")]:
            f = ctk.CTkFrame(legend, fg_color="transparent"); f.pack(side="left", padx=10)
            ctk.CTkLabel(f, text="●", text_color=color,
                         font=("Segoe UI", 14)).pack(side="left")
            ctk.CTkLabel(f, text=lbl, text_color=TEXT_SECONDARY,
                         font=("Segoe UI", 12)).pack(side="left", padx=4)

        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack()

        COLS = 5
        for idx, slot in enumerate(self.lot.slots):
            plate = slot.vehicle.plate_num if (slot.is_occupied and slot.vehicle) else ""
            SlotTile(grid, slot.slot_id, slot.is_occupied, plate).grid(
                row=idx // COLS, column=idx % COLS, padx=6, pady=6)

        _neon_btn(body, "↻  Refresh", NEON_BLUE,
                  command=lambda: [win.destroy(), ParkingMapPopup(self.lot)],
                  width=110, height=36).pack(pady=(10, 0))


class VehicleListPopup:
    def __init__(self, admin: Admin):
        self.admin = admin
        win, body  = _glass_popup("🚗 Parked Vehicles", width=740, height=520)
        self.win   = win
        self._build(body)

    def _build(self, body):
        vehicles = self.admin.view_all_vehicles()
        if not vehicles:
            ctk.CTkLabel(body, text="No vehicles currently parked.",
                         font=("Segoe UI", 14), text_color=TEXT_SECONDARY).pack(pady=60)
            return

        hdr = ctk.CTkFrame(body, fg_color="#0e1f38", corner_radius=10, height=38)
        hdr.pack(fill="x", pady=(0, 8)); hdr.pack_propagate(False)
        for col, w in [("Ticket ID", 110), ("Plate", 110), ("Slot", 80),
                        ("Type", 100), ("Entry Time", 180)]:
            ctk.CTkLabel(hdr, text=col, font=("Segoe UI", 12, "bold"),
                         text_color=NEON_BLUE, width=w).pack(side="left", padx=10, pady=8)

        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for tid, ticket in vehicles.items():
            row = ctk.CTkFrame(scroll, fg_color="#121829", corner_radius=10,
                               border_width=1, border_color=PANEL_BORDER)
            row.pack(fill="x", pady=3)
            entry_str = ticket.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            for val, w in [(tid, 110), (ticket.vehicle.plate_num, 110),
                            (ticket.slot_id, 80), (ticket.vehicle.vehicle_type, 100),
                            (entry_str, 180)]:
                ctk.CTkLabel(row, text=val, font=("Segoe UI", 12),
                             text_color=TEXT_PRIMARY, width=w).pack(side="left", padx=10, pady=9)


class WaitingQueuePopup:
    def __init__(self, admin: Admin):
        self.admin = admin
        win, body  = _glass_popup("⏳ Waiting Queue", width=640, height=460)
        self.win   = win
        self._build(body)

    def _build(self, body):
        queue = self.admin.view_waiting_queue()
        if not queue:
            ctk.CTkLabel(body, text="Waiting queue is empty.",
                         font=("Segoe UI", 14), text_color=TEXT_SECONDARY).pack(pady=60)
            return

        hdr = ctk.CTkFrame(body, fg_color="#0e1f38", corner_radius=10, height=38)
        hdr.pack(fill="x", pady=(0, 8)); hdr.pack_propagate(False)
        for col, w in [("#", 50), ("Customer", 160), ("Plate", 130), ("Type", 120)]:
            ctk.CTkLabel(hdr, text=col, font=("Segoe UI", 12, "bold"),
                         text_color=NEON_BLUE, width=w).pack(side="left", padx=10, pady=8)

        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for pos, (cust, veh) in enumerate(queue, 1):
            cname = cust.name if cust else "Unknown"
            row = ctk.CTkFrame(scroll, fg_color="#121829", corner_radius=10,
                               border_width=1, border_color=PANEL_BORDER)
            row.pack(fill="x", pady=3)
            for val, w in [(str(pos), 50), (cname, 160),
                            (veh.plate_num, 130), (veh.vehicle_type, 120)]:
                ctk.CTkLabel(row, text=val, font=("Segoe UI", 12),
                             text_color=TEXT_PRIMARY, width=w).pack(side="left", padx=10, pady=9)


class SubscribersPopup:
    def __init__(self, admin: Admin):
        self.admin = admin
        win, body  = _glass_popup("👥  Subscriber Management", width=820, height=580)
        self.win   = win
        self.body  = body
        self._build(body)


    def _do_add(self, name_var, hours_var):
        name  = name_var.get().strip()
        hours = hours_var.get().strip()
        if not name:
            self._set_status("⚠ Name is required.", WARN_COLOR); return
        try:
            hours_f = float(hours)
            if hours_f <= 0: raise ValueError
        except ValueError:
            self._set_status("⚠ Enter a valid positive number for hours.", WARN_COLOR); return
        sub = SubscriberCustomer(name, self.admin.parking_lot, hours_f)
        self.admin.add_subscriber(sub)
        self._set_status(f"✅ Subscriber {sub.user_id} ({name}) added.", NEON_GREEN)
        name_var.set(""); hours_var.set("")
        self._refresh_list()

    def _do_remove(self, id_var):
        sid = id_var.get().strip()
        if not sid:
            self._set_status("⚠ Enter a subscriber ID.", WARN_COLOR); return
        if sid not in self.admin.view_subscribers():
            self._set_status(f"⚠ ID '{sid}' not found.", DANGER_COLOR); return
        self.admin.remove_subscriber(sid)
        self._set_status(f"✅ Subscriber {sid} removed.", NEON_GREEN)
        id_var.set("")
        self._refresh_list()

    def _do_search(self, id_var):
        sid = id_var.get().strip()
        if not sid:
            self._set_status("⚠ Enter a subscriber ID to search.", WARN_COLOR)
            self._clear_result_card(); return
        result = self.admin.search_subscriber(sid)
        if result:
            self._set_status("✅ Subscriber found.", NEON_GREEN)
            self._show_result_card(result)
        else:
            self._set_status(f"⚠ No subscriber with ID '{sid}'.", DANGER_COLOR)
            self._clear_result_card()

    def _set_status(self, msg, color):
        self._status_lbl.configure(text=msg, text_color=color)

    def _clear_result_card(self):
        for w in self._result_frame.winfo_children(): w.destroy()

    def _show_result_card(self, sub):
        self._clear_result_card()
        card = ctk.CTkFrame(self._result_frame, fg_color="#0e2a1f",
                            corner_radius=12, border_width=1.5,
                            border_color=NEON_GREEN)
        card.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(card, text="🔍  Search Result",
                     font=("Segoe UI", 12, "bold"),
                     text_color=NEON_GREEN).pack(anchor="w", padx=16, pady=(12, 6))
        for label, value, color in [
            ("Subscriber ID", sub.user_id, NEON_BLUE),
            ("Name",          sub.name,    TEXT_PRIMARY),
            ("Hours Left",    f"{sub.subscription_hours} hrs", NEON_GREEN),
        ]:
            row = ctk.CTkFrame(card, fg_color="transparent"); row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row, text=f"{label}:", font=("Segoe UI", 11),
                         text_color=TEXT_SECONDARY, width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Segoe UI", 12, "bold"),
                         text_color=color).pack(side="left", padx=6)
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

    def _refresh_list(self):
        for w in self._list_frame.winfo_children(): w.destroy()
        subs = self.admin.view_subscribers()
        if not subs:
            ctk.CTkLabel(self._list_frame, text="No subscribers registered.",
                         font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(pady=20)
            return
        for sid, sub in subs.items():
            row = ctk.CTkFrame(self._list_frame, fg_color="#0e1f38", corner_radius=10)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=sid, font=("Segoe UI", 12, "bold"),
                         text_color=NEON_BLUE, width=100).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=sub.name, font=("Segoe UI", 12),
                         text_color=TEXT_PRIMARY, width=150).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=f"{sub.subscription_hours} hrs",
                         font=("Segoe UI", 12), text_color=NEON_GREEN,
                         width=100).pack(side="left", padx=6)

    def _build(self, body):
        # Add subscriber
        add_box = GlassFrame(body, accent=NEON_GREEN)
        add_box.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(add_box, text="➕  Add Subscriber",
                     font=("Segoe UI", 13, "bold"),
                     text_color=NEON_GREEN).pack(anchor="w", padx=16, pady=(12, 6))
        row1 = ctk.CTkFrame(add_box, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(0, 12))
        name_var  = ctk.StringVar()
        hours_var = ctk.StringVar()
        ctk.CTkLabel(row1, text="Name:", text_color=TEXT_SECONDARY,
                     font=("Segoe UI", 12), width=60).pack(side="left")
        ctk.CTkEntry(row1, textvariable=name_var, placeholder_text="Full name",
                     width=180, height=34, corner_radius=8,
                     fg_color="#0c1830", border_color=PANEL_BORDER,
                     text_color=TEXT_PRIMARY).pack(side="left", padx=(4, 16))
        ctk.CTkLabel(row1, text="Hours:", text_color=TEXT_SECONDARY,
                     font=("Segoe UI", 12), width=60).pack(side="left")
        ctk.CTkEntry(row1, textvariable=hours_var, placeholder_text="e.g. 10",
                     width=100, height=34, corner_radius=8,
                     fg_color="#0c1830", border_color=PANEL_BORDER,
                     text_color=TEXT_PRIMARY).pack(side="left", padx=(4, 16))
        _neon_btn(row1, "Add", NEON_GREEN,
                  command=lambda: self._do_add(name_var, hours_var),
                  width=80, height=34).pack(side="left")

        # Remove / search
        ops_box = GlassFrame(body, accent=NEON_BLUE)
        ops_box.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ops_box, text="🔧  Remove / Search",
                     font=("Segoe UI", 13, "bold"),
                     text_color=NEON_BLUE).pack(anchor="w", padx=16, pady=(12, 6))
        row2 = ctk.CTkFrame(ops_box, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 12))
        id_var = ctk.StringVar()
        ctk.CTkLabel(row2, text="Sub ID:", text_color=TEXT_SECONDARY,
                     font=("Segoe UI", 12), width=60).pack(side="left")
        ctk.CTkEntry(row2, textvariable=id_var, placeholder_text="SUB1001",
                     width=160, height=34, corner_radius=8,
                     fg_color="#0c1830", border_color=PANEL_BORDER,
                     text_color=TEXT_PRIMARY).pack(side="left", padx=(4, 16))
        _neon_btn(row2, "Remove", DANGER_COLOR,
                  command=lambda: self._do_remove(id_var),
                  width=90, height=34).pack(side="left", padx=(0, 8))
        _neon_btn(row2, "Search", NEON_BLUE,
                  command=lambda: self._do_search(id_var),
                  width=90, height=34).pack(side="left")

        self._status_lbl = ctk.CTkLabel(body, text="",
                                        font=("Segoe UI", 12),
                                        text_color=NEON_GREEN)
        self._status_lbl.pack(anchor="w", pady=(2, 0))

        self._result_frame = ctk.CTkFrame(body, fg_color="transparent")
        self._result_frame.pack(fill="x", pady=(2, 4))

        ctk.CTkLabel(body, text="Registered Subscribers",
                     font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(4, 6))

        lhdr = ctk.CTkFrame(body, fg_color="#0e1f38", corner_radius=10, height=34)
        lhdr.pack(fill="x"); lhdr.pack_propagate(False)
        for col, w in [("ID", 100), ("Name", 150), ("Sub Hours", 100)]:
            ctk.CTkLabel(lhdr, text=col, font=("Segoe UI", 11, "bold"),
                         text_color=NEON_BLUE, width=w).pack(side="left", padx=10, pady=6)

        scroll = ctk.CTkScrollableFrame(body, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=(4, 0))
        self._list_frame = scroll
        self._refresh_list()



class AdminDashboard(ctk.CTk):

    def __init__(self, admin: Admin):
        super().__init__()
        self.admin = admin
        self.lot   = admin.parking_lot

        self.title("Smart Parking System — Admin Dashboard")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG_COLOR)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=.5, rely=.5, anchor="center",
                             relwidth=.96, relheight=.94)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

        self._running = True
        self.attributes("-alpha", 0.0)
        self._alpha = 0.0
        self.after(50, self._fade_in)
        self._pulse_up = True
        self.after(300, self._pulse_live)
        self.after(500, self._refresh_stats)


    def _build_sidebar(self):
        self.sidebar = GlassFrame(self.container, width=230, corner_radius=20)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=(0, 18))
        self.sidebar.grid_propagate(False)

        ring = ctk.CTkFrame(self.sidebar, width=56, height=56, corner_radius=28,
                            fg_color="#0e1f38", border_width=2, border_color=NEON_BLUE)
        ring.pack(pady=(28, 8)); ring.pack_propagate(False)
        ctk.CTkLabel(ring, text="P", font=("Segoe UI", 22, "bold"),
                     text_color=NEON_BLUE).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(self.sidebar, text="Smart Parking",
                     font=("Segoe UI", 14, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(0, 2))
        ctk.CTkLabel(self.sidebar, text="ADMIN PANEL",
                     font=("Segoe UI", 10),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 24))

        nav_items = [
            ("📊", "Dashboard",     self.show_dashboard),
            ("🅿️", "Parking Map",   self.open_parking_map),
            ("🚗", "Vehicles",      self.open_vehicles),
            ("⏳", "Waiting Queue", self.open_waiting_queue),
            ("👥", "Subscribers",   self.open_subscribers),
        ]
        self._nav_btns = []
        for i, (icon, text, cmd) in enumerate(nav_items):
            b = NavButton(self.sidebar, icon, text, command=cmd, active=(i == 0))
            b.pack(fill="x", padx=16, pady=4)
            self._nav_btns.append(b)

        self.logout_btn = ctk.CTkButton(
            self.sidebar, text="⎋  Logout", height=40, corner_radius=12,
            fg_color="transparent", hover_color="#3a1f25",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self.logout)
        self.logout_btn.pack(side="bottom", fill="x", padx=16, pady=(0, 22))
        self.logout_btn.bind("<Enter>", lambda e: self.logout_btn.configure(
            text_color=DANGER_COLOR, border_color=DANGER_COLOR))
        self.logout_btn.bind("<Leave>", lambda e: self.logout_btn.configure(
            text_color=TEXT_SECONDARY, border_color=PANEL_BORDER))

        badge = ctk.CTkFrame(self.sidebar, fg_color="#0e1f38", corner_radius=14,
                             border_width=1.5, border_color=NEON_BLUE)
        badge.pack(side="bottom", fill="x", padx=16, pady=(0, 4))
        ctk.CTkLabel(badge, text=f"🛡️  {self.admin.name}",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(10, 0), padx=12, anchor="w")
        ctk.CTkLabel(badge, text=f"{self.admin.user_id} • Online",
                     font=("Segoe UI", 10),
                     text_color=NEON_GREEN).pack(pady=(0, 10), padx=12, anchor="w")

        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True, fill="both")


    def _build_main(self):
        self.main = ctk.CTkFrame(self.container, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nswe")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ctk.CTkLabel(header, text="Dashboard Overview",
                     font=("Segoe UI", 24, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        self.live_pill = ctk.CTkLabel(
            header, text="●  Live", font=("Segoe UI", 11, "bold"),
            text_color=NEON_GREEN, fg_color="#0e1c33",
            corner_radius=20, padx=14, pady=6)
        self.live_pill.pack(side="right")

        actions_row = ctk.CTkFrame(self.main, fg_color="transparent")
        actions_row.grid(row=0, column=0, sticky="e")
        for label, color, cmd in [
            ("🅿️ Map",         NEON_BLUE,  self.open_parking_map),
            ("🚗 Vehicles",    NEON_GREEN, self.open_vehicles),
            ("⏳ Queue",       WARN_COLOR, self.open_waiting_queue),
            ("👥 Subscribers", NEON_BLUE,  self.open_subscribers),
        ]:
            _neon_btn(actions_row, label, color, cmd,
                      width=130, height=34).pack(side="left", padx=4)

        stats_row = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        for i in range(4):
            stats_row.grid_columnconfigure(i, weight=1, uniform="stat")

        status = self.lot.display_status()
        self.total_card     = StatCard(stats_row, "🅿️", status["total_slots"], "Total Slots",   NEON_BLUE)
        self.occupied_card  = StatCard(stats_row, "🚗", status["occupied"],     "Occupied",      DANGER_COLOR)
        self.available_card = StatCard(stats_row, "✅", status["available"],    "Available",     NEON_GREEN)
        self.queue_card     = StatCard(stats_row, "⏳", status["waiting"],      "Waiting Queue", WARN_COLOR)
        self.total_card.grid    (row=0, column=0, sticky="ew", padx=(0, 12))
        self.occupied_card.grid (row=0, column=1, sticky="ew", padx=12)
        self.available_card.grid(row=0, column=2, sticky="ew", padx=12)
        self.queue_card.grid    (row=0, column=3, sticky="ew", padx=(12, 0))

        lower = ctk.CTkFrame(self.main, fg_color="transparent")
        lower.grid(row=2, column=0, sticky="nswe")
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=2)
        lower.grid_rowconfigure(0, weight=1)

        # Inline parking map
        map_panel = GlassFrame(lower, accent=NEON_BLUE)
        map_panel.grid(row=0, column=0, sticky="nswe", padx=(0, 18))

        mhdr = ctk.CTkFrame(map_panel, fg_color="transparent")
        mhdr.pack(fill="x", padx=22, pady=(20, 4))
        ctk.CTkLabel(mhdr, text="Live Parking Map",
                     font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        legend = ctk.CTkFrame(mhdr, fg_color="transparent"); legend.pack(side="right")
        for color, lbl in [(NEON_GREEN, "Available"), (DANGER_COLOR, "Occupied")]:
            f = ctk.CTkFrame(legend, fg_color="transparent"); f.pack(side="left", padx=8)
            ctk.CTkLabel(f, text="●", text_color=color,
                         font=("Segoe UI", 12)).pack(side="left")
            ctk.CTkLabel(f, text=lbl, text_color=TEXT_SECONDARY,
                         font=("Segoe UI", 11)).pack(side="left", padx=(4, 0))

        self.grid_frame = ctk.CTkFrame(map_panel, fg_color="transparent")
        self.grid_frame.pack(padx=22, pady=(14, 10), fill="both", expand=True)
        _neon_btn(map_panel, "Open Full Map ↗", NEON_BLUE,
                  command=self.open_parking_map, width=150, height=32).pack(pady=(0, 14))
        self._build_parking_grid()

        # Right column
        side = ctk.CTkFrame(lower, fg_color="transparent")
        side.grid(row=0, column=1, sticky="nswe")
        side.grid_rowconfigure(0, weight=1)
        side.grid_rowconfigure(1, weight=1)
        side.grid_columnconfigure(0, weight=1)

        qpanel = GlassFrame(side, accent=NEON_GREEN)
        qpanel.grid(row=0, column=0, sticky="nswe", pady=(0, 18))
        ctk.CTkLabel(qpanel, text="⏳ Waiting Queue",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(18, 10))
        self.queue_preview = ctk.CTkScrollableFrame(qpanel, fg_color="transparent", height=120)
        self.queue_preview.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._refresh_queue_preview()

        apanel = GlassFrame(side, accent=NEON_BLUE)
        apanel.grid(row=1, column=0, sticky="nswe")
        ctk.CTkLabel(apanel, text="📋 Recent Activity",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(18, 10))
        self.activity_frame = ctk.CTkScrollableFrame(apanel, fg_color="transparent", height=120)
        self.activity_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self._activity_log = []
        self._log_activity("✅", f"Admin {self.admin.name} logged in", NEON_GREEN)


    def _build_parking_grid(self):
        for w in self.grid_frame.winfo_children(): w.destroy()
        COLS = 5
        for idx, slot in enumerate(self.lot.slots):
            plate = slot.vehicle.plate_num if (slot.is_occupied and slot.vehicle) else ""
            SlotTile(self.grid_frame, slot.slot_id, slot.is_occupied, plate).grid(
                row=idx // COLS, column=idx % COLS, padx=5, pady=5)

    def _refresh_queue_preview(self):
        for w in self.queue_preview.winfo_children(): w.destroy()
        queue = self.admin.view_waiting_queue()
        if not queue:
            ctk.CTkLabel(self.queue_preview, text="Queue is empty.",
                         font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(pady=10)
            return
        for pos, (cust, veh) in enumerate(queue, 1):
            cname = cust.name if cust else "Unknown"
            row = ctk.CTkFrame(self.queue_preview, fg_color="#0e1f38", corner_radius=10)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"#{pos}  {veh.plate_num}  •  {cname}",
                         font=("Segoe UI", 12), text_color=TEXT_PRIMARY).pack(
                             side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text="●", text_color=WARN_COLOR,
                         font=("Segoe UI", 12)).pack(side="right", padx=12)

    def _log_activity(self, icon, text, color=TEXT_SECONDARY):
        self._activity_log.insert(0, (icon, text, color))
        if len(self._activity_log) > 20: self._activity_log.pop()
        for w in self.activity_frame.winfo_children(): w.destroy()
        for ico, txt, clr in self._activity_log[:8]:
            row = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=ico, font=("Segoe UI Emoji", 13),
                         text_color=clr).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=txt, font=("Segoe UI", 11.5),
                         text_color=TEXT_SECONDARY, wraplength=240,
                         justify="left").pack(side="left")

    def _refresh_stats(self):
        if not self._running: return
        st = self.lot.display_status()
        self.total_card.set_value(st["total_slots"])
        self.occupied_card.set_value(st["occupied"])
        self.available_card.set_value(st["available"])
        self.queue_card.set_value(st["waiting"])
        self._build_parking_grid()
        self._refresh_queue_preview()
        self.after(3000, self._refresh_stats)

    def _set_active_nav(self, idx):
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == idx)


    def show_dashboard(self):
        self._set_active_nav(0)

    def open_parking_map(self):
        self._set_active_nav(1)
        ParkingMapPopup(self.lot)
        self._log_activity("🅿️", "Opened parking map", NEON_BLUE)

    def open_vehicles(self):
        self._set_active_nav(2)
        VehicleListPopup(self.admin)
        self._log_activity("🚗", "Viewed vehicle list", NEON_BLUE)

    def open_waiting_queue(self):
        self._set_active_nav(3)
        WaitingQueuePopup(self.admin)
        self._log_activity("⏳", "Viewed waiting queue", WARN_COLOR)

    def open_subscribers(self):
        self._set_active_nav(4)
        SubscribersPopup(self.admin)
        self._log_activity("👥", "Opened subscriber management", NEON_GREEN)

    def logout(self):
        self._running = False
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                try:
                    widget.grab_release(); widget.destroy()
                except Exception:
                    pass
        from gui.start_screen import StartScreen
        lot     = self.lot
        sub_mgr = self.admin.subscriber_manager
        self.destroy()
        StartScreen(parking_lot=lot, subscriber_manager=sub_mgr).mainloop()

    # ── Animations ────────────────────────────────────────────────────────────

    def _fade_in(self):
        if not self._running: return
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._alpha < 1.0: self.after(16, self._fade_in)

    def _pulse_live(self):
        if not self._running: return
        self.live_pill.configure(
            text_color=NEON_BLUE if self._pulse_up else NEON_GREEN)
        self._pulse_up = not self._pulse_up
        self.after(800, self._pulse_live)


# ── Demo entry point ──────────────────────────────────────────────────────────

def _build_demo_backend():
    """Builds a fully populated demo backend (used by adminLogin.py)."""
    lot = ParkingLot(rate_per_hour=10)
    for row in ["A", "B", "C", "D"]:
        for col in range(1, 6):
            lot.add_slot(ParkingSlot(f"{row}{col}"))

    sub_mgr = SubscriberManager()

    demo_plates = [
        ("ABC-123", "Sedan",  "Red"),   ("XYZ-789", "SUV",   "Black"),
        ("LMN-456", "Truck",  "White"), ("QWE-111", "Sedan", "Blue"),
        ("TYU-222", "Coupe",  "Silver"),("ASD-333", "SUV",   "Grey"),
        ("ZXC-444", "Sedan",  "Green"), ("POI-555", "Truck", "Yellow"),
        ("VBN-666", "Coupe",  "White"), ("MKL-777", "Sedan", "Red"),
        ("JHG-888", "SUV",    "Black"), ("FDS-999", "Sedan", "Blue"),
    ]
    for plate, vtype, vcolor in demo_plates:
        lot.assign_vehicle(vehicle(plate, vtype, vcolor))

    for name, hrs in [("Aisha Kamal", 20), ("Omar Hassan", 15), ("Nour Samir", 5)]:
        sub_mgr.add_subscriber(SubscriberCustomer(name, lot, hrs))

    for name, plate in [("Mona Ali", "WTQ-001"), ("Khaled Nour", "WTQ-002")]:
        sub = SubscriberCustomer(name, lot, 10)
        lot.waiting_queue.append((sub, vehicle(plate, "Sedan", "Unknown")))

    admin = Admin("ADM001", "Asmaa", sub_mgr, lot)
    return admin


if __name__ == "__main__":
    admin = _build_demo_backend()
    AdminDashboard(admin).mainloop()