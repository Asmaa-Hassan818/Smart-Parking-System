import customtkinter as ctk
import os
import math
import random

ctk.set_appearance_mode("dark")

BG_COLOR       = "#0b0f1a"
PANEL_COLOR    = "#121829"
PANEL_BORDER   = "#1f2a44"
NEON_GREEN     = "#39ffb0"
NEON_BLUE      = "#3ad6ff"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"


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
                "id": item, "speed": speed,
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


class SubscriberLoginScreen(ctk.CTk):
    """
    Parameters
    ----------
    subscriber_manager : SubscriberManager
        Shared instance that holds all registered subscribers.
        Passed into the dashboard so Back can return here with the same data.
    parking_lot : ParkingLot | None
        Shared lot reference forwarded to the dashboard.
    """

    def __init__(self, subscriber_manager=None, parking_lot=None):
        super().__init__()

        self.subscriber_manager = subscriber_manager
        self.parking_lot = parking_lot
        self.after_ids = []
        self.running = True

        self.title("Smart Parking System - Subscriber Login")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_COLOR)

        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        self.panel = ctk.CTkFrame(
            self, width=440, height=500, corner_radius=24,
            fg_color=PANEL_COLOR, border_width=2, border_color=NEON_GREEN
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center")
        self.panel.pack_propagate(False)

        ctk.CTkLabel(
            self.panel, text="★ PREMIUM MEMBER",
            font=("Segoe UI", 10, "bold"),
            text_color="#06241c", fg_color=NEON_GREEN, corner_radius=12
        ).place(relx=0.97, rely=0.035, anchor="ne")

        self.icon_ring = ctk.CTkFrame(
            self.panel, width=90, height=90, corner_radius=45,
            fg_color="#0e2a22", border_width=2, border_color=NEON_GREEN
        )
        self.icon_ring.pack(pady=(46, 14))
        self.icon_ring.pack_propagate(False)
        ctk.CTkLabel(
            self.icon_ring, text="💳", font=("Segoe UI Emoji", 36)
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.panel, text="Subscriber Login",
            font=("Segoe UI", 26, "bold"), text_color=TEXT_PRIMARY
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            self.panel,
            text="Access your subscription account and parking services",
            font=("Segoe UI", 12), text_color=TEXT_SECONDARY,
            wraplength=340, justify="center"
        ).pack(pady=(0, 30))

        self.customer_id_entry = ctk.CTkEntry(
            self.panel, width=320, height=46, corner_radius=12,
            placeholder_text="Enter Customer ID  (e.g. SUB1000)",
            fg_color="#0c1426", border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        self.customer_id_entry.pack(pady=(0, 8))
        self.customer_id_entry.bind("<Return>", lambda e: self.handle_login())

        self.message_label = ctk.CTkLabel(
            self.panel, text="", font=("Segoe UI", 11.5),
            text_color="#ff6b6b"
        )
        self.message_label.pack(pady=(2, 6))

        GlowButton(
            self.panel, glow_color=NEON_BLUE,
            text="Login", width=320, height=46, corner_radius=12,
            fg_color=NEON_GREEN, hover_color="#6affc7",
            text_color="#06241c", font=("Segoe UI", 14, "bold"),
            command=self.handle_login
        ).pack(pady=(8, 12))

        GlowButton(
            self.panel, glow_color=NEON_BLUE,
            text="← Back", width=320, height=42, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self.go_back
        ).pack()

        self.attributes("-alpha", 0.0)
        self._alpha = 0.0
        self._slide_offset = 40
        self.after(50, self._animate_entrance)
        self._glow_up = True
        self.after(200, self._pulse_glow)

    def _resize_bg(self, event):
        return

    def _animate_entrance(self):
        if not self.running:
            return
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._slide_offset > 0:
            self._slide_offset -= 3
            self.panel.place(relx=0.5, rely=0.5, anchor="center",
                             y=self._slide_offset)
        if self._alpha < 1.0 or self._slide_offset > 0:
            aid = self.after(16, self._animate_entrance)
            self.after_ids.append(aid)

    def _pulse_glow(self):
        if not self.running:
            return
        if self._glow_up:
            self.icon_ring.configure(border_color=NEON_BLUE)
            self.panel.configure(border_color="#2de8a0")
        else:
            self.icon_ring.configure(border_color=NEON_GREEN)
            self.panel.configure(border_color=NEON_GREEN)
        self._glow_up = not self._glow_up
        aid = self.after(900, self._pulse_glow)
        self.after_ids.append(aid)

    def stop_all(self):
        self.running = False
        for aid in self.after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        if hasattr(self, "particles"):
            self.particles.stop()


    def handle_login(self):
        from gui.subscriber_screen import SubscriberDashboard

        customer_id = self.customer_id_entry.get().strip().upper()

        if not customer_id:
            self.message_label.configure(
                text_color="#ff6b6b", text="Please enter your Customer ID.")
            return

        if self.subscriber_manager is None:
            self.message_label.configure(
                text_color="#ff6b6b",
                text="System error: no subscriber registry available.")
            return

        subscriber = self.subscriber_manager.search_subscriber(customer_id)

        if subscriber is None:
            self.message_label.configure(
                text_color="#ff6b6b",
                text="Customer ID not found. Please try again.")
            return

        lot = self.parking_lot or subscriber.parking_lot

        self.stop_all()
        self.destroy()

        app = SubscriberDashboard(
            subscriber=subscriber,
            parking_lot=lot,
            subscriber_manager=self.subscriber_manager
        )
        app.mainloop()

    def go_back(self):
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
    print(f"Test ID: {sub.user_id}")

    app = SubscriberLoginScreen(subscriber_manager=manager, parking_lot=lot)
    app.mainloop()