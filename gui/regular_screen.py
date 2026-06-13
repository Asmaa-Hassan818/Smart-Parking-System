import customtkinter as ctk
import os
import math
import random

from models.vehicle import vehicle

ctk.set_appearance_mode("dark")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "assets", "bg.png")

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
            color = random.choice([NEON_BLUE, NEON_CYAN])
            item = self.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")
            self.particles.append({"id": item, "speed": speed, "phase": random.uniform(0, math.tau)})

    def _animate(self):
        h = self.winfo_height()
        for p in self.particles:
            p["phase"] += 0.03
            dx = math.sin(p["phase"]) * 0.4
            self.move(p["id"], dx, -p["speed"])
            coords = self.coords(p["id"])
            if coords and coords[1] < -5:
                self.move(p["id"], 0, h + 10)
        self.after(40, self._animate)


class GlowButton(ctk.CTkButton):

    def __init__(self, master, glow_color=NEON_BLUE, **kwargs):
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



class RegularCustomerScreen(ctk.CTk):

    VEHICLE_TYPES = ["Car", "SUV", "Motorcycle", "Van", "Truck"]

    def __init__(self, parking_lot, on_back=None):
        super().__init__()
        self._bg_pil = None
        self.parking_lot = parking_lot
        self.on_back = on_back
        self._bg_ctk = None
        self._alpha = 0.0

        self.title("Smart Parking System - Regular Customer")
        self.geometry("1200x780")
        self.minsize(1024, 680)
        self.configure(fg_color=BG_COLOR)

        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.place(relx=0.5, rely=0.055, anchor="n")

        self.icon_ring = ctk.CTkFrame(
            self.header, width=64, height=64, corner_radius=32,
            fg_color="#0e1f38", border_width=2, border_color=NEON_BLUE
        )
        self.icon_ring.pack(side="left", padx=(0, 14))
        self.icon_ring.pack_propagate(False)
        ctk.CTkLabel(self.icon_ring, text="🚗", font=("Segoe UI Emoji", 26)
                      ).place(relx=0.5, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="Regular Customer",
                     font=("Segoe UI", 24, "bold"), text_color=TEXT_PRIMARY
                     ).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Park your vehicle and pay based on your duration",
                     font=("Segoe UI", 12), text_color=TEXT_SECONDARY
                     ).pack(anchor="w")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.58, anchor="center")

        self.form_card = GlassCard(self.content, border_color=NEON_BLUE,
                                    width=380, height=430)
        self.form_card.grid(row=0, column=0, padx=20, sticky="n")
        self.form_card.grid_propagate(False)
        self._build_form()

        self.ticket_card = GlassCard(self.content, border_color=PANEL_BORDER,
                                      width=380, height=430)
        self.ticket_card.grid(row=0, column=1, padx=20, sticky="n")
        self.ticket_card.grid_propagate(False)
        self._build_ticket_panel()

        ctk.CTkLabel(
            self, text="SMART PARKING SYSTEM  ©  2026",
            font=("Segoe UI", 11), text_color=TEXT_SECONDARY
        ).place(relx=0.5, rely=0.975, anchor="center")

        self.attributes("-alpha", 0.0)
        self.after(50, self._fade_in)

    def _build_form(self):
        ctk.CTkLabel(self.form_card, text="Vehicle Information",
                     font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY
                     ).pack(pady=(26, 4), padx=24, anchor="w")
        ctk.CTkLabel(self.form_card, text="Enter your details to park or exit",
                     font=("Segoe UI", 11.5), text_color=TEXT_SECONDARY
                     ).pack(pady=(0, 18), padx=24, anchor="w")

        self.name_entry = self._labeled_entry("Customer Name", "Enter your full name")
        self.plate_entry = self._labeled_entry("Plate Number", "e.g. ABC 1234")

        ctk.CTkLabel(self.form_card, text="Vehicle Type",
                     font=("Segoe UI", 12, "bold"), text_color=TEXT_SECONDARY
                     ).pack(pady=(8, 4), padx=24, anchor="w")
        self.vehicle_type_combo = ctk.CTkComboBox(
            self.form_card, values=self.VEHICLE_TYPES, width=332, height=42,
            corner_radius=12, fg_color=INPUT_BG, border_color=PANEL_BORDER,
            button_color="#1b2740", button_hover_color=NEON_BLUE,
            dropdown_fg_color=PANEL_COLOR, dropdown_hover_color="#1b2740",
            text_color=TEXT_PRIMARY, font=("Segoe UI", 13)
        )
        self.vehicle_type_combo.set(self.VEHICLE_TYPES[0])
        self.vehicle_type_combo.pack(padx=24, pady=(0, 12))

        self.park_btn = GlowButton(
            self.form_card, glow_color=NEON_BLUE,
            text="🅿  Park Vehicle", width=332, height=46, corner_radius=12,
            fg_color=NEON_BLUE, hover_color=NEON_CYAN,
            text_color="#06141f", font=("Segoe UI", 14, "bold"),
            command=self.handle_park
        )
        self.park_btn.pack(padx=24, pady=(10, 8))

        self.exit_btn = GlowButton(
            self.form_card, glow_color=NEON_CYAN,
            text="🚪  Exit Vehicle", width=332, height=44, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=NEON_CYAN,
            text_color=NEON_CYAN, font=("Segoe UI", 13, "bold"),
            command=self.handle_exit
        )
        self.exit_btn.pack(padx=24, pady=(0, 8))

        self.back_btn = GlowButton(
            self.form_card, glow_color=NEON_GREEN,
            text="←  Back", width=332, height=40, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self.handle_back
        )
        self.back_btn.pack(padx=24, pady=(0, 0))
        self.back_btn.bind("<Enter>", lambda e: self.back_btn.configure(
            text_color=TEXT_PRIMARY, border_color=NEON_GREEN))
        self.back_btn.bind("<Leave>", lambda e: self.back_btn.configure(
            text_color=TEXT_SECONDARY, border_color=PANEL_BORDER))

    def _labeled_entry(self, label_text, placeholder):
        ctk.CTkLabel(self.form_card, text=label_text,
                     font=("Segoe UI", 12, "bold"), text_color=TEXT_SECONDARY
                     ).pack(pady=(8, 4), padx=24, anchor="w")
        entry = ctk.CTkEntry(
            self.form_card, width=332, height=42, corner_radius=12,
            placeholder_text=placeholder,
            fg_color=INPUT_BG, border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        entry.pack(padx=24)
        entry.bind("<FocusIn>", lambda e: entry.configure(border_color=NEON_BLUE, border_width=2))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=PANEL_BORDER, border_width=1.5))
        return entry

    def _build_ticket_panel(self):
        self.ticket_title = ctk.CTkLabel(
            self.ticket_card, text="Parking Status",
            font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY
        )
        self.ticket_title.pack(pady=(26, 4), padx=24, anchor="w")

        self.ticket_subtitle = ctk.CTkLabel(
            self.ticket_card, text="No active ticket yet",
            font=("Segoe UI", 11.5), text_color=TEXT_SECONDARY
        )
        self.ticket_subtitle.pack(pady=(0, 18), padx=24, anchor="w")

        # status indicator dot + label
        self.status_row = ctk.CTkFrame(self.ticket_card, fg_color="transparent")
        self.status_row.pack(padx=24, anchor="w", pady=(0, 14))

        self.status_dot = ctk.CTkLabel(
            self.status_row, text="●", font=("Segoe UI", 16),
            text_color=TEXT_SECONDARY
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_text = ctk.CTkLabel(
            self.status_row, text="Idle — waiting for action",
            font=("Segoe UI", 13, "bold"), text_color=TEXT_SECONDARY
        )
        self.status_text.pack(side="left")

        # info rows (ticket id / slot / duration / cost)
        self.info_frame = ctk.CTkFrame(self.ticket_card, fg_color="#0c1426",
                                        corner_radius=14)
        self.info_frame.pack(padx=24, pady=(0, 14), fill="x")

        self.row_ticket_id = self._info_row("Ticket ID", "—")
        self.row_slot = self._info_row("Assigned Slot", "—")
        self.row_duration = self._info_row("Duration", "—")
        self.row_cost = self._info_row("Cost", "—")

        self.message_label = ctk.CTkLabel(
            self.ticket_card, text="", font=("Segoe UI", 12),
            text_color=NEON_RED, wraplength=320, justify="left"
        )
        self.message_label.pack(padx=24, pady=(4, 0), anchor="w")

        self.loading_bar = ctk.CTkProgressBar(
            self.ticket_card, width=332, height=6, corner_radius=4,
            progress_color=NEON_BLUE, fg_color="#0c1426"
        )
        self.loading_bar.set(0)
        self.loading_bar.pack(padx=24, pady=(16, 0))
        self.loading_bar.pack_forget()  # hidden until used

    def _info_row(self, label, value):
        row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(row, text=label, font=("Segoe UI", 12),
                     text_color=TEXT_SECONDARY).pack(side="left")
        val_label = ctk.CTkLabel(row, text=value, font=("Segoe UI", 13, "bold"),
                                  text_color=TEXT_PRIMARY)
        val_label.pack(side="right")
        return val_label

    def _resize_bg(self, event):
        if event.widget is not self:
            return
        if self._bg_pil is None:
            return

        w, h = max(event.width, 1), max(event.height, 1)

    def _fade_in(self):
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._alpha < 1.0:
            self.after(16, self._fade_in)

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

    def _reset_ticket_panel(self):
        self.row_ticket_id.configure(text="—")
        self.row_slot.configure(text="—")
        self.row_duration.configure(text="—")
        self.row_cost.configure(text="—")

    def handle_park(self):
        name = self.name_entry.get().strip()
        plate = self.plate_entry.get().strip().upper()
        vtype = self.vehicle_type_combo.get()

        self._set_message("")

        if not name:
            self._set_message("Please enter the customer name.")
            return
        if not plate:
            self._set_message("Please enter the vehicle plate number.")
            return

        self.park_btn.configure(state="disabled")
        self._set_status("Processing...", NEON_BLUE)

        def do_park():
            new_vehicle = vehicle(plate_num=plate, vehicle_type=vtype, vehicle_color="N/A")

            result = self.parking_lot.assign_vehicle(new_vehicle,None)

            if result["status"] == "parked":
                ticket = result["ticket"]
                self.ticket_title.configure(text="Ticket Issued")
                self.ticket_subtitle.configure(text=f"Welcome, {name}!")
                self.row_ticket_id.configure(text=ticket.ticket_id)
                self.row_slot.configure(text=ticket.slot_id)
                self.row_duration.configure(text="In progress")
                self.row_cost.configure(text="—")
                self._set_status("● Parked Successfully", NEON_GREEN)
                self._set_message(
                    f"Vehicle parked at slot {ticket.slot_id}. "
                    f"Keep your Ticket ID ({ticket.ticket_id}) for exit.",
                    NEON_GREEN
                )

            elif result["status"] == "queue":
                self._reset_ticket_panel()
                self.ticket_title.configure(text="Waiting Queue")
                self.ticket_subtitle.configure(text=f"Hello, {name}")
                self._set_status("● Added to Waiting Queue", NEON_CYAN)
                self._set_message(result["message"], NEON_CYAN)

            else:
                self._set_status("● Error", NEON_RED)
                self._set_message(result["message"], NEON_RED)

            self.park_btn.configure(state="normal")

        self._run_loading(do_park)

    def handle_exit(self):
        self._ask_ticket_id(callback=self._process_exit)

    def _process_exit(self, ticket_id):
        ticket_id = (ticket_id or "").strip().upper()
        if not ticket_id:
            self._set_message("Please enter a valid Ticket ID.")
            return

        self.exit_btn.configure(state="disabled")
        self._set_status("Processing...", NEON_BLUE)

        def do_exit():
            result = self.parking_lot.remove_vehicle(ticket_id)

            if result["status"] == "error":
                self._set_status("● Error", NEON_RED)
                self._set_message(result["message"], NEON_RED)
            else:
                ticket = result["ticket"]
                self.ticket_title.configure(text="Exit Receipt")
                self.ticket_subtitle.configure(text="Thank you for parking with us")
                self.row_ticket_id.configure(text=ticket.ticket_id)
                self.row_slot.configure(text=ticket.slot_id)
                self.row_duration.configure(text=f"{round(ticket.duration, 4)} hrs")
                self.row_cost.configure(text=f"{round(ticket.cost, 2)} EGP")
                self._set_status("● Exit Successful", NEON_GREEN)

                msg = f"Total cost: {round(ticket.cost, 2)} EGP for {round(ticket.duration, 4)} hours."
                if result.get("queue_processed"):
                    new_t = result["queue_processed"]
                    msg += f"\nSlot {new_t.slot_id} assigned to next vehicle in queue ({new_t.ticket_id})."
                self._set_message(msg, NEON_GREEN)

            self.exit_btn.configure(state="normal")

        self._run_loading(do_exit)


    def _ask_ticket_id(self, callback):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Exit Vehicle")
        dialog.geometry("360x220")
        dialog.configure(fg_color=BG_COLOR)
        dialog.attributes("-topmost", True)
        dialog.resizable(False, False)
        dialog.grab_set()  # make it modal

        card = GlassCard(dialog, border_color=NEON_CYAN, width=320, height=190)
        card.pack(padx=18, pady=18)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Enter Ticket ID", font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(22, 4))
        ctk.CTkLabel(card, text="You can find this on your parking receipt",
                     font=("Segoe UI", 11), text_color=TEXT_SECONDARY).pack(pady=(0, 12))

        entry = ctk.CTkEntry(
            card, width=260, height=42, corner_radius=12,
            placeholder_text="e.g. T1000",
            fg_color=INPUT_BG, border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        entry.pack(pady=(0, 12))
        entry.focus_set()

        def submit():
            value = entry.get()
            dialog.destroy()
            callback(value)

        entry.bind("<Return>", lambda e: submit())

        confirm_btn = GlowButton(
            card, glow_color=NEON_BLUE, text="Confirm", width=260, height=40,
            corner_radius=12, fg_color=NEON_CYAN, hover_color=NEON_BLUE,
            text_color="#06141f", font=("Segoe UI", 13, "bold"),
            command=submit
        )
        confirm_btn.pack()

    def handle_back(self):
        if self.on_back:
            self.on_back()
        else:
            from gui.start_screen import StartScreen
            app = StartScreen()
            self.destroy()
            app.mainloop()


if __name__ == "__main__":
    from models.parking_lot import ParkingLot
    from models.parking_slot import ParkingSlot

    lot = ParkingLot(rate_per_hour=10)
    for i in range(1, 6):
        lot.add_slot(ParkingSlot(slot_id=f"A{i}"))

    app = RegularCustomerScreen(parking_lot=lot)
    app.mainloop()