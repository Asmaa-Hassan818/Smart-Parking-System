import tkinter as tk
import customtkinter as ctk
import math
import random

from admin_dashboard import AdminDashboard, Admin, _build_demo_backend

ctk.set_appearance_mode("dark")

BG_COLOR       = "#0b0f1a"
PANEL_COLOR    = "#121829"
PANEL_BORDER   = "#1f2a44"
NEON_BLUE      = "#3ad6ff"
NEON_GREEN     = "#39ffb0"
TEXT_PRIMARY   = "#eaf2ff"
TEXT_SECONDARY = "#7d90b3"
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
        for _ in range(45):
            x = random.uniform(0, w); y = random.uniform(0, h)
            r = random.uniform(1.5, 3.5); speed = random.uniform(0.3, 1.0)
            color = random.choice([NEON_BLUE, NEON_GREEN])
            item = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            self.particles.append({"id": item, "speed": speed,
                                    "phase": random.uniform(0, math.tau)})

    def _animate(self):
        try:
            h = self.winfo_height()
            for p in self.particles:
                p["phase"] += 0.03
                self.move(p["id"], math.sin(p["phase"]) * 0.4, -p["speed"])
                coords = self.coords(p["id"])
                if coords and coords[1] < -5:
                    self.move(p["id"], 0, h + 10)
            self.after(40, self._animate)
        except tk.TclError:
            pass

class GlowButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _=None):
        self.configure(border_width=2, border_color=NEON_BLUE)

    def _on_leave(self, _=None):
        self.configure(border_width=0)


class AdminLoginScreen(ctk.CTk):

    def __init__(self, shared_backend=None):
        super().__init__()
        self._shared_backend = shared_backend
        self._running = True

        self.title("Smart Parking System — Admin Login")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_COLOR)

        self.particles = ParticleOverlay(self, bg=BG_COLOR)
        self.particles.place(x=0, y=0, relwidth=1, relheight=1)

        self.panel = ctk.CTkFrame(
            self, width=440, height=490, corner_radius=24,
            fg_color=PANEL_COLOR, border_width=2, border_color=PANEL_BORDER)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")
        self.panel.pack_propagate(False)

        self.icon_ring = ctk.CTkFrame(
            self.panel, width=90, height=90, corner_radius=45,
            fg_color="#0e1f38", border_width=2, border_color=NEON_BLUE)
        self.icon_ring.pack(pady=(46, 14))
        self.icon_ring.pack_propagate(False)
        ctk.CTkLabel(self.icon_ring, text="🛡️",
                      font=("Segoe UI Emoji", 36)).place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(self.panel, text="Admin Login",
                      font=("Segoe UI", 26, "bold"),
                      text_color=TEXT_PRIMARY).pack(pady=(0, 4))
        ctk.CTkLabel(self.panel,
                      text="Access the Smart Parking Management Dashboard",
                      font=("Segoe UI", 12),
                      text_color=TEXT_SECONDARY).pack(pady=(0, 26))

        self.id_entry = ctk.CTkEntry(
            self.panel, width=320, height=46, corner_radius=12,
            placeholder_text="Admin ID  (e.g. ADM001)",
            fg_color="#0c1426", border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_SECONDARY,
            font=("Segoe UI", 13))
        self.id_entry.pack(pady=(0, 6))
        self.id_entry.bind("<FocusIn>",  self._entry_focus_in)
        self.id_entry.bind("<FocusOut>", self._entry_focus_out)
        self.id_entry.bind("<Return>",   lambda e: self._handle_login())

        self.msg_label = ctk.CTkLabel(
            self.panel, text="", font=("Segoe UI", 11.5),
            text_color=DANGER_COLOR, wraplength=310)
        self.msg_label.pack(pady=(2, 8))

        self.login_btn = GlowButton(
            self.panel, text="Login →", width=320, height=46, corner_radius=12,
            fg_color=NEON_BLUE, hover_color="#5fe3ff",
            text_color="#06141f", font=("Segoe UI", 14, "bold"),
            command=self._handle_login)
        self.login_btn.pack(pady=(0, 10))

        self.back_btn = ctk.CTkButton(
            self.panel, text="← Back", width=320, height=42, corner_radius=12,
            fg_color="transparent", hover_color="#1b2740",
            border_width=1.5, border_color=PANEL_BORDER,
            text_color=TEXT_SECONDARY, font=("Segoe UI", 12.5),
            command=self._go_back)
        self.back_btn.pack(pady=(0, 0))
        self.back_btn.bind("<Enter>", lambda e: self.back_btn.configure(
            text_color=TEXT_PRIMARY, border_color=NEON_GREEN))
        self.back_btn.bind("<Leave>", lambda e: self.back_btn.configure(
            text_color=TEXT_SECONDARY, border_color=PANEL_BORDER))
        ctk.CTkLabel(
            self.panel,
            text="Demo IDs: ADM001 · ADM002 · ADM003",
            font=("Segoe UI", 10), text_color=TEXT_SECONDARY
        ).pack(pady=(16, 0))

        ctk.CTkLabel(
            self, text="SMART PARKING SYSTEM  ©  2026",
            font=("Segoe UI", 11), text_color=TEXT_SECONDARY
        ).place(relx=0.5, rely=0.97, anchor="center")

        self.attributes("-alpha", 0.0)
        self._alpha        = 0.0
        self._slide_offset = 40
        self.after(50, self._animate_entrance)

        self._glow_up = True
        self.after(200, self._pulse_icon_ring)

    def _entry_focus_in(self, _=None):
        self.id_entry.configure(border_color=NEON_BLUE, border_width=2)

    def _entry_focus_out(self, _=None):
        self.id_entry.configure(border_color=PANEL_BORDER, border_width=1.5)

    def _animate_entrance(self):
        if not self._running:
            return
        self._alpha = min(1.0, self._alpha + 0.06)
        self.attributes("-alpha", self._alpha)
        if self._slide_offset > 0:
            self._slide_offset = max(0, self._slide_offset - 3)
            self.panel.place(relx=0.5, rely=0.5, anchor="center",
                              y=self._slide_offset)
        if self._alpha < 1.0 or self._slide_offset > 0:
            self.after(16, self._animate_entrance)

    def _pulse_icon_ring(self):
        if not self._running:
            return
        self.icon_ring.configure(
            border_color=NEON_GREEN if self._glow_up else NEON_BLUE)
        self._glow_up = not self._glow_up
        self.after(900, self._pulse_icon_ring)

    def _handle_login(self):
        admin_id = self.id_entry.get().strip().upper()

        if not admin_id:
            self._set_msg("Please enter your Admin ID.", DANGER_COLOR)
            self.id_entry.configure(border_color=DANGER_COLOR, border_width=2)
            return

        if admin_id not in Admin.VALID_ADMINS:
            self._set_msg("Invalid Admin ID. Please try again.", DANGER_COLOR)
            self.id_entry.configure(border_color=DANGER_COLOR, border_width=2)
            self.id_entry.delete(0, "end")
            return

        name = Admin.VALID_ADMINS[admin_id]
        self._set_msg(f"Welcome, {name}! Opening dashboard…", NEON_GREEN)
        self.login_btn.configure(state="disabled", text="Please wait…")
        self.after(600, lambda: self._open_dashboard(admin_id, name))

    def _open_dashboard(self, admin_id: str, name: str):
        if self._shared_backend is not None:
            sub_mgr, lot = self._shared_backend
        else:
            demo_admin = _build_demo_backend()
            sub_mgr = demo_admin.subscriber_manager
            lot     = demo_admin.parking_lot

        admin = Admin(admin_id, name, sub_mgr, lot)

        self._running = False
        self.destroy()

        dashboard = AdminDashboard(admin)
        dashboard.mainloop()

    def _go_back(self):
        self._running = False
        self.destroy()
    def _set_msg(self, text: str, color: str):
        self.msg_label.configure(text=text, text_color=color)



if __name__ == "__main__":
    app = AdminLoginScreen()
    app.mainloop()