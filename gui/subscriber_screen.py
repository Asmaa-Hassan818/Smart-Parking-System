import customtkinter as ctk
import os
import math
import random

from models.vehicle import vehicle

ctk.set_appearance_mode("dark")

BG_COLOR       = "#0b0f1a"
PANEL_COLOR    = "#121829"
PANEL_BORDER   = "#1f2a44"
NEON_BLUE      = "#3ad6ff"
NEON_CYAN      = "#5ef7ff"
NEON_GREEN     = "#39ffb0"
NEON_RED       = "#ff6b6b"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"
INPUT_BG       = "#0c1426"


class ParticleOverlay(ctk.CTkCanvas):

    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.particles = []
        self.bind("<Configure>", self._on_resize)
        self._ready = False
        self.after_ids = []
        self.running = True

    def _on_resize(self, event):
        if not self._ready:
            self._ready = True
            self._build(event.width, event.height)
            self._animate()

    def _build(self, w, h):
        for _ in range(45):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            r = random.uniform(1.5, 3.5)
            speed = random.uniform(0.3, 1.0)
            color = random.choice([NEON_GREEN, NEON_BLUE])
            item = self.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline="")
            self.particles.append({
                "id": item,
                "speed": speed,
                "phase": random.uniform(0, math.tau)
            })

    def _animate(self):
        if not self.running:
            return
        h = self.winfo_height()
        for p in self.particles:
            p["phase"] += 0.03
            dx = math.sin(p["phase"]) * 0.4
            self.move(p["id"], dx, -p["speed"])
            coords = self.coords(p["id"])
            if coords and coords[1] < -5:
                self.move(p["id"], 0, h + 10)
        aid = self.after(40, self._animate)
        self.after_ids.append(aid)

    def stop(self):
        self.running = False
        for aid in self.after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass


class GlowButton(ctk.CTkButton):

    def __init__(self, master, glow_color=NEON_GREEN, **kwargs):
        super().__init__(master, **kwargs)
        self.glow_color = glow_color
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e=None):
        self.configure(border_width=2, border_color=self.glow_color)

    def _on_leave(self, _e=None):
        self.configure(border_width=0)


class GlassCard(ctk.CTkFrame):

    def __init__(self, master, border_color=PANEL_BORDER, **kwargs):
        super().__init__(
            master, corner_radius=20, fg_color=PANEL_COLOR,
            border_width=2, border_color=border_color, **kwargs
        )


class SubscriberDashboard(ctk.CTk):

    VEHICLE_TYPES = ["Car", "SUV", "Motorcycle", "Van", "Truck"]

    def __init__(self, subscriber=None, parking_lot=None,
                 subscriber_manager=None, on_back=None, on_logout=None):
        super().__init__()

        self._bg_pil = None
        self.subscriber = subscriber
        self.parking_lot = parking_lot
        self.subscriber_manager = subscriber_manager  # kept for future use
        self.on_back = on_back
        self.on_logout = on_logout
        self._bg_ctk = None
        self._alpha = 0.0
        self.after_ids = []
        self.running = True

        self.title("Smart Parking System - Subscriber Dashboard")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG_COLOR)

        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Header ────────────────────────────────────────────────────────────
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.place(relx=0.5, rely=0.045, anchor="n")

        self.icon_ring = ctk.CTkFrame(
            self.header, width=64, height=64, corner_radius=32,
            fg_color="#0e2a22", border_width=2, border_color=NEON_GREEN
        )
        self.icon_ring.pack(side="left", padx=(0, 14))
        self.icon_ring.pack_propagate(False)
        ctk.CTkLabel(self.icon_ring, text="💳",
                     font=("Segoe UI Emoji", 26)
                     ).place(relx=0.5, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Subscriber Dashboard",
                     font=("Segoe UI", 24, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_box,
                     text=f"Welcome back, {self.subscriber.name}",
                     font=("Segoe UI", 12),
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        # ── Top-right buttons ─────────────────────────────────────────────────
        self.top_btns = ctk.CTkFrame(self, fg_color="transparent")
        self.top_btns.place(relx=0.985, rely=0.045, anchor="ne")

        self.back_btn = GlowButton(
            self.top_btns, glow_color=NEON_BLUE,
            text="←  Back", width=100, height=36, corner_radius=10,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12),
            command=self.handle_back          # ← wired
        )
        self.back_btn.pack(side="left", padx=(0, 8))

        self.logout_btn = GlowButton(
            self.top_btns, glow_color=NEON_RED,
            text="Logout", width=100, height=36, corner_radius=10,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12),
            command=self.handle_logout        # ← wired
        )
        self.logout_btn.pack(side="left")

        # ── Content cards ─────────────────────────────────────────────────────
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.58, anchor="center")

        self.info_card = GlassCard(self.content, border_color=NEON_GREEN,
                                   width=300, height=460)
        self.info_card.grid(row=0, column=0, padx=14, sticky="n")
        self.info_card.grid_propagate(False)
        self._build_info_card()

        self.form_card = GlassCard(self.content, border_color=NEON_BLUE,
                                   width=360, height=460)
        self.form_card.grid(row=0, column=1, padx=14, sticky="n")
        self.form_card.grid_propagate(False)
        self._build_form()

        self.ticket_card = GlassCard(self.content, border_color=PANEL_BORDER,
                                     width=360, height=460)
        self.ticket_card.grid(row=0, column=2, padx=14, sticky="n")
        self.ticket_card.grid_propagate(False)
        self._build_ticket_panel()

        ctk.CTkLabel(
            self, text="SMART PARKING SYSTEM  ©  2026",
            font=("Segoe UI", 11), text_color=TEXT_SECONDARY
        ).place(relx=0.5, rely=0.975, anchor="center")

        self.attributes("-alpha", 0.0)
        self.after(50, self._fade_in)
        self._refresh_info_card()

    # ── Info card ─────────────────────────────────────────────────────────────

    def _build_info_card(self):
        ctk.CTkLabel(self.info_card, text="Subscriber Information",
                     font=("Segoe UI", 17, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(26, 4), padx=22, anchor="w")
        ctk.CTkLabel(self.info_card, text="Your membership details",
                     font=("Segoe UI", 11.5),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 18), padx=22, anchor="w")

        self.badge = ctk.CTkLabel(
            self.info_card, text="★ ACTIVE MEMBER",
            font=("Segoe UI", 10, "bold"), text_color="#06241c",
            fg_color=NEON_GREEN, corner_radius=12, padx=10, pady=4
        )
        self.badge.pack(padx=22, anchor="w", pady=(0, 16))

        self.info_frame = ctk.CTkFrame(self.info_card, fg_color="#0c1426",
                                       corner_radius=14)
        self.info_frame.pack(padx=22, pady=(0, 14), fill="x")

        self.row_customer_id = self._info_row(self.info_frame, "Customer ID", "—")
        self.row_name        = self._info_row(self.info_frame, "Name", "—")
        self.row_hours       = self._info_row(self.info_frame, "Remaining Hours", "—")
        self.row_status      = self._info_row(self.info_frame, "Membership Status", "—")

        self.balance_btn = GlowButton(
            self.info_card, glow_color=NEON_GREEN,
            text="🔄  Check Remaining Hours", width=256, height=42,
            corner_radius=12, fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=NEON_GREEN,
            text_color=NEON_GREEN, font=("Segoe UI", 12.5, "bold"),
            command=self.handle_check_balance
        )
        self.balance_btn.pack(padx=22, pady=(8, 8))

        self.history_btn = GlowButton(
            self.info_card, glow_color=NEON_BLUE,
            text="🕑  View Parking History", width=256, height=40,
            corner_radius=12, fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12),
            command=self.handle_view_history
        )
        self.history_btn.pack(padx=22)

    def _info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row, text=label, font=("Segoe UI", 12),
                     text_color=TEXT_SECONDARY).pack(side="left")
        val_label = ctk.CTkLabel(row, text=value,
                                 font=("Segoe UI", 13, "bold"),
                                 text_color=TEXT_PRIMARY)
        val_label.pack(side="right")
        return val_label

    def _refresh_info_card(self):
        self.row_customer_id.configure(text=self.subscriber.user_id)
        self.row_name.configure(text=self.subscriber.name)
        self.row_hours.configure(
            text=f"{round(self.subscriber.subscription_hours, 2)} hrs")

        hours = self.subscriber.subscription_hours
        if hours <= 0:
            self.row_status.configure(text="Expired", text_color=NEON_RED)
            self.badge.configure(text="● NO HOURS LEFT",
                                 fg_color=NEON_RED, text_color="#2a0a0a")
        elif hours < 5:
            self.row_status.configure(text="Low Balance", text_color="#ffd166")
            self.badge.configure(text="● LOW BALANCE",
                                 fg_color="#ffd166", text_color="#332300")
        else:
            self.row_status.configure(text="Active", text_color=NEON_GREEN)
            self.badge.configure(text="★ ACTIVE MEMBER",
                                 fg_color=NEON_GREEN, text_color="#06241c")

    # ── Form card ─────────────────────────────────────────────────────────────

    def _build_form(self):
        ctk.CTkLabel(self.form_card, text="Parking Actions",
                     font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(26, 4), padx=24, anchor="w")
        ctk.CTkLabel(self.form_card, text="Park or exit your vehicle",
                     font=("Segoe UI", 11.5),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 18), padx=24, anchor="w")

        ctk.CTkLabel(self.form_card, text="Plate Number",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(8, 4), padx=24, anchor="w")
        self.plate_entry = ctk.CTkEntry(
            self.form_card, width=312, height=42, corner_radius=12,
            placeholder_text="e.g. ABC 1234",
            fg_color=INPUT_BG, border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        self.plate_entry.pack(padx=24)
        self.plate_entry.bind("<FocusIn>",  lambda e: self.plate_entry.configure(
            border_color=NEON_BLUE, border_width=2))
        self.plate_entry.bind("<FocusOut>", lambda e: self.plate_entry.configure(
            border_color=PANEL_BORDER, border_width=1.5))

        ctk.CTkLabel(self.form_card, text="Vehicle Type",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(8, 4), padx=24, anchor="w")
        self.vehicle_type_combo = ctk.CTkComboBox(
            self.form_card, values=self.VEHICLE_TYPES, width=312, height=42,
            corner_radius=12, fg_color=INPUT_BG, border_color=PANEL_BORDER,
            button_color="#1b2740", button_hover_color=NEON_BLUE,
            dropdown_fg_color=PANEL_COLOR, dropdown_hover_color="#1b2740",
            text_color=TEXT_PRIMARY, font=("Segoe UI", 13)
        )
        self.vehicle_type_combo.set(self.VEHICLE_TYPES[0])
        self.vehicle_type_combo.pack(padx=24, pady=(0, 12))

        self.park_btn = GlowButton(
            self.form_card, glow_color=NEON_BLUE,
            text="🅿  Park Vehicle", width=312, height=46, corner_radius=12,
            fg_color=NEON_BLUE, hover_color=NEON_CYAN,
            text_color="#06141f", font=("Segoe UI", 14, "bold"),
            command=self.handle_park
        )
        self.park_btn.pack(padx=24, pady=(6, 16))

        ctk.CTkFrame(self.form_card, height=1,
                     fg_color=PANEL_BORDER).pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkLabel(self.form_card, text="Ticket ID",
                     font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 4), padx=24, anchor="w")
        self.ticket_id_entry = ctk.CTkEntry(
            self.form_card, width=312, height=42, corner_radius=12,
            placeholder_text="e.g. T1000",
            fg_color=INPUT_BG, border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        self.ticket_id_entry.pack(padx=24)
        self.ticket_id_entry.bind("<FocusIn>",  lambda e: self.ticket_id_entry.configure(
            border_color=NEON_GREEN, border_width=2))
        self.ticket_id_entry.bind("<FocusOut>", lambda e: self.ticket_id_entry.configure(
            border_color=PANEL_BORDER, border_width=1.5))

        self.exit_btn = GlowButton(
            self.form_card, glow_color=NEON_GREEN,
            text="🚪  Exit Vehicle", width=312, height=46, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=NEON_GREEN,
            text_color=NEON_GREEN, font=("Segoe UI", 13, "bold"),
            command=self.handle_exit
        )
        self.exit_btn.pack(padx=24, pady=(12, 0))

    # ── Ticket / activity panel ───────────────────────────────────────────────

    def _build_ticket_panel(self):
        self.ticket_title = ctk.CTkLabel(
            self.ticket_card, text="Activity Status",
            font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY)
        self.ticket_title.pack(pady=(26, 4), padx=24, anchor="w")

        self.ticket_subtitle = ctk.CTkLabel(
            self.ticket_card, text="No recent activity",
            font=("Segoe UI", 11.5), text_color=TEXT_SECONDARY)
        self.ticket_subtitle.pack(pady=(0, 18), padx=24, anchor="w")

        self.status_row = ctk.CTkFrame(self.ticket_card, fg_color="transparent")
        self.status_row.pack(padx=24, anchor="w", pady=(0, 14))

        self.status_dot = ctk.CTkLabel(
            self.status_row, text="●", font=("Segoe UI", 16),
            text_color=TEXT_SECONDARY)
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_text = ctk.CTkLabel(
            self.status_row, text="Idle — waiting for action",
            font=("Segoe UI", 13, "bold"), text_color=TEXT_SECONDARY)
        self.status_text.pack(side="left")

        self.detail_frame = ctk.CTkFrame(self.ticket_card, fg_color="#0c1426",
                                         corner_radius=14)
        self.detail_frame.pack(padx=24, pady=(0, 14), fill="x")

        self.row_ticket_id  = self._info_row(self.detail_frame, "Ticket ID",       "—")
        self.row_slot       = self._info_row(self.detail_frame, "Assigned Slot",   "—")
        self.row_duration   = self._info_row(self.detail_frame, "Duration",        "—")
        self.row_deducted   = self._info_row(self.detail_frame, "Hours Deducted",  "—")
        self.row_remaining  = self._info_row(self.detail_frame, "Remaining Hours", "—")
        self.row_extra_cost = self._info_row(self.detail_frame, "Extra Cost",      "—")

        self.message_label = ctk.CTkLabel(
            self.ticket_card, text="", font=("Segoe UI", 12),
            text_color=NEON_RED, wraplength=312, justify="left")
        self.message_label.pack(padx=24, pady=(4, 0), anchor="w")

        self.loading_bar = ctk.CTkProgressBar(
            self.ticket_card, width=312, height=6, corner_radius=4,
            progress_color=NEON_GREEN, fg_color="#0c1426")
        self.loading_bar.set(0)
        self.loading_bar.pack(padx=24, pady=(16, 0))
        self.loading_bar.pack_forget()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _resize_bg(self, event):
        if event.widget is not self or self._bg_pil is None:
            return

    def _fade_in(self):
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._alpha < 1.0:
            aid = self.after(16, self._fade_in)
            self.after_ids.append(aid)

    def _run_loading(self, on_done, steps=12, delay=18):
        self.loading_bar.pack(padx=24, pady=(16, 0))
        self.loading_bar.set(0)

        def step(i=0):
            self.loading_bar.set(i / steps)
            if i < steps:
                self.after(delay, lambda: step(i + 1))
            else:
                self.loading_bar.pack_forget()
                on_done()
        step()

    def _set_status(self, text, color):
        self.status_dot.configure(text_color=color)
        self.status_text.configure(text=text, text_color=color)

    def _set_message(self, text, color=NEON_RED):
        self.message_label.configure(text=text, text_color=color)

    def _reset_detail_panel(self):
        for row in (self.row_ticket_id, self.row_slot, self.row_duration,
                    self.row_deducted, self.row_remaining, self.row_extra_cost):
            row.configure(text="—")

    def stop_all(self):
        self.running = False
        for aid in self.after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        if hasattr(self, "particles"):
            self.particles.stop()

    # ── Action handlers ───────────────────────────────────────────────────────

    def handle_check_balance(self):
        balance = self.subscriber.check_balance()
        self._refresh_info_card()
        self._set_status("● Balance Updated", NEON_GREEN)
        self.ticket_title.configure(text="Balance Check")
        self.ticket_subtitle.configure(text="Latest subscription balance")
        self._set_message(
            f"You currently have {round(balance, 2)} subscription hours remaining.",
            NEON_GREEN)

    def handle_park(self):
        plate = self.plate_entry.get().strip().upper()
        vtype = self.vehicle_type_combo.get()
        self._set_message("")

        if not plate:
            self._set_message("Please enter the vehicle plate number.")
            return

        self.park_btn.configure(state="disabled")
        self._set_status("Processing...", NEON_BLUE)

        def do_park():
            new_vehicle = vehicle(plate_num=plate, vehicle_type=vtype,
                                  vehicle_color="N/A")
            result = self.subscriber.park_vehicle(new_vehicle)

            if result["status"] == "parked":
                ticket = result["ticket"]
                self.ticket_title.configure(text="Ticket Issued")
                self.ticket_subtitle.configure(
                    text=f"Subscriber: {self.subscriber.name}")
                self._reset_detail_panel()
                self.row_ticket_id.configure(text=ticket.ticket_id)
                self.row_slot.configure(text=ticket.slot_id)
                self._set_status("● Parked Successfully", NEON_GREEN)
                self._set_message(
                    f"Vehicle parked at slot {ticket.slot_id}. "
                    f"Use Ticket ID {ticket.ticket_id} when exiting.",
                    NEON_GREEN)
            elif result["status"] == "queue":
                self._reset_detail_panel()
                self.ticket_title.configure(text="Waiting Queue")
                self.ticket_subtitle.configure(
                    text=f"Subscriber: {self.subscriber.name}")
                self._set_status("● Added to Waiting Queue", NEON_CYAN)
                self._set_message(result["message"], NEON_CYAN)
            else:
                self._set_status("● Error", NEON_RED)
                self._set_message(result["message"], NEON_RED)

            self.park_btn.configure(state="normal")

        self._run_loading(do_park)

    def handle_exit(self):
        ticket_id = self.ticket_id_entry.get().strip().upper()
        self._set_message("")

        if not ticket_id:
            self._set_message("Please enter a valid Ticket ID.")
            return

        self.exit_btn.configure(state="disabled")
        self._set_status("Processing...", NEON_BLUE)

        def do_exit():
            result = self.subscriber.exit_vehicle(ticket_id)

            if isinstance(result, str):
                self._set_status("● Error", NEON_RED)
                self._set_message(result, NEON_RED)
            else:
                ticket    = result["ticket"]
                duration  = ticket.duration
                remaining = self.subscriber.subscription_hours

                if ticket.cost and ticket.cost > 0:
                    extra_hours = ticket.cost / self.parking_lot.rate_per_hour
                    deducted    = duration - extra_hours
                else:
                    extra_hours = 0
                    deducted    = duration

                self.ticket_title.configure(text="Exit Receipt")
                self.ticket_subtitle.configure(
                    text="Thank you for parking with us")
                self.row_ticket_id.configure(text=ticket.ticket_id)
                self.row_slot.configure(text=ticket.slot_id)
                self.row_duration.configure(text=f"{round(duration, 4)} hrs")
                self.row_deducted.configure(text=f"{round(deducted, 4)} hrs")
                self.row_remaining.configure(text=f"{round(remaining, 2)} hrs")

                if ticket.cost and ticket.cost > 0:
                    self.row_extra_cost.configure(
                        text=f"{round(ticket.cost, 2)} EGP",
                        text_color=NEON_RED)
                    self._set_status("● Extra Payment Required", "#ffd166")
                else:
                    self.row_extra_cost.configure(text="0 EGP",
                                                  text_color=TEXT_PRIMARY)
                    self._set_status("● Exit Successful", NEON_GREEN)

                self._set_message(
                    result["message"],
                    NEON_GREEN if not ticket.cost else "#ffd166")
                self._refresh_info_card()

            self.exit_btn.configure(state="normal")

        self._run_loading(do_exit)

    def handle_view_history(self):
        self.ticket_title.configure(text="Parking History")
        self.ticket_subtitle.configure(text="Coming soon")
        self._set_status("● Feature Not Available Yet", TEXT_SECONDARY)
        self._set_message(
            "Parking history tracking will be available in a future update.",
            NEON_CYAN)

    # ── Navigation (Back / Logout) ────────────────────────────────────────────

    def handle_back(self):
        from gui.subscriberLogin import SubscriberLoginScreen

        self.stop_all()
        self.destroy()

        app = SubscriberLoginScreen(
            subscriber_manager=self.subscriber_manager,
            parking_lot=self.parking_lot
        )
        app.mainloop()

    def handle_logout(self):
        from gui.start_screen import StartScreen

        self.stop_all()
        self.destroy()

        app = StartScreen()
        app.mainloop()


if __name__ == "__main__":
    from models.parking_lot import ParkingLot
    from models.parking_slot import ParkingSlot
    from models.subscriber_customer import SubscriberCustomer, SubscriberManager

    lot = ParkingLot(rate_per_hour=10)
    for i in range(1, 4):
        lot.add_slot(ParkingSlot(slot_id=f"A{i}"))

    manager = SubscriberManager()
    sub = SubscriberCustomer(name="Asmaa", parking_lot=lot,
                             subscription_hours=12)
    manager.add_subscriber(sub)

    app = SubscriberDashboard(subscriber=sub, parking_lot=lot,
                              subscriber_manager=manager)
    app.mainloop()