import customtkinter as ctk
import tkinter as tk
import math
import random

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#0b0f1a"
PANEL_COLOR = "#121829"
PANEL_BORDER = "#1f2a44"
NEON_BLUE = "#3ad6ff"
NEON_GREEN = "#39ffb0"
TEXT_PRIMARY = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"
CARD_HOVER_BLUE = "#16314f"
CARD_HOVER_GREEN = "#143a30"


class ParticleCanvas(tk.Canvas):

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.particles = []
        self.icons = []
        self.bind("<Configure>", self._on_resize)
        self._init_done = False
        self.running = True

    def _on_resize(self, event):
        if not self._init_done:
            self._init_done = True
            self._build_particles(event.width, event.height)
            self._build_floating_icons(event.width, event.height)
            self._animate()

    def _build_particles(self, w, h):
        for _ in range(55):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            r = random.uniform(1, 3)
            speed = random.uniform(0.15, 0.6)
            color = random.choice([NEON_BLUE, NEON_GREEN, "#3a4a6b"])
            item = self.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline="")
            self.particles.append({
                "id": item, "x": x, "y": y, "r": r,
                "speed": speed, "phase": random.uniform(0, math.tau)
            })

    def _build_floating_icons(self, w, h):
        for g in ["🅿", "🚗", "🚘", "⚡", "🛰", "🅿"]:
            x = random.uniform(0.05 * w, 0.95 * w)
            y = random.uniform(0.1 * h, 0.9 * h)
            item = self.create_text(
                x, y, text=g,
                font=("Segoe UI Emoji", random.randint(18, 34)),
                fill="#22304f"
            )
            self.icons.append({
                "id": item, "x": x, "y": y,
                "vy": random.uniform(-0.08, -0.25),
                "phase": random.uniform(0, math.tau)
            })

    def _animate(self):
        if not self.running:
            return
        w = self.winfo_width()
        h = self.winfo_height()

        for p in self.particles:
            p["phase"] += 0.02
            p["y"] += p["speed"]
            dx = math.sin(p["phase"]) * 0.4
            if p["y"] > h:
                p["y"] = -5
                p["x"] = random.uniform(0, w)
            self.move(p["id"], dx, p["speed"])

        for ic in self.icons:
            ic["phase"] += 0.01
            dx = math.sin(ic["phase"]) * 0.3
            self.move(ic["id"], dx, ic["vy"])
            coords = self.coords(ic["id"])
            if coords and coords[1] < -40:
                self.moveto(ic["id"],
                            random.uniform(0.05 * w, 0.95 * w), h + 20)

        try:
            self.after(40, self._animate)
        except Exception:
            return

    def stop(self):
        self.running = False


class ActionCard(ctk.CTkFrame):

    def __init__(self, master, icon, title, subtitle, accent,
                 command=None, **kwargs):
        super().__init__(
            master, corner_radius=20, fg_color=PANEL_COLOR,
            border_width=2, border_color=PANEL_BORDER, **kwargs
        )
        self.accent = accent
        self.command = command
        self.base_border = PANEL_BORDER
        self._hover_color = (CARD_HOVER_BLUE if accent == NEON_BLUE
                             else CARD_HOVER_GREEN)

        self.grid_propagate(False)
        self.configure(width=300, height=360)

        self.icon_frame = ctk.CTkFrame(
            self, width=72, height=72, corner_radius=36,
            fg_color="#1a2236", border_width=2, border_color=accent
        )
        self.icon_frame.pack(pady=(36, 18))
        self.icon_frame.pack_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_frame, text=icon,
            font=("Segoe UI Emoji", 30), text_color=accent
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(
            self, text=title,
            font=("Segoe UI Semibold", 20, "bold"), text_color=TEXT_PRIMARY
        )
        self.title_label.pack(pady=(0, 6))

        self.subtitle_label = ctk.CTkLabel(
            self, text=subtitle, font=("Segoe UI", 12),
            text_color=TEXT_SECONDARY, wraplength=190, justify="center"
        )
        self.subtitle_label.pack(pady=(0, 18))

        self.enter_btn = ctk.CTkLabel(
            self, text="Continue  →",
            font=("Segoe UI", 12, "bold"), text_color=accent
        )
        self.enter_btn.pack(pady=(0, 10))

        for widget in (self, self.icon_frame, self.icon_label,
                       self.title_label, self.subtitle_label, self.enter_btn):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            widget.configure(cursor="hand2")

    def _on_enter(self, _event=None):
        self.configure(border_color=self.accent,
                       fg_color=self._hover_color, border_width=3)

    def _on_leave(self, _event=None):
        self.configure(border_color=self.base_border,
                       fg_color=PANEL_COLOR, border_width=2)

    def _on_click(self, _event=None):
        if self.command:
            self.command()


class StartScreen(ctk.CTk):
    """
    Parameters
    ----------
    parking_lot        : ParkingLot       – shared lot (required for all screens)
    subscriber_manager : SubscriberManager – shared manager (required for subscriber flow)
    """

    def __init__(self, parking_lot=None, subscriber_manager=None):
        super().__init__()

        # Store shared state so it can be forwarded to child screens
        self.parking_lot = parking_lot
        self.subscriber_manager = subscriber_manager

        self.title("Smart Parking System")
        self.geometry("1100x720")
        self.minsize(960, 640)
        self.configure(fg_color=BG_COLOR)

        self.bg_canvas = ParticleCanvas(self)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.content, text="🅿️ SMART PARKING SYSTEM",
            font=("Segoe UI", 30, "bold"), text_color=NEON_BLUE
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            self.content, text="Welcome to Smart Parking System",
            font=("Segoe UI", 26, "bold"), text_color=TEXT_PRIMARY
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            self.content,
            text="Efficient Parking Management for Administrators and Customers",
            font=("Segoe UI", 14), text_color=TEXT_SECONDARY
        ).pack(pady=(0, 36))

        self.cards_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.cards_frame.pack(pady=(0, 24))

        ActionCard(
            self.cards_frame, icon="🛡️", title="Admin",
            subtitle="Manage parking slots, subscribers and monitor the garage",
            accent=NEON_BLUE, command=self.open_admin
        ).grid(row=0, column=0, padx=18)

        ActionCard(
            self.cards_frame, icon="💳", title="Subscriber",
            subtitle="Login with your membership ID and manage your parking hours",
            accent=NEON_GREEN, command=self.open_subscriber
        ).grid(row=0, column=1, padx=18)

        ActionCard(
            self.cards_frame, icon="🚗", title="Regular Customer",
            subtitle="Park your vehicle and pay based on your parking duration",
            accent=NEON_BLUE, command=self.open_regular
        ).grid(row=0, column=2, padx=18)

        ctk.CTkLabel(
            self, text="Smart Parking System © 2026",
            font=("Segoe UI", 11), text_color=TEXT_SECONDARY
        ).place(relx=0.5, rely=0.97, anchor="center")

        self._fade_alpha = 0.0
        self._slide_offset = 40
        self.attributes("-alpha", 0.0)
        self.after(50, self._animate_entrance)

    def _animate_entrance(self):
        self._fade_alpha = min(1.0, self._fade_alpha + 0.06)
        self.attributes("-alpha", self._fade_alpha)
        if self._slide_offset > 0:
            self._slide_offset -= 3
            self.content.place(relx=0.5, rely=0.5, anchor="center",
                               y=self._slide_offset)
        if self._fade_alpha < 1.0 or self._slide_offset > 0:
            self.after(16, self._animate_entrance)

    def _go(self, build_fn):
        """Stop canvas, destroy self, then open the next screen."""
        self.bg_canvas.stop()
        self.destroy()
        build_fn()

    def open_admin(self):
        def go():
            from gui.adminLogin import AdminLoginScreen
            AdminLoginScreen().mainloop()

        self._go(go)

    def open_subscriber(self):
        def go():
            from gui.subscriberLogin import SubscriberLoginScreen
            SubscriberLoginScreen(
                subscriber_manager=self.subscriber_manager,
                parking_lot=self.parking_lot
            ).mainloop()

        self._go(go)

    def open_regular(self):
        def go():
            from gui.regular_screen import RegularCustomerScreen
            RegularCustomerScreen(
                parking_lot=self.parking_lot
            ).mainloop()

        self._go(go)


if __name__ == "__main__":
    from models.parking_lot import ParkingLot
    from models.parking_slot import ParkingSlot
    from models.subscriber_customer import SubscriberCustomer, SubscriberManager

    lot = ParkingLot(rate_per_hour=10)
    for i in range(1, 6):
        lot.add_slot(ParkingSlot(slot_id=f"A{i}"))

    manager = SubscriberManager()
    sub = SubscriberCustomer(name="Asmaa", parking_lot=lot, subscription_hours=12)
    manager.add_subscriber(sub)

    StartScreen(parking_lot=lot, subscriber_manager=manager).mainloop()
