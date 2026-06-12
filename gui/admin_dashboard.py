"""
Smart Parking System - Admin Dashboard (CustomTkinter)
Matches Start Screen / Admin Login / Subscriber Login design language.

Run:
    python admin_dashboard.py
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
NEON_BLUE      = "#3ad6ff"
NEON_GREEN     = "#39ffb0"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"
SLOT_FREE      = "#173a2f"
SLOT_FREE_BD   = NEON_GREEN
SLOT_OCC       = "#3a1f25"
SLOT_OCC_BD    = "#ff6b6b"


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
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            r = random.uniform(1.2, 3)
            speed = random.uniform(0.25, 0.8)
            color = random.choice([NEON_BLUE, NEON_GREEN])
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


class GlassFrame(ctk.CTkFrame):
    """Reusable glassmorphism panel."""

    def __init__(self, master, accent=NEON_BLUE, **kwargs):
        kwargs.setdefault("corner_radius", 18)
        kwargs.setdefault("fg_color", PANEL_COLOR)
        kwargs.setdefault("border_width", 1.5)
        kwargs.setdefault("border_color", PANEL_BORDER)
        super().__init__(master, **kwargs)
        self.accent = accent


class StatCard(GlassFrame):
    """Small KPI card: icon, value, label."""

    def __init__(self, master, icon, value, label, accent=NEON_BLUE):
        super().__init__(master, accent=accent, height=110)
        self.grid_propagate(False)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))

        icon_box = ctk.CTkFrame(top, width=42, height=42, corner_radius=12,
                                 fg_color="#0c1830", border_width=1.5, border_color=accent)
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, font=("Segoe UI Emoji", 18)).place(relx=0.5, rely=0.5, anchor="center")

        self.value_label = ctk.CTkLabel(top, text=value, font=("Segoe UI", 26, "bold"), text_color=TEXT_PRIMARY)
        self.value_label.pack(side="right")

        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12), text_color=TEXT_SECONDARY) \
            .pack(anchor="w", padx=18, pady=(6, 14))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


class NavButton(ctk.CTkButton):
    """Sidebar navigation button with active/glow states."""

    def __init__(self, master, icon, text, command=None, active=False):
        super().__init__(
            master, text=f"  {icon}   {text}", anchor="w",
            font=("Segoe UI", 13, "bold" if active else "normal"),
            height=44, corner_radius=12,
            fg_color="#16263f" if active else "transparent",
            hover_color="#16263f",
            text_color=NEON_BLUE if active else TEXT_SECONDARY,
            border_width=1.5 if active else 0,
            border_color=NEON_BLUE,
            command=command
        )
        self.active = active
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e=None):
        if not self.active:
            self.configure(text_color=TEXT_PRIMARY)

    def _on_leave(self, _e=None):
        if not self.active:
            self.configure(text_color=TEXT_SECONDARY)


class SlotTile(ctk.CTkFrame):
    """A single parking slot tile for the visual parking map."""

    def __init__(self, master, slot_id, occupied=False, plate=""):
        bg = SLOT_OCC if occupied else SLOT_FREE
        border = SLOT_OCC_BD if occupied else SLOT_FREE_BD
        super().__init__(master, width=92, height=72, corner_radius=12,
                          fg_color=bg, border_width=1.5, border_color=border)
        self.grid_propagate(False)

        ctk.CTkLabel(self, text=slot_id, font=("Segoe UI", 13, "bold"),
                      text_color=TEXT_PRIMARY).place(relx=0.5, rely=0.32, anchor="center")

        status_text = plate if occupied else "Free"
        status_color = "#ffb3b3" if occupied else "#9affd6"
        ctk.CTkLabel(self, text=status_text, font=("Segoe UI", 10),
                      text_color=status_color).place(relx=0.5, rely=0.72, anchor="center")


class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart Parking System - Admin Dashboard")
        self.geometry("1300x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG_COLOR)

        # ---------- background ----------
        self._bg_ctk = None
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._resize_bg)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        # ---------- layout container ----------
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.96, relheight=0.94)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # ===================== SIDEBAR =====================
        self.sidebar = GlassFrame(self.container, width=230, corner_radius=20)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=(0, 18))
        self.sidebar.grid_propagate(False)

        logo_ring = ctk.CTkFrame(self.sidebar, width=56, height=56, corner_radius=28,
                                  fg_color="#0e1f38", border_width=2, border_color=NEON_BLUE)
        logo_ring.pack(pady=(28, 8))
        logo_ring.pack_propagate(False)
        ctk.CTkLabel(logo_ring, text="P", font=("Segoe UI", 22, "bold"), text_color=NEON_BLUE) \
            .place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.sidebar, text="Smart Parking", font=("Segoe UI", 14, "bold"),
                      text_color=TEXT_PRIMARY).pack(pady=(0, 2))
        ctk.CTkLabel(self.sidebar, text="ADMIN PANEL", font=("Segoe UI", 10),
                      text_color=TEXT_SECONDARY).pack(pady=(0, 24))

        nav_items = [
            ("📊", "Dashboard", True, self.show_dashboard),
            ("🅿️", "Parking Map", False, lambda: print("Parking Map")),
            ("🚗", "Vehicles", False, lambda: print("Vehicles")),
            ("⏳", "Waiting Queue", False, lambda: print("Waiting Queue")),
            ("👥", "Subscribers", False, lambda: print("Subscribers")),
        ]
        self.nav_buttons = []
        for icon, text, active, cmd in nav_items:
            b = NavButton(self.sidebar, icon, text, command=cmd, active=active)
            b.pack(fill="x", padx=16, pady=4)
            self.nav_buttons.append(b)

        # spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(expand=True, fill="both")

        self.admin_badge = ctk.CTkFrame(self.sidebar, fg_color="#0e1f38", corner_radius=14,
                                         border_width=1.5, border_color=NEON_BLUE)
        self.admin_badge.pack(fill="x", padx=16, pady=18)
        ctk.CTkLabel(self.admin_badge, text="🛡️  Asmaa", font=("Segoe UI", 12, "bold"),
                      text_color=TEXT_PRIMARY).pack(pady=(10, 0), padx=12, anchor="w")
        ctk.CTkLabel(self.admin_badge, text="ADM001 • Online", font=("Segoe UI", 10),
                      text_color=NEON_GREEN).pack(pady=(0, 10), padx=12, anchor="w")

        self.logout_btn = ctk.CTkButton(
            self.sidebar, text="⎋  Logout", height=40, corner_radius=12,
            fg_color="transparent", hover_color="#3a1f25",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self.logout
        )
        self.logout_btn.pack(fill="x", padx=16, pady=(0, 22))
        self.logout_btn.bind("<Enter>", lambda e: self.logout_btn.configure(
            text_color="#ff6b6b", border_color="#ff6b6b"))
        self.logout_btn.bind("<Leave>", lambda e: self.logout_btn.configure(
            text_color=TEXT_SECONDARY, border_color=PANEL_BORDER))

        # ===================== MAIN CONTENT =====================
        self.main = ctk.CTkFrame(self.container, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nswe")
        self.main.grid_rowconfigure(2, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        # ---- header ----
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ctk.CTkLabel(header, text="Dashboard Overview", font=("Segoe UI", 24, "bold"),
                      text_color=TEXT_PRIMARY).pack(side="left")

        self.live_pill = ctk.CTkLabel(
            header, text="●  Live", font=("Segoe UI", 11, "bold"), text_color=NEON_GREEN,
            fg_color="#0e1c33", corner_radius=20, padx=14, pady=6
        )
        self.live_pill.pack(side="right")

        # ---- stat cards row ----
        stats_row = ctk.CTkFrame(self.main, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 18))
        for i in range(4):
            stats_row.grid_columnconfigure(i, weight=1, uniform="stat")

        self.total_card = StatCard(stats_row, "🅿️", "20", "Total Slots", NEON_BLUE)
        self.total_card.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.occupied_card = StatCard(stats_row, "🚗", "12", "Occupied", "#ff8a8a")
        self.occupied_card.grid(row=0, column=1, sticky="ew", padx=12)

        self.available_card = StatCard(stats_row, "✅", "8", "Available", NEON_GREEN)
        self.available_card.grid(row=0, column=2, sticky="ew", padx=12)

        self.queue_card = StatCard(stats_row, "⏳", "3", "Waiting Queue", "#ffd166")
        self.queue_card.grid(row=0, column=3, sticky="ew", padx=(12, 0))

        # ---- lower section: parking map + side panel ----
        lower = ctk.CTkFrame(self.main, fg_color="transparent")
        lower.grid(row=2, column=0, sticky="nswe")
        lower.grid_columnconfigure(0, weight=3)
        lower.grid_columnconfigure(1, weight=2)
        lower.grid_rowconfigure(0, weight=1)

        # parking map panel
        map_panel = GlassFrame(lower, accent=NEON_BLUE)
        map_panel.grid(row=0, column=0, sticky="nswe", padx=(0, 18))

        map_header = ctk.CTkFrame(map_panel, fg_color="transparent")
        map_header.pack(fill="x", padx=22, pady=(20, 4))
        ctk.CTkLabel(map_header, text="Live Parking Map", font=("Segoe UI", 16, "bold"),
                      text_color=TEXT_PRIMARY).pack(side="left")

        legend = ctk.CTkFrame(map_header, fg_color="transparent")
        legend.pack(side="right")
        self._legend_dot(legend, NEON_GREEN, "Available")
        self._legend_dot(legend, "#ff6b6b", "Occupied")

        self.grid_frame = ctk.CTkFrame(map_panel, fg_color="transparent")
        self.grid_frame.pack(padx=22, pady=(14, 22), fill="both", expand=True)

        self._build_parking_grid()

        # right side panel: waiting queue + recent activity
        side_panel = ctk.CTkFrame(lower, fg_color="transparent")
        side_panel.grid(row=0, column=1, sticky="nswe")
        side_panel.grid_rowconfigure(0, weight=1)
        side_panel.grid_rowconfigure(1, weight=1)
        side_panel.grid_columnconfigure(0, weight=1)

        queue_panel = GlassFrame(side_panel, accent=NEON_GREEN)
        queue_panel.grid(row=0, column=0, sticky="nswe", pady=(0, 18))
        ctk.CTkLabel(queue_panel, text="⏳ Waiting Queue", font=("Segoe UI", 15, "bold"),
                      text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(18, 10))

        queue_items = ["ABC-123  •  Regular", "XYZ-789  •  Subscriber (SUB1002)", "QWE-456  •  Regular"]
        for item in queue_items:
            row = ctk.CTkFrame(queue_panel, fg_color="#0e1f38", corner_radius=10)
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(row, text=item, font=("Segoe UI", 12), text_color=TEXT_PRIMARY) \
                .pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text="●", text_color="#ffd166", font=("Segoe UI", 12)) \
                .pack(side="right", padx=12)

        activity_panel = GlassFrame(side_panel, accent=NEON_BLUE)
        activity_panel.grid(row=1, column=0, sticky="nswe")
        ctk.CTkLabel(activity_panel, text="📋 Recent Activity", font=("Segoe UI", 15, "bold"),
                      text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(18, 10))

        activities = [
            ("✅", "Vehicle ABC-123 parked at A2", NEON_GREEN),
            ("🚪", "SUB1001 exited — 0 EGP (subscription)", NEON_BLUE),
            ("🚪", "Vehicle GHI-321 exited — 45 EGP", "#ffd166"),
            ("➕", "New subscriber added: SUB1003", NEON_GREEN),
        ]
        for icon, text, color in activities:
            row = ctk.CTkFrame(activity_panel, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(row, text=icon, font=("Segoe UI Emoji", 13), text_color=color) \
                .pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=text, font=("Segoe UI", 11.5), text_color=TEXT_SECONDARY,
                          wraplength=260, justify="left").pack(side="left")

        # ---------- entrance animation ----------
        self.attributes("-alpha", 0.0)
        self._alpha = 0.0
        self.after(50, self._fade_in)

        self._pulse_up = True
        self.after(300, self._pulse_live)

    # ---------- helpers ----------
    def _legend_dot(self, master, color, text):
        f = ctk.CTkFrame(master, fg_color="transparent")
        f.pack(side="left", padx=8)
        ctk.CTkLabel(f, text="●", text_color=color, font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(f, text=text, text_color=TEXT_SECONDARY, font=("Segoe UI", 11)).pack(side="left", padx=(4, 0))

    def _build_parking_grid(self):
        # demo layout: 5 columns x 4 rows of slots
        occupied_slots = {"A1", "A3", "A4", "B1", "B2", "B4", "C2", "C3", "C5", "D1", "D3", "D5"}
        plates = {
            "A1": "ABC-123", "A3": "XYZ-789", "A4": "LMN-456", "B1": "QWE-111",
            "B2": "TYU-222", "B4": "ASD-333", "C2": "ZXC-444", "C3": "POI-555",
            "C5": "VBN-666", "D1": "MKL-777", "D3": "JHG-888", "D5": "FDS-999",
        }
        rows = ["A", "B", "C", "D"]
        for r, row_letter in enumerate(rows):
            for c in range(5):
                slot_id = f"{row_letter}{c+1}"
                occupied = slot_id in occupied_slots
                tile = SlotTile(self.grid_frame, slot_id, occupied=occupied, plate=plates.get(slot_id, ""))
                tile.grid(row=r, column=c, padx=6, pady=6)

    # ---------- background ----------
    def _resize_bg(self, event):
        if event.widget is not self or self._bg_pil is None:
            return
        w, h = max(event.width, 1), max(event.height, 1)

    # ---------- animations ----------
    def _fade_in(self):
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._alpha < 1.0:
            self.after(16, self._fade_in)

    def _pulse_live(self):
        if self._pulse_up:
            self.live_pill.configure(text_color=NEON_BLUE)
        else:
            self.live_pill.configure(text_color=NEON_GREEN)
        self._pulse_up = not self._pulse_up
        self.after(800, self._pulse_live)

    # ---------- nav actions ----------
    def show_dashboard(self):
        print("Already on dashboard")

    def logout(self):
        print("Logout -> back to Start Screen")
        # self.destroy(); open start_screen()


if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()