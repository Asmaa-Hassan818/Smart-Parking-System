"""
Smart Parking System - Subscriber Login Screen (CustomTkinter)
Matches Start Screen & Admin Login design, with a neon-green "premium member" theme.

Run:
    python subscriber_login.py
(expects assets/bg.png next to this file)
"""

import customtkinter as ctk
import os
import math
import random

ctk.set_appearance_mode("dark")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_PATH = os.path.join(BASE_DIR, "assets", "bg.png")

# ---- Palette ----
BG_COLOR       = "#0b0f1a"
PANEL_COLOR    = "#121829"
PANEL_BORDER   = "#1f2a44"
NEON_GREEN     = "#39ffb0"
NEON_BLUE      = "#3ad6ff"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"


class ParticleOverlay(ctk.CTkCanvas):
    """Floating neon particles drifting upward."""

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
            color = random.choice([NEON_GREEN, NEON_BLUE])
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
    """CTkButton with a hover border-glow illusion."""

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
    def __init__(self):
        super().__init__()
        self.title("Smart Parking System - Subscriber Login")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_COLOR)

        # ---------- background image ----------
        self._bg_ctk = None
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        # particle overlay
        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        # ---------- glassmorphism login panel ----------
        self.panel = ctk.CTkFrame(
            self, width=440, height=500, corner_radius=24,
            fg_color=PANEL_COLOR, border_width=2, border_color=NEON_GREEN
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center")
        self.panel.pack_propagate(False)

        # premium badge (top-right of panel)
        self.badge = ctk.CTkLabel(
            self.panel, text="★ PREMIUM MEMBER",
            font=("Segoe UI", 10, "bold"), text_color="#06241c",
            fg_color=NEON_GREEN, corner_radius=12, padx=10, pady=3
        )
        self.badge.place(relx=0.97, rely=0.035, anchor="ne")

        # icon ring (membership card)
        self.icon_ring = ctk.CTkFrame(
            self.panel, width=90, height=90, corner_radius=45,
            fg_color="#0e2a22", border_width=2, border_color=NEON_GREEN
        )
        self.icon_ring.pack(pady=(46, 14))
        self.icon_ring.pack_propagate(False)
        ctk.CTkLabel(
            self.icon_ring, text="💳", font=("Segoe UI Emoji", 36)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # title + subtitle
        ctk.CTkLabel(
            self.panel, text="Subscriber Login",
            font=("Segoe UI", 26, "bold"), text_color=TEXT_PRIMARY
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            self.panel, text="Access your subscription account and parking services",
            font=("Segoe UI", 12), text_color=TEXT_SECONDARY,
            wraplength=340, justify="center"
        ).pack(pady=(0, 30))

        # input field
        self.customer_id_entry = ctk.CTkEntry(
            self.panel, width=320, height=46, corner_radius=12,
            placeholder_text="Enter Customer ID",
            fg_color="#0c1426", border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13)
        )
        self.customer_id_entry.pack(pady=(0, 8))
        self.customer_id_entry.bind("<FocusIn>", self._entry_focus_in)
        self.customer_id_entry.bind("<FocusOut>", self._entry_focus_out)
        self.customer_id_entry.bind("<Return>", lambda e: self.handle_login())

        # status message
        self.message_label = ctk.CTkLabel(
            self.panel, text="", font=("Segoe UI", 11.5), text_color="#ff6b6b"
        )
        self.message_label.pack(pady=(2, 6))

        # Login button (primary, neon green glow)
        self.login_btn = GlowButton(
            self.panel, glow_color=NEON_BLUE,
            text="Login", width=320, height=46, corner_radius=12,
            fg_color=NEON_GREEN, hover_color="#6affc7",
            text_color="#06241c", font=("Segoe UI", 14, "bold"),
            command=self.handle_login
        )
        self.login_btn.pack(pady=(8, 12))

        # Back button (glassmorphism / minimal)
        self.back_btn = GlowButton(
            self.panel, glow_color=NEON_BLUE,
            text="← Back", width=320, height=42, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self.go_back
        )
        self.back_btn.pack(pady=(0, 0))
        self.back_btn.bind("<Enter>", lambda e: self.back_btn.configure(
            text_color=TEXT_PRIMARY, border_color=NEON_GREEN))
        self.back_btn.bind("<Leave>", lambda e: self.back_btn.configure(
            text_color=TEXT_SECONDARY, border_color=PANEL_BORDER))

        # footer
        ctk.CTkLabel(
            self, text="SMART PARKING SYSTEM  ©  2026",
            font=("Segoe UI", 11), text_color=TEXT_SECONDARY
        ).place(relx=0.5, rely=0.97, anchor="center")

        # ---------- entrance animation ----------
        self.attributes("-alpha", 0.0)
        self._alpha = 0.0
        self._slide_offset = 40
        self.after(50, self._animate_entrance)

        # pulsing glow on icon ring + panel border
        self._glow_up = True
        self.after(200, self._pulse_glow)

    # ---------- background handling ----------
    def _resize_bg(self, event):
        if event.widget is not self or self._bg_pil is None:
            return
        w, h = max(event.width, 1), max(event.height, 1)

    def _animate_entrance(self):
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)

        if self._slide_offset > 0:
            self._slide_offset -= 3
            self.panel.place(relx=0.5, rely=0.5, anchor="center", y=self._slide_offset)

        if self._alpha < 1.0 or self._slide_offset > 0:
            self.after(16, self._animate_entrance)

    # ---------- pulsing neon glow ----------
    def _pulse_glow(self):
        if self._glow_up:
            self.icon_ring.configure(border_color=NEON_BLUE)
            self.panel.configure(border_color="#2de8a0")
        else:
            self.icon_ring.configure(border_color=NEON_GREEN)
            self.panel.configure(border_color=NEON_GREEN)
        self._glow_up = not self._glow_up
        self.after(900, self._pulse_glow)

    # ---------- input focus glow ----------
    def _entry_focus_in(self, _e=None):
        self.customer_id_entry.configure(border_color=NEON_GREEN, border_width=2)

    def _entry_focus_out(self, _e=None):
        self.customer_id_entry.configure(border_color=PANEL_BORDER, border_width=1.5)

    # ---------- actions ----------
    def handle_login(self):
        customer_id = self.customer_id_entry.get().strip().upper()

        # placeholder validation - replace with subscriber_manager.search_subscriber(customer_id)
        if customer_id.startswith("SUB") and len(customer_id) >= 4:
            self.message_label.configure(
                text_color=NEON_GREEN,
                text=f"Welcome back, {customer_id}!"
            )
            print(f"Login success -> open Subscriber Dashboard for {customer_id}")
            #self.destroy(); open SubscriberDashboard(subscriber)
        else:
            self.message_label.configure(
                text_color="#ff6b6b",
                text="Customer ID not found. Please try again."
            )

    def go_back(self):
        print("Go back to Start Screen")
        #self.destroy(); open StartScreen()


if __name__ == "__main__":
    app = SubscriberLoginScreen()
    app.mainloop()